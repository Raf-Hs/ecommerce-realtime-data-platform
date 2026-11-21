"""Tests for the Olist adapter."""

from pathlib import Path

from src.ingestion.olist import OlistAdapter
from src.validation.event_validator import validate_event


def test_orders_read_and_normalize() -> None:
    adapter = OlistAdapter(Path("data/samples"), kind="orders", filename="olist_orders_sample.csv")
    rows = list(adapter.read())
    assert len(rows) == 2
    events = [adapter.normalize(r) for r in rows]
    assert events[0].event_type == "order_created"
    assert events[0].source == "olist"
    assert events[0].entity_id.startswith("olist:order:")
    for e in events:
        assert validate_event(e) == [], validate_event(e)


def test_order_items() -> None:
    adapter = OlistAdapter(Path("data/samples"), kind="order_items", filename="olist_order_items_sample.csv")
    rows = list(adapter.read())
    assert len(rows) == 3
    events = [adapter.normalize(r) for r in rows]
    assert all(e.event_type == "order_item_added" for e in events)
    assert all(e.entity_id.startswith("olist:product:") for e in events)


def test_payments() -> None:
    adapter = OlistAdapter(Path("data/samples"), kind="payments", filename="olist_order_payments_sample.csv")
    rows = list(adapter.read())
    assert len(rows) == 2
    events = [adapter.normalize(r) for r in rows]
    assert all(e.event_type == "payment_recorded" for e in events)


def test_invalid_kind_raises() -> None:
    import pytest

    with pytest.raises(ValueError):
        OlistAdapter(Path("data/samples"), kind="bogus")