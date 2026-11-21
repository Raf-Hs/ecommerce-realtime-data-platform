"""Kafka consumer with validation and dead-letter routing.

Consumes messages from a source topic, validates them against the canonical
event schema, routes invalid messages to ``invalid-events`` and unprocessable
messages to ``dead-letter-events``, and tracks per-batch counters.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Callable, Iterable

from kafka import KafkaConsumer, KafkaProducer

from src.models.canonical_event import CanonicalEvent
from src.validation.event_validator import validate_event

logger = logging.getLogger(__name__)


@dataclass
class ConsumerStats:
    total: int = 0
    valid: int = 0
    invalid: int = 0
    dead_letter: int = 0
    errors: list[str] = field(default_factory=list)


class ValidatingConsumer:
    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        source_topic: str = "clickstream-events",
        group_id: str = "novacart-validator",
        invalid_topic: str = "invalid-events",
        dlq_topic: str = "dead-letter-events",
        on_valid: Callable[[CanonicalEvent], None] | None = None,
    ) -> None:
        self.source_topic = source_topic
        self.invalid_topic = invalid_topic
        self.dlq_topic = dlq_topic
        self.on_valid = on_valid
        self._consumer = KafkaConsumer(
            source_topic,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            consumer_timeout_ms=5000,
        )
        self._producer = KafkaProducer(bootstrap_servers=bootstrap_servers)

    def process_one(self, raw_bytes: bytes) -> str:
        """Process a single raw message. Return 'valid', 'invalid', or 'dlq'."""
        try:
            data = json.loads(raw_bytes.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            self._send_dlq(raw_bytes, f"json parse error: {exc}")
            return "dlq"

        if not isinstance(data, dict):
            self._send_invalid({"raw": data}, "payload is not a JSON object")
            return "invalid"

        # Reconstruct a CanonicalEvent best-effort.
        try:
            event = CanonicalEvent(**{k: data[k] for k in CanonicalEvent.__dataclass_fields__ if k in data})
        except (KeyError, TypeError) as exc:
            self._send_invalid(data, f"missing field: {exc}")
            return "invalid"

        errors = validate_event(event)
        if errors:
            self._send_invalid(data, "; ".join(errors))
            return "invalid"

        if self.on_valid is not None:
            self.on_valid(event)
        return "valid"

    def _send_invalid(self, data: dict, reason: str) -> None:
        payload = {"record": data, "reason": reason, "target": "invalid-events"}
        self._producer.send(self.invalid_topic, value=json.dumps(payload).encode("utf-8"))

    def _send_dlq(self, raw: bytes, reason: str) -> None:
        payload = {"raw": raw.decode("utf-8", errors="replace"), "reason": reason}
        self._producer.send(self.dlq_topic, value=json.dumps(payload).encode("utf-8"))

    def run(self, max_messages: int | None = None) -> ConsumerStats:
        stats = ConsumerStats()
        count = 0
        for msg in self._consumer:
            stats.total += 1
            result = self.process_one(msg.value)
            if result == "valid":
                stats.valid += 1
            elif result == "invalid":
                stats.invalid += 1
            else:
                stats.dead_letter += 1
            count += 1
            if max_messages is not None and count >= max_messages:
                break
        self._producer.flush()
        logger.info("consumer stats: total=%d valid=%d invalid=%d dlq=%d",
                    stats.total, stats.valid, stats.invalid, stats.dead_letter)
        return stats

    def close(self) -> None:
        self._consumer.close()
        self._producer.close()