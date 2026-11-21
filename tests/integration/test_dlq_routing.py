"""Integration test: invalid messages are routed to invalid-events / DLQ."""

import json
import socket
import time

import pytest
from kafka import KafkaConsumer, KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

from src.consumers.kafka_consumer import ValidatingConsumer

BOOTSTRAP = "localhost:9092"
TEST_TOPIC = "novacart-dlq-test"


def _kafka_available() -> bool:
    try:
        with socket.create_connection(("localhost", 9092), timeout=3):
            return True
    except OSError:
        return False


def _ensure_topic() -> None:
    admin = KafkaAdminClient(bootstrap_servers=BOOTSTRAP)
    try:
        admin.create_topics([NewTopic(name=TEST_TOPIC, num_partitions=1, replication_factor=1)])
    except TopicAlreadyExistsError:
        pass
    finally:
        admin.close()


def test_invalid_message_routed_to_invalid_topic() -> None:
    _ensure_topic()
    producer = KafkaProducer(bootstrap_servers=BOOTSTRAP)
    valid_payload = {
        "event_id": "abc123",
        "event_type": "view",
        "event_time": "2015-06-01T00:00:00Z",
        "ingestion_time": "2026-01-01T00:00:00Z",
        "source": "retailrocket",
        "source_event_id": "1",
        "entity_type": "product",
        "entity_id": "rr:item:100",
        "payload": {},
        "schema_version": "1.0.0",
        "provenance": {},
    }
    invalid_payload = {"event_type": "view"}  # missing required fields
    producer.send(TEST_TOPIC, value=json.dumps(valid_payload).encode())
    producer.send(TEST_TOPIC, value=json.dumps(invalid_payload).encode())
    producer.send(TEST_TOPIC, value=b"not json {{{")
    producer.flush()
    producer.close()

    # Give Kafka a moment to settle
    time.sleep(1)

    consumer = ValidatingConsumer(
        source_topic=TEST_TOPIC,
        group_id=f"dlq-test-{time.time()}",
    )
    # process a bounded number
    stats = consumer.run(max_messages=3)
    consumer.close()

    assert stats.total >= 3
    assert stats.invalid >= 1
    assert stats.dead_letter >= 1