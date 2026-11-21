"""Base class for source adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable

from src.models.canonical_event import CanonicalEvent


class BaseAdapter(ABC):
    """Common interface for all source adapters."""

    source: str

    def __init__(self, data_path: Path | str) -> None:
        self.data_path = Path(data_path)

    @abstractmethod
    def read(self) -> Iterable[dict]:
        """Yield raw records from the source."""

    @abstractmethod
    def normalize(self, raw: dict, source_event_id: str) -> CanonicalEvent:
        """Convert a raw record into a canonical event."""

    def validate(self, event: CanonicalEvent) -> list[str]:
        """Return a list of validation errors (empty if valid)."""
        errors: list[str] = []
        if not event.event_id:
            errors.append("missing event_id")
        if not event.event_type:
            errors.append("missing event_type")
        if not event.event_time:
            errors.append("missing event_time")
        if event.source not in {"retailrocket", "olist", "instacart", "synthetic"}:
            errors.append(f"unknown source: {event.source}")
        if not event.entity_id:
            errors.append("missing entity_id")
        return errors