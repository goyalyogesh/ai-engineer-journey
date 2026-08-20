from .db import get_connection

# customer_id here must match crm/seed_data.py's ORDERS exactly -- this is
# the cross-system join FR2/01-REQUIREMENTS.md Section 9 describes: CRM
# gives you customer_id, only then can billing be queried.
RECORDS = [
    # customer_id, payment_status, hold_active, hold_reason,        plan
    ("CUST-001", "authorized", False, None,                 "fiber_500mb"),  # ORD-88213: clean billing
    ("CUST-002", "authorized", False, None,                 "fiber_500mb"),  # ORD-90001: clean billing
    ("CUST-003", "declined",   True,  "payment_declined",   "fiber_500mb"),  # ORD-90002: billing hold only
    ("CUST-004", "authorized", False, None,                 "fiber_500mb"),  # ORD-90003: clean billing
    ("CUST-005", "declined",   True,  "payment_declined",   "fiber_500mb"),  # ORD-90004: multiple causes
    ("CUST-006", "authorized", False, None,                 "fiber_500mb"),  # ORD-90005: clean order
    ("CUST-007", "authorized", False, None,                 "fiber_500mb"),  # ORD-90006: conflicting evidence -- billing itself looks clean

    # --- Phase 6: 2 more variants per archetype ---
    ("CUST-010", "authorized", False, None,                 "fiber_500mb"),  # ORD-90010: clean billing
    ("CUST-011", "authorized", False, None,                 "fiber_500mb"),  # ORD-90011: clean billing
    ("CUST-012", "authorized", False, None,                 "fiber_500mb"),  # ORD-90012: clean billing
    ("CUST-013", "authorized", False, None,                 "fiber_500mb"),  # ORD-90013: clean billing
    ("CUST-014", "declined",   True,  "payment_declined",   "fiber_500mb"),  # ORD-90014: billing hold only
    ("CUST-015", "declined",   True,  "payment_declined",   "fiber_500mb"),  # ORD-90015: billing hold only
    ("CUST-016", "authorized", False, None,                 "fiber_500mb"),  # ORD-90016: clean billing
    ("CUST-017", "authorized", False, None,                 "fiber_500mb"),  # ORD-90017: clean billing
    ("CUST-018", "declined",   True,  "payment_declined",   "fiber_500mb"),  # ORD-90018: multiple causes
    ("CUST-019", "declined",   True,  "payment_declined",   "fiber_500mb"),  # ORD-90019: multiple causes
    ("CUST-020", "authorized", False, None,                 "fiber_500mb"),  # ORD-90020: clean order
    ("CUST-021", "authorized", False, None,                 "fiber_500mb"),  # ORD-90021: clean order
    ("CUST-022", "authorized", False, None,                 "fiber_500mb"),  # ORD-90022: conflicting evidence -- billing looks clean
    ("CUST-023", "authorized", False, None,                 "fiber_500mb"),  # ORD-90023: conflicting evidence -- billing looks clean
]


def seed() -> None:
    conn = get_connection()
    conn.executemany(
        """
        INSERT OR REPLACE INTO billing_status
            (customer_id, payment_status, hold_active, hold_reason, plan)
        VALUES (?, ?, ?, ?, ?)
        """,
        RECORDS,
    )
    conn.commit()
    conn.close()
