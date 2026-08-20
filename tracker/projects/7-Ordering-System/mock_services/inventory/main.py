import os
import random
import asyncio
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from .db import get_connection, init_db
from .seed_data import seed
from .models import InventoryRecord

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed()
    yield


app = FastAPI(title="Mock Network Inventory Service", lifespan=lifespan)


async def simulate_latency_and_failure() -> None:
    # See mock_services/crm/main.py for why this is here and why it reads
    # env vars fresh per-request rather than caching at import time.
    failure_rate = float(os.environ.get("MOCK_FAILURE_RATE", 0.1))
    latency_min = int(os.environ.get("MOCK_LATENCY_MIN_MS", 200))
    latency_max = int(os.environ.get("MOCK_LATENCY_MAX_MS", 1500))
    await asyncio.sleep(random.uniform(latency_min, latency_max) / 1000)
    if random.random() < failure_rate:
        raise HTTPException(status_code=503, detail="transient failure")


@app.get("/inventory", response_model=InventoryRecord)
async def get_inventory(
    circuit_id: str | None = None, address: str | None = None
) -> InventoryRecord:
    await simulate_latency_and_failure()
    if not circuit_id and not address:
        raise HTTPException(
            status_code=400, detail="Provide circuit_id or address"
        )

    conn = get_connection()
    # 01-REQUIREMENTS.md Section 9: circuit_id is the key once known (from
    # provisioning), but address is what's available before that -- this is
    # exactly the "no circuit assigned for this address" lookup path the
    # ORD-88213 worked example depends on.
    if circuit_id:
        row = conn.execute(
            "SELECT * FROM inventory WHERE circuit_id = ?", (circuit_id,)
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT * FROM inventory WHERE address = ?", (address,)
        ).fetchone()
    conn.close()

    if row is None:
        identifier = circuit_id or address
        raise HTTPException(
            status_code=404, detail=f"No inventory record for {identifier}"
        )
    return InventoryRecord(**dict(row))
