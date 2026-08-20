import os

import pytest

from agent.tools import (
    get_order_record,
    get_billing_status,
    get_provisioning_log,
    get_inventory_status,
    search_knowledge_base,
)

# real_mock_services (starts the 4 mock services as real uvicorn servers)
# lives in tests/conftest.py, session-scoped and autouse -- shared with
# test_specialists.py, which needs the same real services for its own
# full-stack test.


async def test_get_order_record():
    result = await get_order_record.ainvoke({"order_id": "ORD-88213"})
    assert result.success is True
    assert result.data["customer_id"] == "CUST-001"
    assert result.error is None


async def test_get_order_record_not_found():
    # 404 is a confirmed absence, not a failure -- success stays True with
    # no data (agent/tools.py's _fetch_json), never retried.
    result = await get_order_record.ainvoke({"order_id": "ORD-DOES-NOT-EXIST"})
    assert result.success is True
    assert result.data is None


async def test_get_billing_status():
    result = await get_billing_status.ainvoke({"customer_id": "CUST-001"})
    assert result.success is True
    assert result.data["payment_status"] == "authorized"


async def test_get_provisioning_log():
    result = await get_provisioning_log.ainvoke({"order_id": "ORD-88213"})
    assert result.success is True
    assert result.data["error_code"] == "ERR_4471"


async def test_get_inventory_status_by_address_not_found():
    # Reproduces the worked example: no circuit assigned for this address
    # -- itself the root-cause signal (02-ARCHITECTURE.md Section 1), so
    # success=True, data=None, not an error.
    result = await get_inventory_status.ainvoke(
        {"address": "100 Main St, Springfield"}
    )
    assert result.success is True
    assert result.data is None


async def test_get_inventory_status_by_circuit_id():
    result = await get_inventory_status.ainvoke({"circuit_id": "C-600"})
    assert result.success is True
    assert result.data["status"] == "assigned"


async def test_get_inventory_status_requires_a_lookup_key():
    result = await get_inventory_status.ainvoke({})
    assert result.success is False
    assert "circuit_id or address" in result.error


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"), reason="requires a real OPENAI_API_KEY"
)
async def test_search_knowledge_base():
    result = await search_knowledge_base.ainvoke({"query": "what does ERR_4471 mean?"})
    assert result.success is True
    sources = {r["source"] for r in result.data["results"]}
    assert "err-4471" in sources


async def test_search_knowledge_base_degrades_without_api_key(monkeypatch):
    # Section 3.6's "unavailable" contract applies here too -- a missing
    # key must be reported explicitly, never silently treated as "no
    # results found."
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = await search_knowledge_base.ainvoke({"query": "anything"})
    assert result.success is False
    assert result.error == "unavailable: OPENAI_API_KEY not configured"


async def test_retry_then_unavailable(monkeypatch):
    # Section 3.6: one retry, then an explicit "unavailable" result --
    # never a silently dropped/empty evidence entry.
    monkeypatch.setenv("MOCK_FAILURE_RATE", "1.0")
    try:
        result = await get_order_record.ainvoke({"order_id": "ORD-88213"})
    finally:
        monkeypatch.setenv("MOCK_FAILURE_RATE", "0")
    assert result.success is False
    assert result.error.startswith("unavailable:")
