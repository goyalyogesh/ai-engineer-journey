import pytest
from fastapi.testclient import TestClient

from mock_services.crm.main import app as crm_app
from mock_services.billing.main import app as billing_app
from mock_services.provisioning.main import app as provisioning_app
from mock_services.inventory.main import app as inventory_app


@pytest.fixture(autouse=True)
def fast_deterministic_mocks(monkeypatch):
    # Keep these tests fast and non-flaky despite the mock services'
    # intentional latency/failure simulation (02-ARCHITECTURE.md Section
    # 11) -- that randomness is a real feature, tested deliberately in
    # Phase 2 (MOCK_FAILURE_RATE=1.0, the retry/"unavailable" path), not
    # something these happy-path/404 tests should have to tolerate.
    monkeypatch.setenv("MOCK_FAILURE_RATE", "0")
    monkeypatch.setenv("MOCK_LATENCY_MIN_MS", "1")
    monkeypatch.setenv("MOCK_LATENCY_MAX_MS", "5")


def test_crm_happy_path():
    with TestClient(crm_app) as client:
        response = client.get("/orders/ORD-88213")
        assert response.status_code == 200
        data = response.json()
        assert data["order_id"] == "ORD-88213"
        assert data["customer_id"] == "CUST-001"
        assert data["status"] == "created"


def test_crm_404():
    with TestClient(crm_app) as client:
        response = client.get("/orders/ORD-DOES-NOT-EXIST")
        assert response.status_code == 404


def test_billing_happy_path():
    with TestClient(billing_app) as client:
        response = client.get("/billing/CUST-001")
        assert response.status_code == 200
        data = response.json()
        assert data["customer_id"] == "CUST-001"
        assert data["payment_status"] == "authorized"
        assert data["hold_active"] is False


def test_billing_404():
    with TestClient(billing_app) as client:
        response = client.get("/billing/CUST-DOES-NOT-EXIST")
        assert response.status_code == 404


def test_provisioning_happy_path():
    with TestClient(provisioning_app) as client:
        response = client.get("/provisioning/ORD-88213")
        assert response.status_code == 200
        data = response.json()
        assert data["order_id"] == "ORD-88213"
        assert data["status"] == "failed"
        assert data["error_code"] == "ERR_4471"


def test_provisioning_404():
    with TestClient(provisioning_app) as client:
        response = client.get("/provisioning/ORD-DOES-NOT-EXIST")
        assert response.status_code == 404


def test_inventory_happy_path():
    with TestClient(inventory_app) as client:
        response = client.get("/inventory", params={"circuit_id": "C-600"})
        assert response.status_code == 200
        data = response.json()
        assert data["circuit_id"] == "C-600"
        assert data["status"] == "assigned"


def test_inventory_requires_a_lookup_key():
    # Neither circuit_id nor address given -- this service's own contract
    # (not a retry/failure-simulation concern, so it belongs in Phase 1's
    # own tests, not Phase 2's).
    with TestClient(inventory_app) as client:
        response = client.get("/inventory")
        assert response.status_code == 400


def test_inventory_404():
    with TestClient(inventory_app) as client:
        # ORD-88213's address has no circuit assigned -- this is the exact
        # lookup the worked example (02-ARCHITECTURE.md Section 1) depends on.
        response = client.get(
            "/inventory", params={"address": "100 Main St, Springfield"}
        )
        assert response.status_code == 404


def test_worked_example_ord_88213_end_to_end():
    # 04-BUILD-PLAN.md Phase 1's actual definition of done: querying
    # ORD-88213 across all 4 services reproduces the worked example
    # (02-ARCHITECTURE.md Section 1) exactly.
    with TestClient(crm_app) as crm_client:
        crm = crm_client.get("/orders/ORD-88213").json()
    assert crm["status"] == "created"

    with TestClient(billing_app) as billing_client:
        billing = billing_client.get(f"/billing/{crm['customer_id']}").json()
    assert billing["payment_status"] == "authorized"
    assert billing["hold_active"] is False

    with TestClient(provisioning_app) as prov_client:
        provisioning = prov_client.get("/provisioning/ORD-88213").json()
    assert provisioning["status"] == "failed"
    assert provisioning["error_code"] == "ERR_4471"
    assert provisioning["circuit_id"] is None

    with TestClient(inventory_app) as inv_client:
        inv_response = inv_client.get(
            "/inventory", params={"address": crm["address"]}
        )
    assert inv_response.status_code == 404  # no circuit assigned for this address
