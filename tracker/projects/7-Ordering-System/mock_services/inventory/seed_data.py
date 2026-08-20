from .db import get_connection

# Only 2 circuits actually exist -- matching the 2 archetypes that produced
# a circuit_id in provisioning/seed_data.py (ORD-90003, ORD-90005). Every
# other seeded order deliberately has NO matching inventory record, which
# is what makes the "no circuit assigned for this address" worked-example
# result (ORD-88213) true by construction, not a special case to code around.
RECORDS = [
    # circuit_id, address,                                status
    ("C-500", "999 Wrong Address Ave, Springfield", "assigned"),  # ORD-90003: address mismatch vs. CRM's "400 Pine Rd"
    ("C-600", "600 Birch Dr, Springfield",           "assigned"),  # ORD-90005: matches CRM's address exactly -- clean order
]


def seed() -> None:
    conn = get_connection()
    conn.executemany(
        "INSERT OR REPLACE INTO inventory (circuit_id, address, status) VALUES (?, ?, ?)",
        RECORDS,
    )
    conn.commit()
    conn.close()
