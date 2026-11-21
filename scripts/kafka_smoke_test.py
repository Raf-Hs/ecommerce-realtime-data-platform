"""Kafka round-trip smoke test.

Creates (or reuses) a test topic, produces a single message, consumes it back,
and verifies the payload. Used to validate the local Kafka infrastructure
(Phase 1).

Usage:
    python scripts/kafka_smoke_test.py
"""

import json
import time
import uuid
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

BOOTSTRAP = "localhost:9092"
TOPIC = "novacart-smoke-test"


def ensure_topic() -> None:
    admin = KafkaAdminClient(bootstrap_servers=BOOTSTRAP, client_id="smoke-admin")
    try:
        admin.create_topics([NewTopic(name=TOPIC, num_partitions=1, replication_factor=1)])
        print(f"Created topic: {TOPIC}")
    except TopicAlreadyExistsError:
        print(f"Topic already exists: {TOPIC}")
    finally:
        admin.close()


def produce() -> str:
    payload = {"smoke_id": str(uuid.uuid4()), "message": "hello novacart", "ts": time.time()}
    producer = KafkaProducer(bootstrap_servers=BOOTSTRAP)
    future = producer.send(
        TOPIC, key=b"smoke", value=json.dumps(payload).encode("utf-8")
    )
    future.get(timeout=10)
    producer.flush()
    producer.close()
    print(f"Produced: {payload}")
    return payload["smoke_id"]


def consume(expected_id: str, timeout_s: int = 15) -> bool:
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=BOOTSTRAP,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id=f"smoke-group-{uuid.uuid4()}",
        consumer_timeout_ms=timeout_s * 1000,
    )
    deadline = time.time() + timeout_s
    found = False
    for msg in consumer:
        value = json.loads(msg.value.decode("utf-8"))
        if value.get("smoke_id") == expected_id:
            print(f"Consumed: {value}")
            found = True
            break
        if time.time() > deadline:
            break
            found = True
            break
        if time.time() > deadline:
            break
    consumer.close()
    return found


def main() -> int:
    ensure_topic()
    expected_id = produce()
    # small delay to let the message become available
    time.sleep(1)
    if consume(expected_id):
        print("SMOKE TEST PASSED")
        return 0
    print("SMOKE TEST FAILED: message not consumed")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())