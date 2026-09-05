"""Loads Phase 1's mock-service seed data (entity graph, 02-ARCHITECTURE.md
Section 5.1) and the error-code knowledge graph (Section 5.2) into the real
Neo4j instance. Idempotent -- every write is a MERGE, so re-running this
after a code/data change never duplicates nodes, same "safe to re-run"
property as Phase 1's mock-service seed() functions.

Run with `python -m graph.populate` from the project root (venv active,
Neo4j reachable -- `docker compose up -d neo4j`).

Deliberately reuses mock_services/*/seed_data.py directly (not a second,
hand-maintained copy of the same 21 orders) -- the entity graph is meant to
describe the exact same data the mock services already serve over HTTP,
just structured for traversal instead of REST lookups.
"""
import os

from graph.neo4j_for_adk import graphdb
from mock_services.crm.seed_data import ORDERS as CRM_ORDERS
from mock_services.inventory.seed_data import RECORDS as INVENTORY_RECORDS
from mock_services.provisioning.seed_data import RECORDS as PROVISIONING_RECORDS

# The error-code knowledge graph (Section 5.2's worked example: ERR_4471
# --[CAUSED_BY]--> cause --[RESOLVED_BY]--> resolution, plus related
# incidents). Deliberately covers only the same 2 error codes the Chroma
# KB documents cover (agent/tools.py's _KB_DOCUMENTS) -- ERR_9999/8888/7777
# stay absent from BOTH retrieval methods on purpose, so the FR6
# insufficient-evidence scenarios (Phase 6) still hold after this phase
# merges vector + graph retrieval.
_ERROR_CODE_GRAPH = [
    {
        "code": "ERR_4471",
        "cause": (
            "No circuit is assigned in network inventory for the service "
            "address."
        ),
        "resolution": (
            "Assign a circuit to the address in inventory, then retry "
            "provisioning."
        ),
        "incidents": [
            {
                "ticket_id": "INC-4821",
                "description": (
                    "Missing circuit assignment at a residential address, "
                    "resolved by the inventory team, Jan 2026."
                ),
            },
            {
                "ticket_id": "INC-5103",
                "description": (
                    "Same root cause at a different address -- resolved "
                    "the same way."
                ),
            },
        ],
    },
    {
        "code": "ERR_BILL_MISMATCH",
        "cause": (
            "Provisioning flags a billing-related hold, but billing's own "
            "records show no active hold -- a cross-system data "
            "inconsistency, not a confirmed billing block."
        ),
        "resolution": (
            "Cross-check the billing system directly before acting; treat "
            "provisioning's claim as unconfirmed until verified."
        ),
        "incidents": [
            {
                "ticket_id": "INC-3390",
                "description": (
                    "Provisioning falsely flagged a billing hold that "
                    "billing had already cleared."
                ),
            },
        ],
    },
]


def apply_schema() -> None:
    schema_path = os.path.join(os.path.dirname(__file__), "schema.cypher")
    with open(schema_path) as f:
        content = f.read()
    # Strip comment lines *before* splitting on ';' -- an ordinary
    # semicolon used as English punctuation inside a `//` comment (not a
    # statement terminator) would otherwise be mistaken for one, silently
    # chopping the actual statement that follows it (caught during real
    # verification: see 05-DEVELOPMENT-LOG.md's Phase 8 entry).
    code_only = "\n".join(
        line for line in content.splitlines() if not line.strip().startswith("//")
    )
    for statement in code_only.split(";"):
        statement = statement.strip()
        if not statement:
            continue
        result = graphdb.send_query(statement)
        if result["status"] == "error":
            raise RuntimeError(f"Schema statement failed: {result['error_message']}\n{statement}")


def populate_entity_graph() -> None:
    customer_ids = {order[1] for order in CRM_ORDERS}
    for customer_id in customer_ids:
        graphdb.send_query(
            "MERGE (:Customer {customer_id: $customer_id})",
            {"customer_id": customer_id},
        )

    for order_id, customer_id, service_type, address, status, created_at in CRM_ORDERS:
        graphdb.send_query(
            """
            MATCH (c:Customer {customer_id: $customer_id})
            MERGE (o:Order {order_id: $order_id})
            SET o.service_type = $service_type, o.address = $address,
                o.status = $status, o.created_at = $created_at
            MERGE (c)-[:PLACED]->(o)
            """,
            {
                "order_id": order_id, "customer_id": customer_id,
                "service_type": service_type, "address": address,
                "status": status, "created_at": created_at,
            },
        )

    for order_id, status, error_code, circuit_id, updated_at in PROVISIONING_RECORDS:
        graphdb.send_query(
            """
            MATCH (o:Order {order_id: $order_id})
            MERGE (p:ProvisioningState {order_id: $order_id})
            SET p.status = $status, p.error_code = $error_code, p.updated_at = $updated_at
            MERGE (o)-[:HAS_STATUS]->(p)
            """,
            {
                "order_id": order_id, "status": status,
                "error_code": error_code, "updated_at": updated_at,
            },
        )
        if circuit_id:
            # circuit_id only exists once provisioning actually succeeded
            # (01-REQUIREMENTS.md Section 9) -- REQUIRES only makes sense
            # once that's known, not speculatively for every order.
            graphdb.send_query(
                """
                MATCH (o:Order {order_id: $order_id})
                MERGE (c:Circuit {circuit_id: $circuit_id})
                MERGE (o)-[:REQUIRES]->(c)
                """,
                {"order_id": order_id, "circuit_id": circuit_id},
            )

    for circuit_id, address, status in INVENTORY_RECORDS:
        # Inventory's own address for a circuit is the authoritative one
        # for ASSIGNED_TO -- it can legitimately differ from the order's
        # CRM address (that's literally the inventory/address-mismatch
        # archetype), so this must never be assumed to match.
        graphdb.send_query(
            """
            MERGE (c:Circuit {circuit_id: $circuit_id})
            SET c.status = $status
            MERGE (a:Address {full_address: $address})
            MERGE (c)-[:ASSIGNED_TO]->(a)
            """,
            {"circuit_id": circuit_id, "address": address, "status": status},
        )


def populate_error_code_graph() -> None:
    for entry in _ERROR_CODE_GRAPH:
        graphdb.send_query(
            """
            MERGE (e:ErrorCode {code: $code})
            MERGE (cause:Cause {description: $cause})
            MERGE (res:Resolution {description: $resolution})
            MERGE (e)-[:CAUSED_BY]->(cause)
            MERGE (cause)-[:RESOLVED_BY]->(res)
            """,
            {"code": entry["code"], "cause": entry["cause"], "resolution": entry["resolution"]},
        )
        for incident in entry["incidents"]:
            graphdb.send_query(
                """
                MATCH (e:ErrorCode {code: $code})
                MERGE (i:Incident {ticket_id: $ticket_id})
                SET i.description = $description
                MERGE (e)-[:RELATED_INCIDENT]->(i)
                """,
                {
                    "code": entry["code"], "ticket_id": incident["ticket_id"],
                    "description": incident["description"],
                },
            )


def populate() -> None:
    apply_schema()
    populate_entity_graph()
    populate_error_code_graph()


if __name__ == "__main__":
    populate()
    print("Graph populated.")
