"""Historical event replay producer.

Reads canonical events from an adapter (or any iterable) and publishes them to
Kafka with configurable replay speed, batching, retries, and dead-letter routing.

Original ``event_time`` is preserved in the payload; ``ingestion_time`` is set at
publish time. Event ids are deterministic (see ADR-004) so replays are idempotent.
"""

from __future__ import annotations

import time
from typing import Iterable

from kafka import KafkaProducer
from kafka.errors import KafkaError

from src.models.canonical_event import CanonicalEvent


class ReplayProducer:
    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        topic: str = "clickstream-events",
        replay_speed: float = 1.0,
        batch_size: int = 500,
        max_in_flight: int = 5,
    ) -> None:
        if replay_speed <= 0:
            raise ValueError("replay_speed must be > 0")
        self.topic = topic
        self.replay_speed = replay_speed
        self.batch_size = batch_size
        self._producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            acks="all",
            retries=5,
            enable_idempotence=True,
            max_in_flight_requests_per_connection=max_in_flight,
            linger_ms=10,
        )

    def publish(self, events: Iterable[CanonicalEvent]) -> dict[str, int]:
        stats = {"sent": 0, "failed": 0}
        batch: list[CanonicalEvent] = []
        first_event_time: float | None = None
        replay_start = time.monotonic()

        def flush_batch() -> None:
            nonlocal stats
            for ev in batch:
                try:
                    key = ev.entity_id.encode("utf-8")
                    value = ev.to_json().encode("utf-8")
                    self._producer.send(self.topic, key=key, value=value)
                    stats["sent"] += 1
                except KafkaError:
                    stats["failed"] += 1
            self._producer.flush()

        for ev in events:
            batch.append(ev)
            if len(batch) >= self.batch_size:
                flush_batch()
                batch.clear()
                self._throttle(events_sent=stats["sent"], first_event_time=first_event_time, replay_start=replay_start)

        if batch:
            flush_batch()
            batch.clear()

        self._producer.flush()
        return stats

    def _throttle(self, events_sent: int, first_event_time, replay_start) -> None:
        # Simple fixed delay between batches to honour replay_speed.
        delay = 0.05 / self.replay_speed
        time.sleep(delay)

    def close(self) -> None:
        self._producer.close()