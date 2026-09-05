import os

import pytest

from agent.tools import _search_vector

# Vector search alone (Chroma only) -- no Neo4j connection needed at all,
# matching 02-ARCHITECTURE.md Section 13's isolation-then-integration
# pattern, now applied to Phase 8's 2 retrieval methods. The merged
# search_knowledge_base tool's own tests (which do need Neo4j, since the
# tool always runs both) live in tests/test_kb_merged.py.

pytestmark = pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"), reason="requires a real OPENAI_API_KEY"
)


async def test_vector_search_finds_err_4471():
    results = await _search_vector("what does ERR_4471 mean?")
    sources = {doc.metadata.get("source") for doc in results}
    assert "err-4471" in sources


async def test_vector_search_returns_up_to_k_results():
    results = await _search_vector("ERR_4471", k=2)
    assert len(results) <= 2


async def test_vector_search_still_returns_closest_match_for_unknown_code():
    # The whole reason exact_match_found (agent/tools.py) exists: vector
    # search has no relevance floor by default, so it returns *something*
    # even for a code the KB has never seen -- that's expected behavior at
    # this isolated layer, not a bug here. The "is this actually relevant"
    # judgment is exact_match_found's job, tested in test_kb_merged.py.
    results = await _search_vector("ERR_9999")
    assert len(results) > 0
