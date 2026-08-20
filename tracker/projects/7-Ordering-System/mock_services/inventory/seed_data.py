from .db import get_connection

# Most circuits here exist for orders whose provisioning actually produced
# a circuit_id (provisioning/seed_data.py's "succeeded" rows). Orders with
# no real circuit anywhere -- e.g. ORD-88213 -- deliberately have NO
# matching inventory record, which is what makes the "no circuit assigned
# for this address" worked-example result true by construction, not a
# special case to code around. The 3 "unknown error code" scenarios below
# are the deliberate exception: they DO have a genuine, correctly-
# addressed circuit, independent of their own provisioning attempt's
# outcome (inventory tracks what circuits exist, not what any one order's
# provisioning succeeded at) -- see the Phase 6 correction comment there.
RECORDS = [
    # circuit_id, address,                                status
    ("C-500", "999 Wrong Address Ave, Springfield", "assigned"),  # ORD-90003: address mismatch vs. CRM's "400 Pine Rd"
    ("C-600", "600 Birch Dr, Springfield",           "assigned"),  # ORD-90005: matches CRM's address exactly -- clean order

    # --- Phase 6: 2 more variants per archetype ---
    ("C-700", "9999 Mismatch Ave, Springfield",      "assigned"),  # ORD-90016: address mismatch vs. CRM's "1400 Fir Dr"
    ("C-701", "8888 Other Ave, Springfield",         "assigned"),  # ORD-90017: address mismatch vs. CRM's "1500 Cypress Way"
    ("C-702", "1800 Magnolia Dr, Springfield",       "assigned"),  # ORD-90020: matches CRM's address exactly -- clean order
    ("C-703", "1900 Dogwood Ln, Springfield",        "assigned"),  # ORD-90021: matches CRM's address exactly -- clean order

    # --- Phase 6 correction: the "unknown error code" archetype needs a
    # genuinely assigned, correctly-addressed circuit here -- inventory
    # tracks what circuits exist independent of any one order's
    # provisioning attempt, so a circuit can legitimately be assigned even
    # though ORD-90001/12/13's own provisioning failed with an
    # unrecognized code. Found during real Phase 6 eval verification: with
    # no inventory record here (matching the "known error code" pattern),
    # "no circuit assigned" was coincidentally TRUE for every failed
    # order regardless of error code -- letting the agent "explain" an
    # unknown error by citing an unrelated, technically-true-but-not-
    # actually-explanatory fact instead of admitting it doesn't know.
    ("C-800", "200 Oak Ave, Springfield",             "assigned"),  # ORD-90001: circuit exists, so "no circuit" is NOT the explanation
    ("C-801", "1000 Poplar Ave, Springfield",          "assigned"),  # ORD-90012: same
    ("C-802", "1100 Willow Rd, Springfield",           "assigned"),  # ORD-90013: same
]


def seed() -> None:
    conn = get_connection()
    conn.executemany(
        "INSERT OR REPLACE INTO inventory (circuit_id, address, status) VALUES (?, ?, ?)",
        RECORDS,
    )
    conn.commit()
    conn.close()
