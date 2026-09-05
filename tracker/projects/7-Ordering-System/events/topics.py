"""Kafka topic creation (04-BUILD-PLAN.md Phase 9, 02-ARCHITECTURE.md
Section 4). Run with `python -m events.topics` once the broker is up
(`docker compose up -d kafka`) -- idempotent, safe to re-run, same
discipline as `graph/populate.py`'s MERGE-everywhere idempotency.

Topics named after the real order-management state transitions a system
like this would naturally publish -- explicit creation here (rather than
relying on Kafka's auto-create-on-first-produce default) is the
professional norm for defined partitions/replication, not just decoration.
"""
import asyncio
import os

from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from aiokafka.errors import TopicAlreadyExistsError
from dotenv import load_dotenv

load_dotenv()

TOPICS = [
    "order.created",
    "order.payment_authorized",
    "order.provisioning_failed",
    "order.provisioning_succeeded",
    "order.billing_hold_applied",
    "diagnosis.events",
]


async def create_topics() -> None:
    admin = AIOKafkaAdminClient(
        bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    )
    await admin.start()
    try:
        new_topics = [NewTopic(name=t, num_partitions=1, replication_factor=1) for t in TOPICS]
        try:
            await admin.create_topics(new_topics)
        except TopicAlreadyExistsError:
            pass  # idempotent -- safe to re-run against an already-set-up broker
    finally:
        await admin.close()


if __name__ == "__main__":
    asyncio.run(create_topics())
    print(f"Created/verified {len(TOPICS)} topics.")
