"""The 5 @tool functions + ToolResult (02-ARCHITECTURE.md Section 3.3).

Every tool talks to its backing service **only over HTTP** (mock CRM /
Billing / Provisioning / Inventory) or Chroma (search_knowledge_base) --
never a direct Python import into a mock service's internals. That
boundary is what makes the "5th backend system = 1 new tool, no agent
redesign" extensibility claim (01-REQUIREMENTS.md NFR table) actually
true, not just aspirational (Section 3.3).
"""
import asyncio
import os
import re
import time

import httpx
from dotenv import load_dotenv
from langchain_core.tools import tool
from pydantic import BaseModel

from agent.observability import log_event

load_dotenv()  # this module reads *_SERVICE_URL / OPENAI_API_KEY directly
# from os.environ (below) -- it must not depend on some other module
# (e.g. a mock service's own main.py) having already called load_dotenv()
# as a side effect of import order.


class ToolResult(BaseModel):
    tool_name: str
    success: bool
    data: dict | None
    error: str | None  # populated on failure, incl. "unavailable" (Section 3.6)
    latency_ms: float


async def _fetch_json(tool_name: str, url: str, params: dict | None = None) -> ToolResult:
    start = time.monotonic()
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(url, params=params)
        if response.status_code == 404:
            # A confirmed absence is itself diagnostic evidence here, not an
            # error -- e.g. Inventory returning 404 for ORD-88213's address
            # *is* the root-cause signal in the worked example
            # (02-ARCHITECTURE.md Section 1), not a failed call. So this is
            # a successful call that found no record, never retried.
            return ToolResult(
                tool_name=tool_name, success=True, data=None, error=None,
                latency_ms=(time.monotonic() - start) * 1000,
            )
        response.raise_for_status()
        data = response.json()
    return ToolResult(
        tool_name=tool_name, success=True, data=data, error=None,
        latency_ms=(time.monotonic() - start) * 1000,
    )


async def call_with_retry(fn, *args, retries: int = 1, **kwargs) -> ToolResult:
    # Section 3.6: exactly one retry with a short fixed backoff -- not a
    # full circuit-breaker/exponential-backoff policy, which would be out
    # of proportion for this project's actual point. If the retry also
    # fails, the failure is recorded explicitly as "unavailable" rather
    # than silently dropped -- a system being unreachable is itself
    # diagnostic information (FR6 insufficient_evidence).
    for attempt in range(retries + 1):
        try:
            result = await fn(*args, **kwargs)
            # Phase 5's "structured JSON log line per tool call"
            # requirement (02-ARCHITECTURE.md Section 12's Core-tier
            # logging) -- logged here, the one place every tool call
            # (success or handled failure) actually returns.
            log_event(
                "tool_call", tool_name=result.tool_name, success=result.success,
                latency_ms=result.latency_ms, error=result.error, attempt=attempt,
            )
            return result
        except (httpx.HTTPError, httpx.TimeoutException) as e:
            if attempt == retries:
                tool_name = args[0] if args else kwargs.get("tool_name", fn.__name__)
                result = ToolResult(
                    tool_name=tool_name, success=False, data=None,
                    error=f"unavailable: {e}", latency_ms=0,
                )
                log_event(
                    "tool_call", tool_name=result.tool_name, success=False,
                    latency_ms=0, error=result.error, attempt=attempt,
                )
                return result
            await asyncio.sleep(0.2)  # short fixed backoff (Section 3.6)


@tool
async def get_order_record(order_id: str) -> ToolResult:
    """Look up a telecom order's CRM record (status, customer ID, service type, address) by order ID."""
    url = f"{os.environ['CRM_SERVICE_URL']}/orders/{order_id}"
    return await call_with_retry(_fetch_json, "get_order_record", url)


@tool
async def get_billing_status(customer_id: str) -> ToolResult:
    """Look up a customer's billing status (payment status, active holds, plan) by customer ID."""
    url = f"{os.environ['BILLING_SERVICE_URL']}/billing/{customer_id}"
    return await call_with_retry(_fetch_json, "get_billing_status", url)


@tool
async def get_provisioning_log(order_id: str) -> ToolResult:
    """Look up a telecom order's provisioning status and any error code, by order ID."""
    url = f"{os.environ['PROVISIONING_SERVICE_URL']}/provisioning/{order_id}"
    return await call_with_retry(_fetch_json, "get_provisioning_log", url)


@tool
async def get_inventory_status(circuit_id: str | None = None, address: str | None = None) -> ToolResult:
    """Look up network inventory / circuit assignment status, by circuit ID or service address."""
    if circuit_id is None and address is None:
        # A caller (planner) error, not a backend failure -- never sent
        # over HTTP, so it can't be an "unavailable" result either.
        return ToolResult(
            tool_name="get_inventory_status", success=False, data=None,
            error="must provide circuit_id or address", latency_ms=0,
        )
    params = {k: v for k, v in {"circuit_id": circuit_id, "address": address}.items() if v is not None}
    url = f"{os.environ['INVENTORY_SERVICE_URL']}/inventory"
    return await call_with_retry(_fetch_json, "get_inventory_status", url, params=params)


