"""Adapter for the Retailrocket e-commerce dataset."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from src.ingestion.base import BaseAdapter
from src.models.canonical_event import CanonicalEvent, make_event_id, now_utc_iso


class RetailrocketAdapter(BaseAdapter):
    source = "retailrocket"

    # Retailrocket event timestamps are Unix milliseconds.
    TIMESTAMP_UNIT = "ms"

    def __init__(self, data_path: Path | str, events_file: str = "events.csv") -> None:
        super().__init__(data_path)
        self.events_file = self.data_path / events_file

    def read(self) -> Iterable[dict]:
        if not self.events_file.exists():
            raise FileNotFoundError(f"Retailrocket events file not found: {self.events_file}")
        with self.events_file.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for idx, row in enumerate(reader):
                row["_row_number"] = idx
                yield row

    def normalize(self, raw: dict, source_event_id: str | None = None) -> CanonicalEvent:
        sid = source_event_id if source_event_id is not None else str(raw["_row_number"])
        event_type = raw["event"].strip().lower()
        ts_ms = int(raw["timestamp"])
        event_time = datetime.fromtimestamp(ts_ms / 1000.0, tz=timezone.utc).isoformat().replace("+00:00", "Z")
        visitor_id = raw["visitorid"]
        item_id = raw["itemid"]
        event_id = make_event_id(self.source, sid, event_time)
        payload = {
            "visitor_id": f"rr:visitor:{visitor_id}",
            "item_id": f"rr:item:{item_id}",
            "transaction_id": raw.get("transactionid") or None,
            "raw_event": event_type,
        }
        return CanonicalEvent(
            event_id=event_id,
            event_type=event_type,
            event_time=event_time,
            ingestion_time=now_utc_iso(),
            source=self.source,
            source_event_id=sid,
            entity_type="product",
            entity_id=f"rr:item:{item_id}",
            payload=payload,
            provenance={
                "dataset": "retailrocket",
                "file": self.events_file.name,
                "row_number": int(raw["_row_number"]),
            },
        )