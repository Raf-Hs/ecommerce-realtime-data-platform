"""Canonical event envelope used across all sources.

Every source (Retailrocket, Olist, Instacart, synthetic) is normalized into this
single envelope so that downstream processing is source-agnostic while preserving
source-specific identifiers and provenance.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


SCHEMA_VERSION = "1.0.0"

VALID_SOURCES = {"retailrocket", "olist", "instacart", "synthetic"}


@dataclass(frozen=True)
class CanonicalEvent:
    event_id: str
    event_type: str
    event_time: str  # ISO-8601 UTC
    ingestion_time: str  # ISO-8601 UTC
    source: str
    source_event_id: str
    entity_type: str
    entity_id: str
    payload: dict[str, Any]
    schema_version: str = SCHEMA_VERSION
    provenance: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "event_time": self.event_time,
            "ingestion_time": self.ingestion_time,
            "source": self.source,
            "source_event_id": self.source_event_id,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "payload": self.payload,
            "schema_version": self.schema_version,
            "provenance": self.provenance,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), separators=(",", ":"))


def make_event_id(source: str, source_event_id: str, event_time: str) -> str:
    """Deterministic event id per ADR-004."""
    raw = f"{source}|{source_event_id}|{event_time}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")