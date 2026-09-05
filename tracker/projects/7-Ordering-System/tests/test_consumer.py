from agent.state import DiagnosisOutput
from events import consumer as consumer_module
from events.consumer import handle_event

# Isolated unit test: a constructed fake event + an injected fake
# graph/publish -- no real Kafka broker, no real supervisor graph
# (02-ARCHITECTURE.md Section 13's isolation-then-integration pattern,
# same DI shape as agent/supervisor.py's node factories). The full
# integration test (real broker, real graph) lives in
# tests/test_events_integration.py, since it needs the real Docker Kafka
# stack running -- a genuinely different, slower test tier, same split as
# tests/test_kb_vector.py vs. tests/test_kb_merged.py in Phase 8.

_FAKE_DIAGNOSIS = DiagnosisOutput(
    root_cause="no circuit assigned for address",
    confidence="high",
    evidence=["no circuit assigned for address"],
    recommended_action="assign a circuit",
    insufficient_evidence=False,
)


class FakeGraph:
    def __init__(self, diagnosis=_FAKE_DIAGNOSIS):
        self._diagnosis = diagnosis
        self.invoked_with = None

    async def ainvoke(self, state, config=None):
        self.invoked_with = state
        return {"diagnosis": self._diagnosis}


async def test_handle_event_parses_order_id_and_invokes_graph():
    graph = FakeGraph()
    event = {"order_id": "ORD-88213", "error_code": "ERR_4471"}

    published = []

    async def fake_publish(topic, payload):
        published.append((topic, payload))

    result = await handle_event(event, graph=graph, publish=fake_publish)

    assert graph.invoked_with["order_id"] == "ORD-88213"
    assert result["order_id"] == "ORD-88213"
    assert result["diagnosis"] is _FAKE_DIAGNOSIS


async def test_handle_event_publishes_to_diagnosis_events():
    graph = FakeGraph()
    published = []

    async def fake_publish(topic, payload):
        published.append((topic, payload))

    await handle_event({"order_id": "ORD-88213"}, graph=graph, publish=fake_publish)

    assert len(published) == 1
    topic, payload = published[0]
    assert topic == "diagnosis.events"
    assert payload["order_id"] == "ORD-88213"
    assert payload["triggering_event"] == {"order_id": "ORD-88213"}
    assert payload["diagnosis"]["root_cause"] == _FAKE_DIAGNOSIS.root_cause
    assert "correlation_id" in payload


async def test_handle_event_generates_a_fresh_correlation_id_per_call():
    graph = FakeGraph()
    published = []

    async def fake_publish(topic, payload):
        published.append(payload)

    r1 = await handle_event({"order_id": "ORD-A"}, graph=graph, publish=fake_publish)
    r2 = await handle_event({"order_id": "ORD-B"}, graph=graph, publish=fake_publish)

    assert r1["correlation_id"] != r2["correlation_id"]


async def test_run_consumer_composes_build_consumer_and_consume_forever(monkeypatch):
    # run_consumer() itself is just wiring -- verified here with fakes
    # rather than a real broker (tests/test_events_integration.py already
    # covers the real, full end-to-end path).
    calls = []

    async def fake_build_consumer(group_id, auto_offset_reset):
        calls.append(("build", group_id, auto_offset_reset))
        return "fake-consumer-object"

    async def fake_consume_forever(consumer):
        calls.append(("consume", consumer))

    monkeypatch.setattr(consumer_module, "build_consumer", fake_build_consumer)
    monkeypatch.setattr(consumer_module, "consume_forever", fake_consume_forever)

    await consumer_module.run_consumer(group_id="g1", auto_offset_reset="latest")

    assert calls == [("build", "g1", "latest"), ("consume", "fake-consumer-object")]
