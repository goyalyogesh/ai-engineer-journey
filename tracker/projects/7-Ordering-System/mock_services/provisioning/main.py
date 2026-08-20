import os
import random
import asyncio
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from .db import get_connection, init_db
from .seed_data import seed
from .models import ProvisioningRecord

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed()
    yield


app = FastAPI(title="Mock Provisioning Service", lifespan=lifespan)


async def simulate_latency_and_failure() -> None:
    # See mock_services/crm/main.py for why this is here and why it reads
    # env vars fresh per-request rather than caching at import time.
    failure_rate = float(os.environ.get("MOCK_FAILURE_RATE", 0.1))
    latency_min = int(os.environ.get("MOCK_LATENCY_MIN_MS", 200))
    latency_max = int(os.environ.get("MOCK_LATENCY_MAX_MS", 1500))
    await asyncio.sleep(random.uniform(latency_min, latency_max) / 1000)
    if random.random() < failure_rate:
        raise HTTPException(status_code=503, detail="transient failure")


@app.get("/provisioning/{order_id}", response_model=ProvisioningRecord)
async def get_provisioning(order_id: str) -> ProvisioningRecord:
    await simulate_latency_and_failure()
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM provisioning_log WHERE order_id = ?", (order_id,)
    ).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(
            status_code=404, detail=f"Provisioning record for {order_id} not found"
        )
    return ProvisioningRecord(**dict(row))
