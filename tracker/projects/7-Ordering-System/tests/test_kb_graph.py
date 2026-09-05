from agent.tools import _search_graph
from graph.neo4j_for_adk import graphdb

# Graph traversal alone (a direct Cypher query via graph/neo4j_for_adk.py)
# -- no vector search / OpenAI call involved at all, matching
# 02-ARCHITECTURE.md Section 13's isolation-then-integration pattern.
# Assumes the local Neo4j container is running and populated
# (`docker compose up -d neo4j && python -m graph.populate`), same
# precondition as the mock services being up for tests/test_tools.py.


async def test_graph_search_returns_err_4471_chain():
    result = await _search_graph("ERR_4471")
    assert result is not None
    assert "circuit" in result["cause"].lower()
    assert "circuit" in result["resolution"].lower()
    assert "INC-4821" in result["related_incidents"]
    assert "INC-5103" in result["related_incidents"]


async def test_graph_search_returns_err_bill_mismatch_chain():
    result = await _search_graph("ERR_BILL_MISMATCH")
    assert result is not None
    assert "billing" in result["cause"].lower()
    assert "INC-3390" in result["related_incidents"]


async def test_graph_search_returns_none_for_unknown_code():
    # ERR_9999 is deliberately absent from the graph, same as the Chroma
    # KB (05-DEVELOPMENT-LOG.md's Phase 6 finding) -- the FR6
    # insufficient-evidence scenarios depend on this staying true after
    # Phase 8 adds a second retrieval method.
    result = await _search_graph("ERR_9999")
    assert result is None


def test_worked_example_entity_graph_join():
    # 01-REQUIREMENTS.md Section 9's join problem, expressed as one Cypher
    # traversal instead of manually joining 4 REST responses -- the actual
    # point of the entity graph (02-ARCHITECTURE.md Section 5.1), verified
    # directly against the real graph (not through the agent at all).
    result = graphdb.send_query(
        """
        MATCH (cust:Customer)-[:PLACED]->(o:Order {order_id: $order_id})-[:HAS_STATUS]->(p:ProvisioningState)
        RETURN cust.customer_id AS customer_id, o.address AS address,
               p.status AS status, p.error_code AS error_code
        """,
        {"order_id": "ORD-88213"},
    )
    assert result["status"] == "success"
    record = result["records"][0]
    assert record["customer_id"] == "CUST-001"
    assert record["address"] == "100 Main St, Springfield"
    assert record["status"] == "failed"
    assert record["error_code"] == "ERR_4471"
