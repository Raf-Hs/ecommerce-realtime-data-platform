"""Adapter for the UCI Online Retail II dataset.

Source: https://archive.ics.uci.edu/dataset/502/online+retail+ii
License: CC BY 4.0

The dataset ships as an Excel workbook with two sheets (2009-2010 and
2010-2011). Convert it to CSV first (see scripts/convert_uci_xlsx.py) or point
the adapter at a directory of CSV files with the original column names.
"""

from __future__ import annotations

import csv
import glob
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from src.ingestion.base import BaseAdapter
from src.models.canonical_event import CanonicalEvent, make_event_id, now_utc_iso


def _parse_ts(value: str) -> str:
    if not value:
        return ""
    # UCI timestamps are "YYYY-MM-DD HH:MM:SS"
    try:
        dt = datetime.strptime(value.strip(), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return ""
    return dt.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")


class UciOnlineRetailAdapter(BaseAdapter):
    source = "uci_online_retail"

    COLUMNS = ["Invoice", "StockCode", "Description", "Quantity", "InvoiceDate", "Price", "Customer ID", "Country"]

    def __init__(self, data_path: Path | str, csv_glob: str = "online_retail*.csv") -> None:
        super().__init__(data_path)
        self.csv_glob = csv_glob
        self.files = sorted(self.data_path.glob(csv_glob)) if self.data_path.is_dir() else [self.data_path]

    def read(self) -> Iterable[dict]:
        if not self.files:
            raise FileNotFoundError(f"No UCI CSV files found under: {self.data_path}")
        for f in self.files:
            if not f.exists():
                raise FileNotFoundError(f"UCI file not found: {f}")
            with f.open(newline="", encoding="utf-8", errors="replace") as fh:
                reader = csv.DictReader(fh)
                for idx, row in enumerate(reader):
                    row["_source_file"] = f.name
                    row["_row_number"] = idx
                    yield row

    def normalize(self, raw: dict, source_event_id: str | None = None) -> CanonicalEvent:
        sid = source_event_id if source_event_id is not None else f"{raw['_source_file']}:{raw['_row_number']}"
        invoice = (raw.get("Invoice") or "").strip()
        stock_code = (raw.get("StockCode") or "").strip()
        description = (raw.get("Description") or "").strip() or "unknown"
        try:
            quantity = int(float(raw.get("Quantity") or 0))
        except (ValueError, TypeError):
            quantity = 0
        try:
            price = float(raw.get("Price") or 0.0)
        except (ValueError, TypeError):
            price = 0.0
        customer_id = (raw.get("Customer ID") or "").strip()
        country = (raw.get("Country") or "").strip()
        invoice_date = (raw.get("InvoiceDate") or "").strip()

        # Determine event type: cancellations have Invoice starting with 'C'
        if invoice.upper().startswith("C"):
            event_type = "cancellation"
        elif quantity > 0:
            event_type = "purchase"
        elif quantity < 0:
            event_type = "return"
        else:
            event_type = "adjustment"

        event_time = _parse_ts(invoice_date)
        if not event_time:
            event_time = now_utc_iso()

        event_id = make_event_id(self.source, sid, event_time)
        entity_id = f"uci:product:{stock_code}" if stock_code else ""

        return CanonicalEvent(
            event_id=event_id,
            event_type=event_type,
            event_time=event_time,
            ingestion_time=now_utc_iso(),
            source=self.source,
            source_event_id=sid,
            entity_type="product",
            entity_id=entity_id,
            payload={
                "invoice": invoice,
                "stock_code": stock_code,
                "description": description,
                "quantity": quantity,
                "price": price,
                "line_total": round(quantity * price, 2),
                "customer_id": f"uci:customer:{customer_id}" if customer_id else None,
                "country": country,
            },
            provenance={
                "dataset": "uci_online_retail_ii",
                "file": raw["_source_file"],
                "row_number": int(raw["_row_number"]),
                "license": "CC BY 4.0",
            },
        )