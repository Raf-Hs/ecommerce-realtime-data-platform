"""Integration test: replay producer -> Kafka round trip. Requires running Kafka."""

import socket

import pytest

from src.ingestion.retailrocket import RetailrocketAdapter
from src.producers.replay import ReplayProducer


def _kafka_available() -> bool:
    try:
        with socket.create_connection(("localhost", 9092), timeout=3):
            return True
    except OSError:
        return False


@pytest.mark.skipif(not _kafka_available(), reason="Kafka not running")
def test_replay_publishes_events() -> None:
    adapter = RetailrocketAdapter("data/samples", events_file="retailrocket_events_sample.csv")
    events = [adapter.normalize(r) for r in adapter.read()]
    producer = ReplayProducer(topic="novacart-replay-test", replay_speed=100.0, batch_size=2)
    stats = producer.publish(events)
    producer.close()
    assert stats["sent"] == len(events)
    assert stats["failed"] == 0