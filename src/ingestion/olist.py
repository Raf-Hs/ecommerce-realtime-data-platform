"""Adapter for the Olist Brazilian e-commerce dataset.

Olist ships several CSVs. This adapter supports three event-producing kinds:
- ``orders``       -> ``order_created`` events
- ``order_items``  -> ``order_item_added`` events
- ``payments``     -> ``payment_recorded`` events
"""

from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Iterable

from src.ingestion.base import BaseAdapter
from src.models.canonical_event import CanonicalEvent, make_event_id, now_utc_iso


def _parse_ts(value: str) -> str:
    if not value:
        return ""
    # Olist timestamps are "YYYY-MM-DD HH:MM:SS"
    dt = datetime.strptime(value.strip(), "%Y-%m-%d %H:%M:%S")
    return dt.replace(tzinfo=__import__("datetime").timezone.utc).isoformat().replace("+00:00", "Z")


class OlistAdapter(BaseAdapter):
    source = "olist"

    KINDS = {"orders", "order_items", "payments"}

    def __init__(
        self, data_path: Path | str, kind: str = "orders", filename: str | None = None
    ) -> None:
        super().__init__(data_path)
        if kind not in self.KINDS:
            raise ValueError(f"Unknown Olist kind: {kind}")
        self.kind = kind
        self.file = self.data_path / (filename or self._filename(kind))

    @staticmethod
    def _filename(kind: str) -> str:
        return {
            "orders": "olist_orders_dataset.csv",
            "order_items": "olist_order_items_dataset.csv",
            "payments": "olist_order_payments_dataset.csv",
        }[kind]

    def read(self) -> Iterable[dict]:
        if not self.file.exists():
            raise FileNotFoundError(f"Olist file not found: {self.file}")
        with self.file.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for idx, row in enumerate(reader):
                row["_row_number"] = idx
                yield row

    def normalize(self, raw: dict, source_event_id: str | None = None) -> CanonicalEvent:
        sid = source_event_id if source_event_id is not None else str(raw["_row_number"])
        if self.kind == "orders":
            return self._normalize_order(raw, sid)
        if self.kind == "order_items":
            return self._normalize_item(raw, sid)
        return self._normalize_payment(raw, sid)

    def _normalize_order(self, raw: dict, sid: str) -> CanonicalEvent:
        order_id = raw["order_id"]
        event_time = _parse_ts(raw.get("order_purchase_timestamp", ""))
        if not event_time:
            event_time = now_utc_iso()
        event_id = make_event_id(self.source, sid, event_time)
        return CanonicalEvent(
            event_id=event_id,
            event_type="order_created",
            event_time=event_time,
            ingestion_time=now_utc_iso(),
            source=self.source,
            source_event_id=sid,
            entity_type="order",
            entity_id=f"olist:order:{order_id}",
            payload={
                "order_id": f"olist:order:{order_id}",
                "customer_id": f"olist:customer:{raw.get('customer_id', '')}",
                "status": raw.get("order_status", ""),
            },
            provenance={"dataset": "olist", "file": self.file.name, "row_number": int(raw["_row_number"])},
        )

    def _normalize_item(self, raw: dict, sid: str) -> CanonicalEvent:
        order_id = raw["order_id"]
        product_id = raw["product_id"]
        event_time = now_utc_iso()
        event_id = make_event_id(self.source, sid, event_time)
        return CanonicalEvent(
            event_id=event_id,
            event_type="order_item_added",
            event_time=event_time,
            ingestion_time=event_time,
            source=self.source,
            source_event_id=sid,
            entity_type="product",
            entity_id=f"olist:product:{product_id}",
            payload={
                "order_id": f"olist:order:{order_id}",
                "product_id": f"olist:product:{product_id}",
                "seller_id": f"olist:seller:{raw.get('seller_id', '')}",
                "price": raw.get("price", ""),
                "freight_value": raw.get("freight_value", ""),
            },
            provenance={"dataset": "olist", "file": self.file.name, "row_number": int(raw["_row_number"])},
        )

    def _normalize_payment(self, raw: dict, sid: str) -> CanonicalEvent:
        order_id = raw["order_id"]
        event_time = now_utc_iso()
        event_id = make_event_id(self.source, sid, event_time)
        return CanonicalEvent(
            event_id=event_id,
            event_type="payment_recorded",
            event_time=event_time,
            ingestion_time=event_time,
            source=self.source,
            source_event_id=sid,
            entity_type="order",
            entity_id=f"olist:order:{order_id}",
            payload={
                "order_id": f"olist:order:{order_id}",
                "payment_type": raw.get("payment_type", ""),
                "payment_value": raw.get("payment_value", ""),
                "installments": raw.get("payment_installments", ""),
            },
            provenance={"dataset": "olist", "file": self.file.name, "row_number": int(raw["_row_number"])},
        )