# --- search_knowledge_base: Chroma vector search only this phase --------
# Neo4j/GraphRAG merge is Phase 8 (Extended) -- 04-BUILD-PLAN.md Phase 8,
# 02-ARCHITECTURE.md Section 5.2. Kept in this file (not a separate
# module) per the repo structure in 04-BUILD-PLAN.md, which places the KB
# tool alongside the other 4 in tools.py.

# Seed documents cover the error codes actually seeded in
# mock_services/provisioning/seed_data.py -- ERR_9999 is deliberately
# absent (that seed record exists specifically to exercise the
# "insufficient_evidence" path when the KB has no answer).
_KB_DOCUMENTS = [
    {
        "id": "err-4471",
        "text": (
            "ERR_4471: provisioning failed because no circuit is assigned "
            "in network inventory for the service address. This is a "
            "network/infrastructure-side cause, not a billing or CRM "
            "issue -- resolving it requires assigning a circuit to the "
            "address in inventory before provisioning can be retried."
        ),
    },
    {
        "id": "err-bill-mismatch",
        "text": (
            "ERR_BILL_MISMATCH: provisioning reports a billing-related "
            "hold blocking the order, but this code is emitted by the "
            "provisioning system itself, not billing. It should be "
            "cross-checked against the billing system's own hold_active "
            "status before being trusted at face value -- the two "
            "systems can disagree."
        ),
    },
    {
        "id": "billing-hold-not-started",
        "text": (
            "When a customer's billing status shows an active hold "
            "(hold_active=true, e.g. for a declined or pending payment), "
            "provisioning will not start at all -- the provisioning log "
            "will show status 'not_started' with no error_code, because "
            "the order never reached the provisioning system."
        ),
    },
    {
        "id": "inventory-address-mismatch",
        "text": (
            "A circuit_id can be marked 'succeeded' in provisioning while "
            "inventory records it under a different address than the "
            "order's CRM address -- this is an inventory data-quality "
            "issue (an address mismatch), not a provisioning failure, and "
            "shows up as provisioning succeeding but the order still not "
            "working at the customer's address."
        ),
    },
]

_vectorstore = None  # lazy singleton -- built once per process, on first use


def _get_vectorstore():
    global _vectorstore
    if _vectorstore is not None:
        return _vectorstore

    from langchain_chroma import Chroma
    from langchain_core.documents import Document
    from langchain_openai import OpenAIEmbeddings

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    store = Chroma(
        collection_name="order_diagnosis_kb",
        embedding_function=embeddings,
        persist_directory=os.environ["CHROMA_PATH"],
    )
    # Only seed once -- Chroma persists to disk, so re-running the process
    # shouldn't re-embed (cost) or duplicate entries on every startup.
    existing = store.get(ids=[d["id"] for d in _KB_DOCUMENTS])
    if len(existing["ids"]) < len(_KB_DOCUMENTS):
        store.add_documents(
            [Document(page_content=d["text"], metadata={"source": d["id"]}) for d in _KB_DOCUMENTS],
            ids=[d["id"] for d in _KB_DOCUMENTS],
        )
    _vectorstore = store
    return _vectorstore


# Vector search always returns its *closest* documents, even when nothing
# in the knowledge base actually explains the query (e.g. an error code
# the KB has never seen) -- there's no relevance floor by default. Found
# during real Phase 6 eval verification: this let the agent confidently
# reuse ERR_4471's explanation for the unrelated, unknown ERR_9999, since
# both queries scored similarly close to the same document (short,
# structurally similar technical codes don't embed far apart). A
# similarity-score threshold turned out too fragile to reliably separate
# "genuine match" from "coincidental closest neighbor" for terse codes
# like this -- so instead: error codes are exact, well-defined tokens, not
# natural-language concepts needing fuzzy matching, so a literal substring
# check is a deterministic, much more reliable relevance signal here than
# trusting embedding distance.
_ERROR_CODE_PATTERN = re.compile(r"ERR_[A-Z0-9_]+", re.IGNORECASE)


async def _search_kb(tool_name: str, query: str) -> ToolResult:
    start = time.monotonic()
    if not os.environ.get("OPENAI_API_KEY"):
        # Degrade explicitly, same "unavailable" contract as an
        # unreachable HTTP service (Section 3.6) -- never silently return
        # empty results as if the KB genuinely had nothing to say.
        return ToolResult(
            tool_name=tool_name, success=False, data=None,
            error="unavailable: OPENAI_API_KEY not configured", latency_ms=0,
        )
    store = _get_vectorstore()
    results = await asyncio.to_thread(store.similarity_search, query, k=3)

    query_codes = {m.upper() for m in _ERROR_CODE_PATTERN.findall(query)}
    exact_match_found = (
        any(any(code in doc.page_content.upper() for code in query_codes) for doc in results)
        if query_codes else None  # query wasn't about a specific error code -- not applicable
    )

    data = {
        "results": [
            {"content": doc.page_content, "source": doc.metadata.get("source")}
            for doc in results
        ],
        "exact_match_found": exact_match_found,
    }
    return ToolResult(
        tool_name=tool_name, success=True, data=data, error=None,
        latency_ms=(time.monotonic() - start) * 1000,
    )


@tool
async def search_knowledge_base(query: str) -> ToolResult:
    """Search the knowledge base for docs explaining telecom provisioning error codes and diagnostic facts, with citations."""
    return await call_with_retry(_search_kb, "search_knowledge_base", query)
