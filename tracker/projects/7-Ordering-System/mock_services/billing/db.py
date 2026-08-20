import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "billing.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS billing_status (
    customer_id TEXT PRIMARY KEY,
    payment_status TEXT NOT NULL,
    hold_active BOOLEAN NOT NULL,
    hold_reason TEXT,
    plan TEXT NOT NULL
);
"""


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()
