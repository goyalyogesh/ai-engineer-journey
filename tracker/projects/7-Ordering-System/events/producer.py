"""Kafka producer helpers -- used by both the mock services (publishing
state-change events as they seed, Phase 9) and events/consumer.py
(publishing diagnosis results to diagnosis.events).

Two different producer lifecycles on purpose, not one universal
singleton:
- `publish_event`/`_get_producer` -- a lazy, persistent singleton per
  process, same pattern as agent/tools.py's Chroma vectorstore and
  graph/neo4j_for_adk.py's graphdb. Safe for events/consumer.py, which
  runs as a single long-lived process with one asyncio event loop.
- `publish_events_best_effort` -- a short-lived, per-call producer,
  deliberately NOT reusing the shared singleton. Real bug found running
  this for real: this project's own test harness
  (tests/conftest.py) runs each of the 4 mock services in its own
  **thread**, each with its own independent asyncio event loop, inside
  one process. `AIOKafkaProducer` is bound to whichever event loop is
  running when `.start()` is awaited -- a single shared module-level
  singleton, raced by multiple threads' loops concurrently, deadlocked
  (the full test suite hung indefinitely rather than failing loudly --
  see 05-DEVELOPMENT-LOG.md's Phase 9 entry). A fresh producer per call
  sidesteps this entirely: one extra connection per service startup is a
  one-time cost, not a per-request one, so it's a fine tradeoff for code
  that only ever publishes one batch of seed events at startup.
"""
import json
import logging
import os

from aiokafka import AIOKafkaProducer

logger = logging.getLogger(__name__)

_producer: AIOKafkaProducer | None = None


async def _get_producer() -> AIOKafkaProducer:
    global _producer
    if _producer is None:
        # Only assign the module-level singleton *after* start() succeeds --
        # otherwise a failed start() (Kafka unreachable) leaves a
        # constructed-but-never-started producer sitting in `_producer`
        # forever, which aiokafka warns about as "Unclosed AIOKafkaProducer"
        # at process exit and which a later retry could never replace.
        producer = AIOKafkaProducer(
            bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        await producer.start()
        _producer = producer
    return _producer


async def publish_event(topic: str, payload: dict) -> None:
    producer = await _get_producer()
    await producer.send_and_wait(topic, payload)


async def publish_events_best_effort(events: list[tuple[str, dict]]) -> None:
    """Used by the mock services' own startup (publishing seed-derived
    state-change events, Phase 9) -- best-effort on purpose. Kafka is a
    genuinely real, *additional* trigger path (FR7), not a replacement for
    the synchronous POST /diagnose path that already works without it, and
    this project's own test suite (Phases 0-8) never runs a Kafka broker
    at all. A missing broker fails fast (~0ms, connection refused, not a
    hung timeout -- verified directly), so this never meaningfully slows
    startup; it just logs and moves on instead of preventing a mock
    service from serving its (Kafka-independent) read endpoints.

    Uses its own short-lived producer -- see module docstring for why this
    must NOT reuse the shared singleton `_get_producer()` manages.
    """
    if not events:
        return
    try:
        producer = AIOKafkaProducer(
            bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        await producer.start()
        try:
            for topic, payload in events:
                await producer.send_and_wait(topic, payload)
        finally:
            await producer.stop()
    except Exception as e:
        logger.warning(f"Kafka unavailable, skipping seed-event publish: {e}")
