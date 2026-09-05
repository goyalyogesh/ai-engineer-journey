import os

import pytest

from agent.tools import search_knowledge_base

# search_knowledge_base's actual merge logic -- both vector and graph
# retrieval run for real here, verifying they land in the combined
# response correctly. This is the "only then" integration layer of
# 02-ARCHITECTURE.md Section 13's isolation-then-integration pattern;
# tests/test_kb_vector.py and tests/test_kb_graph.py cover each retrieval
# method alone.

pytestmark = pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"), reason="requires a real OPENAI_API_KEY"
)


async def test_search_knowledge_base_merges_vector_and_graph_for_known_code():
    result = await search_knowledge_base.ainvoke({"query": "ERR_4471"})
    assert result.success is True

    # Vector side
    sources = {r["source"] for r in result.data["results"]}
    assert "err-4471" in sources
    assert result.data["exact_match_found"] is True

    # Graph side -- present in the SAME response, not a separate call
    assert result.data["graph_match_found"] is True
    assert result.data["graph"]["cause"]
    assert result.data["graph"]["resolution"]
    assert "INC-4821" in result.data["graph"]["related_incidents"]


async def test_search_knowledge_base_no_match_for_unknown_error_code():
    # 05-DEVELOPMENT-LOG.md's Phase 6 finding, still true after Phase 8
    # adds a second retrieval method: an error code absent from BOTH the
    # KB and the graph must show neither signal as a match.
    result = await search_knowledge_base.ainvoke({"query": "ERR_9999"})
    assert result.success is True
    assert result.data["exact_match_found"] is False
    assert result.data["graph_match_found"] is False
    assert result.data["graph"] is None


async def test_search_knowledge_base_not_applicable_for_non_code_queries():
    result = await search_knowledge_base.ainvoke({"query": "why is provisioning slow"})
    assert result.success is True
    assert result.data["exact_match_found"] is None
    assert result.data["graph_match_found"] is None
    assert result.data["graph"] is None


async def test_search_knowledge_base_degrades_without_api_key(monkeypatch):
    # Section 3.6's "unavailable" contract applies here too -- a missing
    # key must be reported explicitly, never silently treated as "no
    # results found." Fails before either retrieval method even runs.
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = await search_knowledge_base.ainvoke({"query": "anything"})
    assert result.success is False
    assert result.error == "unavailable: OPENAI_API_KEY not configured"
