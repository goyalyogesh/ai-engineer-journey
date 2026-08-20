from .db import get_connection

# One record per 03-EVALUATION.md archetype (04-BUILD-PLAN.md Phase 1's seed
# table) -- customer_id/order_id here must line up with the matching seed
# records in billing/provisioning/inventory. The full 20-25 scenario golden
# dataset (3-4 variants per archetype) is Phase 6's job, not this one.
ORDERS = [
    # order_id,   customer_id, service_type,     address,                          status,    created_at
    ("ORD-88213", "CUST-001", "fiber_internet", "100 Main St, Springfield",        "created", "2026-01-15T09:00:00Z"),  # known error code
    ("ORD-90001", "CUST-002", "fiber_internet", "200 Oak Ave, Springfield",        "created", "2026-01-16T09:00:00Z"),  # unknown error code
    ("ORD-90002", "CUST-003", "fiber_internet", "300 Elm St, Springfield",         "created", "2026-01-17T09:00:00Z"),  # billing hold only
    ("ORD-90003", "CUST-004", "fiber_internet", "400 Pine Rd, Springfield",        "created", "2026-01-18T09:00:00Z"),  # inventory/address mismatch
    ("ORD-90004", "CUST-005", "fiber_internet", "500 Cedar Ln, Springfield",       "created", "2026-01-19T09:00:00Z"),  # multiple causes
    ("ORD-90005", "CUST-006", "fiber_internet", "600 Birch Dr, Springfield",       "created", "2026-01-20T09:00:00Z"),  # clean order
    ("ORD-90006", "CUST-007", "fiber_internet", "700 Walnut Ct, Springfield",      "created", "2026-01-21T09:00:00Z"),  # conflicting evidence
]


def seed() -> None:
    conn = get_connection()
    conn.executemany(
        """
        INSERT OR REPLACE INTO orders
            (order_id, customer_id, service_type, address, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ORDERS,
    )
    conn.commit()
    conn.close()
