from .db import get_connection

# order_id here must match crm/seed_data.py's ORDERS exactly. circuit_id is
# only populated when provisioning actually succeeded -- it's the field
# that "produces" the next join key for inventory (01-REQUIREMENTS.md
# Section 9), discovered progressively, not known up front.
RECORDS = [
    # order_id,   status,        error_code,          circuit_id, updated_at
    ("ORD-88213", "failed",      "ERR_4471",           None,       "2026-01-15T09:05:00Z"),  # known error code (worked example)
    ("ORD-90001", "failed",      "ERR_9999",           None,       "2026-01-16T09:05:00Z"),  # unknown error code -- deliberately absent from the KB (Phase 8)
    ("ORD-90002", "not_started", None,                 None,       "2026-01-17T09:05:00Z"),  # billing hold -- provisioning never even started
    ("ORD-90003", "succeeded",   None,                 "C-500",    "2026-01-18T09:05:00Z"),  # inventory/address mismatch -- circuit assigned, but see inventory seed
    ("ORD-90004", "failed",      "ERR_4471",           None,       "2026-01-19T09:05:00Z"),  # multiple causes -- co-occurs with a real billing hold
    ("ORD-90005", "succeeded",   None,                 "C-600",    "2026-01-20T09:05:00Z"),  # clean order
    ("ORD-90006", "failed",      "ERR_BILL_MISMATCH",  None,       "2026-01-21T09:05:00Z"),  # conflicting evidence -- error implies a billing cause despite billing showing clean

    # --- Phase 6: 2 more variants per archetype ---
    ("ORD-90010", "failed",      "ERR_4471",           None,       "2026-01-22T09:05:00Z"),  # known error code #2
    ("ORD-90011", "failed",      "ERR_4471",           None,       "2026-01-23T09:05:00Z"),  # known error code #3
    ("ORD-90012", "failed",      "ERR_8888",           None,       "2026-01-24T09:05:00Z"),  # unknown error code #2 -- also absent from the KB
    ("ORD-90013", "failed",      "ERR_7777",           None,       "2026-01-25T09:05:00Z"),  # unknown error code #3 -- also absent from the KB
    ("ORD-90014", "not_started", None,                 None,       "2026-01-26T09:05:00Z"),  # billing hold only #2
    ("ORD-90015", "not_started", None,                 None,       "2026-01-27T09:05:00Z"),  # billing hold only #3
    ("ORD-90016", "succeeded",   None,                 "C-700",    "2026-01-28T09:05:00Z"),  # inventory/address mismatch #2
    ("ORD-90017", "succeeded",   None,                 "C-701",    "2026-01-29T09:05:00Z"),  # inventory/address mismatch #3
    ("ORD-90018", "failed",      "ERR_4471",           None,       "2026-01-30T09:05:00Z"),  # multiple causes #2 -- co-occurs with a real billing hold
    ("ORD-90019", "failed",      "ERR_4471",           None,       "2026-01-31T09:05:00Z"),  # multiple causes #3 -- co-occurs with a real billing hold
    ("ORD-90020", "succeeded",   None,                 "C-702",    "2026-02-01T09:05:00Z"),  # clean order #2
    ("ORD-90021", "succeeded",   None,                 "C-703",    "2026-02-02T09:05:00Z"),  # clean order #3
    ("ORD-90022", "failed",      "ERR_BILL_MISMATCH",  None,       "2026-02-03T09:05:00Z"),  # conflicting evidence #2
    ("ORD-90023", "failed",      "ERR_BILL_MISMATCH",  None,       "2026-02-04T09:05:00Z"),  # conflicting evidence #3
]


def seed() -> None:
    conn = get_connection()
    conn.executemany(
        """
        INSERT OR REPLACE INTO provisioning_log
            (order_id, status, error_code, circuit_id, updated_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        RECORDS,
    )
    conn.commit()
    conn.close()
