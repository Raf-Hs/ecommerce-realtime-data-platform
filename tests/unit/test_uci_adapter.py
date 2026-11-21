"""Tests for the UCI Online Retail II adapter."""

from pathlib import Path

from src.ingestion.uci_online_retail import UciOnlineRetailAdapter
from src.validation.event_validator import validate_event


def test_read_yields_rows() -> None:
    adapter = UciOnlineRetailAdapter(Path("data/samples"), csv_glob="uci_online_retail_sample.csv")
    rows = list(adapter.read())
    assert len(rows) == 5


def test_normalize_purchase() -> None:
    adapter = UciOnlineRetailAdapter(Path("data/samples"), csv_glob="uci_online_retail_sample.csv")
    rows = list(adapter.read())
    event = adapter.normalize(rows[0])
    assert event.source == "uci_online_retail"
    assert event.event_type == "purchase"
    assert event.entity_id.startswith("uci:product:")
    assert event.payload["quantity"] == 12
    assert event.payload["customer_id"] == "uci:customer:13085.0"
    assert validate_event(event) == []


def test_normalize_cancellation() -> None:
    adapter = UciOnlineRetailAdapter(Path("data/samples"), csv_glob="uci_online_retail_sample.csv")
    rows = list(adapter.read())
    event = adapter.normalize(rows[2])
    assert event.event_type == "cancellation"
    assert event.payload["quantity"] == -12
    assert validate_event(event) == []


def test_guest_customer() -> None:
    adapter = UciOnlineRetailAdapter(Path("data/samples"), csv_glob="uci_online_retail_sample.csv")
    rows = list(adapter.read())
    event = adapter.normalize(rows[3])
    assert event.payload["customer_id"] is None
    assert validate_event(event) == []


def test_all_sample_events_valid() -> None:
    adapter = UciOnlineRetailAdapter(Path("data/samples"), csv_glob="uci_online_retail_sample.csv")
    for raw in adapter.read():
        event = adapter.normalize(raw)
        errors = validate_event(event)
        assert errors == [], f"validation errors: {errors}"


def test_missing_file_raises() -> None:
    import pytest

    adapter = UciOnlineRetailAdapter(Path("/nonexistent"), csv_glob="*.csv")
    with pytest.raises(FileNotFoundError):
        list(adapter.read())