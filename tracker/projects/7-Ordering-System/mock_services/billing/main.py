import os
import random
import asyncio
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from .db import get_connection, init_db
from .seed_data import RECORDS, seed
from .models import BillingRecord

load_dotenv()


async def _publish_seed_events() -> None:
    # Phase 9 (02-ARCHITECTURE.md Section 4): order.billing_hold_applied /
    # order.payment_authorized. Billing's own data keys on customer_id, not
    # order_id (01-REQUIREMENTS.md Section 9's join problem) -- a real
    # Billing system might publish customer_id-only events and rely on a
    # separate lookup. Here, since this project's seed data has a genuine
    # 1:1 customer<->order mapping, the order_id is resolved against CRM's
    # own seed data at publish time and included directly, so the
    # consumer (events/consumer.py) never needs a second lookup step --
    # a deliberate, honest simplification specific to this mock system,
    # not how a production Billing service would necessarily behave.
    from mock_services.crm.seed_data import ORDERS
    from events.producer import publish_events_best_effort

    customer_to_order = {customer_id: order_id for order_id, customer_id, *_ in ORDERS}

    events = []
    for customer_id, payment_status, hold_active, hold_reason, plan in RECORDS:
        order_id = customer_to_order.get(customer_id)
        if order_id is None:
            continue
        if hold_active:
            events.append(("order.billing_hold_applied", {
                "order_id": order_id, "customer_id": customer_id, "hold_reason": hold_reason,
            }))
        elif payment_status == "authorized":
            events.append(("order.payment_authorized", {
                "order_id": order_id, "customer_id": customer_id,
            }))
    await publish_events_best_effort(events)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed()
    await _publish_seed_events()
    yield


app = FastAPI(title="Mock Billing Service", lifespan=lifespan)


async def simulate_latency_and_failure() -> None:
    # See mock_services/crm/main.py for why this is here and why it reads
    # env vars fresh per-request rather than caching at import time.
    failure_rate = float(os.environ.get("MOCK_FAILURE_RATE", 0.1))
    latency_min = int(os.environ.get("MOCK_LATENCY_MIN_MS", 200))
    latency_max = int(os.environ.get("MOCK_LATENCY_MAX_MS", 1500))
    await asyncio.sleep(random.uniform(latency_min, latency_max) / 1000)
    if random.random() < failure_rate:
        raise HTTPException(status_code=503, detail="transient failure")


@app.get("/billing/{customer_id}", response_model=BillingRecord)
async def get_billing(customer_id: str) -> BillingRecord:
    await simulate_latency_and_failure()
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM billing_status WHERE customer_id = ?", (customer_id,)
    ).fetchone()
    conn.close()
    if row is None:
        raise HTTPException(
            status_code=404, detail=f"Billing record for {customer_id} not found"
        )
    return BillingRecord(**dict(row))
