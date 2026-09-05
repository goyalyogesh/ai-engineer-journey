"""Kafka event consumer -- FR7's async trigger path (02-ARCHITECTURE.md
Section 4). Subscribes to order.provisioning_failed and
order.billing_hold_applied, invokes the *same* compiled supervisor graph
`api/main.py`'s POST /diagnose uses (one agent core, two trigger paths,
not two separate implementations), publishes the result to
diagnosis.events.
"""
import asyncio
import json
import os
import uuid

from aiokafka import AIOKafkaConsumer

from agent.observability import correlation_id_var, log_event
from agent.state import DiagnosisOutput
from agent.supervisor import get_supervisor_graph, initial_supervisor_state
from events.producer import publish_event

TRIGGER_TOPICS = ["order.provisioning_failed", "order.billing_hold_applied"]


async def handle_event(event: dict, graph=None, publish=publish_event) -> dict:
    """The actual per-event logic, deliberately isolated from the Kafka
    subscription loop below -- callable directly with a constructed fake
    event and an injected fake graph/publish function, no real broker or
    real supervisor graph needed (Section 13's isolation-then-integration
    pattern, same DI shape as agent/supervisor.py's node factories).
    """
    order_id = event["order_id"]
    correlation_id = str(uuid.uuid4())
    token = correlation_id_var.set(correlation_id)
    try:
        log_event("consumer_event_received", topic_event=event)
        resolved_graph = graph or await get_supervisor_graph()
        config = {"configurable": {"thread_id": correlation_id}}
        result = await resolved_graph.ainvoke(initial_supervisor_state(order_id), config=config)
        diagnosis: DiagnosisOutput = result["diagnosis"]
        await publish("diagnosis.events", {
            "order_id": order_id,
            "correlation_id": correlation_id,
            "triggering_event": event,
            "diagnosis": diagnosis.model_dump(),
        })
        return {"order_id": order_id, "correlation_id": correlation_id, "diagnosis": diagnosis}
    finally:
        correlation_id_var.reset(token)


async def build_consumer(
    group_id: str = "order-diagnosis-consumer", auto_offset_reset: str = "earliest"
) -> AIOKafkaConsumer:
    # group_id/auto_offset_reset are parameterized (not hardcoded) so
    # tests/test_events_integration.py can use a fresh, disposable group
    # starting from "latest" -- the real deployed consumer wants the
    # stable default (resume from where it left off across restarts,
    # process everything that happened while it was down), but a test
    # using that same stable group_id would otherwise have to churn
    # through this project's own accumulated testing-session backlog
    # (every mock-service restart across every phase re-publishes its
    # seed events) -- each backlog message triggering a real, ~10-15s
    # diagnosis -- before ever reaching the message the test just
    # published. Caught by the first real run of this test.
    #
    # Split from the consume loop below (build vs. run) so a caller can
    # confirm the consumer group has actually been assigned partitions
    # (`consumer.assignment()` non-empty) before publishing anything --
    # `auto_offset_reset` only takes effect once that assignment happens,
    # which is *not* guaranteed to have completed just because `.start()`
    # returned. A fixed `asyncio.sleep()` before publishing raced this and
    # intermittently missed the message entirely (also caught by the first
    # real run of tests/test_events_integration.py).
    consumer = AIOKafkaConsumer(
        *TRIGGER_TOPICS,
        bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
        group_id=group_id,
        auto_offset_reset=auto_offset_reset,
    )
    await consumer.start()
    return consumer


async def consume_forever(consumer: AIOKafkaConsumer) -> None:
    try:
        async for message in consumer:
            event = json.loads(message.value.decode("utf-8"))
            await handle_event(event)
    finally:
        await consumer.stop()


async def run_consumer(
    group_id: str = "order-diagnosis-consumer", auto_offset_reset: str = "earliest"
) -> None:
    consumer = await build_consumer(group_id, auto_offset_reset)
    await consume_forever(consumer)


if __name__ == "__main__":
    asyncio.run(run_consumer())
