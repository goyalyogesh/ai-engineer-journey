"""Full integration test for Phase 9's event-driven trigger path
(04-BUILD-PLAN.md's "original v1 check"): publishing a real
order.provisioning_failed event, against the real Docker Kafka broker and
the real compiled supervisor graph (events/consumer.py's real consume
loop, not handle_event() called directly), triggers a full diagnosis with
zero API calls involved, visible on diagnosis.events.

Assumes the local Kafka broker is running and its topics exist
(`docker compose up -d kafka && python -m events.topics`) and Neo4j is up
(search_knowledge_base's graph half, Phase 8) -- the slow, real-
infrastructure integration tier, same split as tests/test_kb_merged.py
vs. tests/test_kb_vector.py/test_kb_graph.py. tests/test_consumer.py
covers the fast, isolated handler logic with fakes; this file is the
"only then" integration layer.
"""
import asyncio
import json
import uuid

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from events.consumer import build_consumer, consume_forever


async def _wait_for_assignment(consumer: AIOKafkaConsumer, timeout: float = 15) -> None:
    # auto_offset_reset only takes effect once the consumer group has
    # actually been assigned partitions -- NOT guaranteed the moment
    # .start() returns. Publishing before assignment completes races
    # "latest" and can silently miss the message (caught on the first
    # real run of this test, which used a fixed asyncio.sleep() instead
    # and intermittently timed out).
    deadline = asyncio.get_event_loop().time() + timeout
    while not consumer.assignment():
        if asyncio.get_event_loop().time() > deadline:
            raise TimeoutError("consumer group was never assigned partitions")
        await asyncio.sleep(0.2)


async def test_provisioning_failed_event_triggers_full_diagnosis_end_to_end():
    # Watch diagnosis.events *before* publishing or starting the trigger
    # consumer, so the real message can never be missed by a race. Fresh,
    # disposable group + "latest" so this test only sees what it's about
    # to publish, not this project's own accumulated testing-session
    # backlog on this topic.
    watcher = AIOKafkaConsumer(
        "diagnosis.events",
        bootstrap_servers="localhost:9092",
        group_id=f"integration-watcher-{uuid.uuid4()}",
        auto_offset_reset="latest",
    )
    await watcher.start()
    await _wait_for_assignment(watcher)

    # The actual process this test verifies exists: a real consumer,
    # subscribed to order.provisioning_failed, running independently in
    # the background -- not the handler function called directly. Same
    # fresh-group/"latest" reasoning as the watcher above (production
    # uses the stable default group instead -- see
    # events/consumer.py's build_consumer() docstring).
    trigger_consumer = await build_consumer(
        group_id=f"integration-test-consumer-{uuid.uuid4()}", auto_offset_reset="latest"
    )
    await _wait_for_assignment(trigger_consumer)
    consumer_task = asyncio.create_task(consume_forever(trigger_consumer))

    producer = AIOKafkaProducer(bootstrap_servers="localhost:9092")
    await producer.start()
    try:
        await producer.send_and_wait(
            "order.provisioning_failed",
            json.dumps({"order_id": "ORD-88213", "error_code": "ERR_4471"}).encode("utf-8"),
        )

        msg = await asyncio.wait_for(watcher.getone(), timeout=60)
        payload = json.loads(msg.value.decode("utf-8"))
        assert payload["order_id"] == "ORD-88213"
        assert payload["triggering_event"]["order_id"] == "ORD-88213"
        assert payload["diagnosis"]["insufficient_evidence"] is False
        root_cause_lower = payload["diagnosis"]["root_cause"].lower()
        assert "circuit" in root_cause_lower or "4471" in root_cause_lower or "provision" in root_cause_lower
    finally:
        await producer.stop()
        await watcher.stop()
        consumer_task.cancel()
        try:
            await consumer_task
        except asyncio.CancelledError:
            pass
