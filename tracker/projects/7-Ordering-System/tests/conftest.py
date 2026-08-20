# Shared pytest fixtures. Empty at Phase 0 by design (04-BUILD-PLAN.md) --
# fixtures get added per-phase as each layer (mock services, tools,
# specialists, supervisor) actually exists to fixture against.
import os
import threading
import time

import httpx
import pytest

from mock_services.billing.main import app as billing_app
from mock_services.crm.main import app as crm_app
from mock_services.inventory.main import app as inventory_app
from mock_services.provisioning.main import app as provisioning_app

_APPS_AND_PORTS = [
    (crm_app, 8001),
    (billing_app, 8002),
    (provisioning_app, 8003),
    (inventory_app, 8004),
]


def _run_server(app, port):
    import uvicorn

    uvicorn.Server(
        uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
    ).run()


@pytest.fixture(scope="session", autouse=True)
def real_mock_services():
    # 02-ARCHITECTURE.md Section 13: tool functions (and anything that
    # calls them -- specialists, the supervisor) are tested against the
    # *real* mock services, not a further layer of mocking -- so these are
    # genuine uvicorn servers on real sockets (same ports agent/tools.py's
    # *_SERVICE_URL env vars point at by default), not in-process
    # TestClient calls. Promoted from tests/test_tools.py into this shared
    # conftest.py in Phase 3, once test_specialists.py needed the same
    # real services for its own full-stack test.
    os.environ["MOCK_FAILURE_RATE"] = "0"
    os.environ["MOCK_LATENCY_MIN_MS"] = "1"
    os.environ["MOCK_LATENCY_MAX_MS"] = "5"

    for app, port in _APPS_AND_PORTS:
        threading.Thread(target=_run_server, args=(app, port), daemon=True).start()

    for _, port in _APPS_AND_PORTS:
        for _ in range(50):
            try:
                httpx.get(f"http://127.0.0.1:{port}/openapi.json", timeout=0.2)
                break
            except httpx.HTTPError:
                time.sleep(0.1)
    yield
