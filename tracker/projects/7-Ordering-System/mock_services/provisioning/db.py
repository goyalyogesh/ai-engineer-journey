import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "provisioning.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS provisioning_log (
    order_id TEXT PRIMARY KEY,
    status TEXT NOT NULL,
    error_code TEXT,
    circuit_id TEXT,
    updated_at TEXT NOT NULL
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
