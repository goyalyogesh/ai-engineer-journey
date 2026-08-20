from .db import get_connection

# One record per 03-EVALUATION.md archetype (04-BUILD-PLAN.md Phase 1's seed
# table) -- customer_id/order_id here must line up with the matching seed
# records in billing/provisioning/inventory. Phase 6 adds 2 more variants
# per archetype below (ORD-90010+) to reach the golden dataset's 20-25
# scenario target -- same 7 archetypes, different concrete instances.
ORDERS = [
    # order_id,   customer_id, service_type,     address,                          status,    created_at
    ("ORD-88213", "CUST-001", "fiber_internet", "100 Main St, Springfield",        "created", "2026-01-15T09:00:00Z"),  # known error code
    ("ORD-90001", "CUST-002", "fiber_internet", "200 Oak Ave, Springfield",        "created", "2026-01-16T09:00:00Z"),  # unknown error code
    ("ORD-90002", "CUST-003", "fiber_internet", "300 Elm St, Springfield",         "created", "2026-01-17T09:00:00Z"),  # billing hold only
    ("ORD-90003", "CUST-004", "fiber_internet", "400 Pine Rd, Springfield",        "created", "2026-01-18T09:00:00Z"),  # inventory/address mismatch
    ("ORD-90004", "CUST-005", "fiber_internet", "500 Cedar Ln, Springfield",       "created", "2026-01-19T09:00:00Z"),  # multiple causes
    ("ORD-90005", "CUST-006", "fiber_internet", "600 Birch Dr, Springfield",       "created", "2026-01-20T09:00:00Z"),  # clean order
    ("ORD-90006", "CUST-007", "fiber_internet", "700 Walnut Ct, Springfield",      "created", "2026-01-21T09:00:00Z"),  # conflicting evidence

    # --- Phase 6: 2 more variants per archetype ---
    ("ORD-90010", "CUST-010", "fiber_internet", "800 Maple Ave, Springfield",      "created", "2026-01-22T09:00:00Z"),  # known error code #2
    ("ORD-90011", "CUST-011", "fiber_internet", "900 Chestnut St, Springfield",    "created", "2026-01-23T09:00:00Z"),  # known error code #3
    ("ORD-90012", "CUST-012", "fiber_internet", "1000 Poplar Ave, Springfield",    "created", "2026-01-24T09:00:00Z"),  # unknown error code #2
    ("ORD-90013", "CUST-013", "fiber_internet", "1100 Willow Rd, Springfield",     "created", "2026-01-25T09:00:00Z"),  # unknown error code #3
    ("ORD-90014", "CUST-014", "fiber_internet", "1200 Ash Ln, Springfield",        "created", "2026-01-26T09:00:00Z"),  # billing hold only #2
    ("ORD-90015", "CUST-015", "fiber_internet", "1300 Spruce Ct, Springfield",     "created", "2026-01-27T09:00:00Z"),  # billing hold only #3
    ("ORD-90016", "CUST-016", "fiber_internet", "1400 Fir Dr, Springfield",        "created", "2026-01-28T09:00:00Z"),  # inventory/address mismatch #2
    ("ORD-90017", "CUST-017", "fiber_internet", "1500 Cypress Way, Springfield",   "created", "2026-01-29T09:00:00Z"),  # inventory/address mismatch #3
    ("ORD-90018", "CUST-018", "fiber_internet", "1600 Redwood Blvd, Springfield",  "created", "2026-01-30T09:00:00Z"),  # multiple causes #2
    ("ORD-90019", "CUST-019", "fiber_internet", "1700 Sequoia St, Springfield",    "created", "2026-01-31T09:00:00Z"),  # multiple causes #3
    ("ORD-90020", "CUST-020", "fiber_internet", "1800 Magnolia Dr, Springfield",   "created", "2026-02-01T09:00:00Z"),  # clean order #2
    ("ORD-90021", "CUST-021", "fiber_internet", "1900 Dogwood Ln, Springfield",    "created", "2026-02-02T09:00:00Z"),  # clean order #3
    ("ORD-90022", "CUST-022", "fiber_internet", "2000 Hickory Ave, Springfield",   "created", "2026-02-03T09:00:00Z"),  # conflicting evidence #2
    ("ORD-90023", "CUST-023", "fiber_internet", "2100 Sycamore Rd, Springfield",   "created", "2026-02-04T09:00:00Z"),  # conflicting evidence #3
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
