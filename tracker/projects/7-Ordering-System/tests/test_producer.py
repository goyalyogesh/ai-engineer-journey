from events.producer import publish_events_best_effort


async def test_publish_events_best_effort_empty_list_is_a_noop():
    # Should return immediately without even trying to connect.
    await publish_events_best_effort([])


async def test_publish_events_best_effort_degrades_when_kafka_unreachable(monkeypatch):
    # A missing/unreachable broker must never raise out of this function
    # (mock services call this during their own FastAPI startup, and a
    # broker being down must not prevent them from serving their
    # Kafka-independent read endpoints -- 05-DEVELOPMENT-LOG.md's Phase 9
    # entry). Verified directly: an unreachable broker fails in ~0ms
    # (connection refused), not a hung timeout.
    monkeypatch.setenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:19999")
    await publish_events_best_effort([("some.topic", {"order_id": "ORD-X"})])
