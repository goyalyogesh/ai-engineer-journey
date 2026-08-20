import os
import random
import asyncio
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from .db import get_connection, init_db
from .seed_data import seed
from .models import OrderRecord

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Seeded on startup so the service is queryable immediately once running
    # -- 04-BUILD-PLAN.md Phase 1's seed table, not Phase 6's full golden set.
    init_db()
    seed()
    yield


app = FastAPI(title="Mock CRM Service", lifespan=lifespan)


async def simulate_latency_and_failure() -> None:
    # 02-ARCHITECTURE.md Section 11: mocks simulate realistic latency +
    # transient failures, not instant always-succeed responses -- needed so
    # p95 latency (03-EVALUATION.md) and the retry/"unavailable" evidence
    # path (Section 3.6) have something real to exercise, not a toy always-
    # fast, always-correct stand-in. Read fresh per-request (not cached at
    # import time) so tests can override via env vars deterministically.
    failure_rate = float(os.environ.get("MOCK_FAILURE_RATE", 0.1))
    latency_min = int(os.environ.get("MOCK_LATENCY_MIN_MS", 200))
    latency_max = int(os.environ.get("MOCK_LATENCY_MAX_MS", 1500))
    await asyncio.sleep(random.uniform(latency_min, latency_max) / 1000)
    if random.random() < failure_rate:
        raise HTTPException(status_code=503, detail="transient failure")


@app.get("/orders/{order_id}", response_model=OrderRecord)
async def get_order(order_id: str) -> OrderRecord:
    await simulate_latency_and_failure()
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM orders WHERE order_id = ?", (order_id,)
    ).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")
    return OrderRecord(**dict(row))
