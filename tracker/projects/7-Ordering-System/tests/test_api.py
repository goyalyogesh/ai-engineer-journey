import json

import pytest
from fastapi.testclient import TestClient

from agent.state import DiagnosisOutput
from api.main import app, get_graph_dependency, limiter

_FAKE_DIAGNOSIS = DiagnosisOutput(
    root_cause="no circuit assigned for address",
    confidence="high",
    evidence=["no circuit assigned for address"],
    recommended_action="assign a circuit",
    insufficient_evidence=False,
)


class FakeGraph:
    """Lets the API layer's own contract (auth, rate limiting, response
    shape) be tested independent of whether the agent logic underneath is
    real or stubbed -- 04-BUILD-PLAN.md Phase 5's Definition of Done says
    this explicitly."""

    async def ainvoke(self, state, config=None):
        return {"diagnosis": _FAKE_DIAGNOSIS}


@pytest.fixture(scope="module")
def client():
    # One TestClient for the whole module -- FastAPI's lifespan (which
    # opens a real AsyncSqliteSaver connection, agent/supervisor.py)
    # should only run its startup/shutdown once per test session, not
    # once per test function.
    with TestClient(app) as c:
        yield c


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    # Without this, "10/minute" budget consumed by an earlier test in
    # this module would bleed into the next one, since `limiter` is a
    # module-level singleton shared by the whole `app`.
    limiter.reset()
    yield


@pytest.fixture
def api_key(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-secret-key")
    return "test-secret-key"


@pytest.fixture
def stub_graph():
    app.dependency_overrides[get_graph_dependency] = lambda: FakeGraph()
    yield
    app.dependency_overrides.pop(get_graph_dependency, None)


def test_diagnose_without_api_key_returns_401(client, api_key, stub_graph):
    response = client.post("/diagnose", json={"order_id": "ORD-88213"})
    assert response.status_code == 401


def test_diagnose_with_wrong_api_key_returns_401(client, api_key, stub_graph):
    response = client.post(
        "/diagnose", json={"order_id": "ORD-88213"}, headers={"X-API-Key": "wrong"}
    )
    assert response.status_code == 401


def test_diagnose_with_valid_api_key_returns_diagnosis(client, api_key, stub_graph):
    response = client.post(
        "/diagnose", json={"order_id": "ORD-88213"}, headers={"X-API-Key": api_key}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["root_cause"] == "no circuit assigned for address"
    assert body["insufficient_evidence"] is False


def test_diagnose_exceeding_rate_limit_returns_429(client, api_key, stub_graph):
    statuses = []
    for _ in range(15):
        response = client.post(
            "/diagnose", json={"order_id": "ORD-88213"}, headers={"X-API-Key": api_key}
        )
        statuses.append(response.status_code)
        if response.status_code == 429:
            break
    assert 429 in statuses
    assert statuses.count(200) <= 10


# --- Real end-to-end: no stub, real graph, real log file -----------------
# 04-BUILD-PLAN.md Phase 5's actual Definition of Done: a real request
# returns the correct diagnosis, and the log file shows a full
# correlation-ID-linked trace of that one request.

async def test_diagnose_real_end_to_end_produces_correlation_linked_log(
    client, api_key, tmp_path, monkeypatch
):
    log_path = tmp_path / "events.jsonl"
    monkeypatch.setenv("LOG_FILE_PATH", str(log_path))

    response = client.post(
        "/diagnose", json={"order_id": "ORD-88213"}, headers={"X-API-Key": api_key}
    )
    assert response.status_code == 200
    body = response.json()
    assert body["insufficient_evidence"] is False

    lines = [json.loads(line) for line in log_path.read_text().splitlines()]
    assert lines, "expected at least one structured log line for this request"

    correlation_ids = {line["correlation_id"] for line in lines}
    # Every line from this one request shares the same correlation_id --
    # that's what makes it possible to grep one request's full trace.
    assert len(correlation_ids) == 1
    assert None not in correlation_ids

    events = {line["event"] for line in lines}
    assert "tool_call" in events
    assert "node_start" in events
    assert "node_end" in events
