"""Tests for the Retailrocket adapter."""

from pathlib import Path

from src.ingestion.retailrocket import RetailrocketAdapter
from src.validation.event_validator import validate_event


def test_read_yields_rows() -> None:
    adapter = RetailrocketAdapter(Path("data/samples"), events_file="retailrocket_events_sample.csv")
    rows = list(adapter.read())
    assert len(rows) == 6
    assert rows[0]["event"] == "view"


def test_normalize_produces_canonical_event() -> None:
    adapter = RetailrocketAdapter(Path("data/samples"), events_file="retailrocket_events_sample.csv")
    rows = list(adapter.read())
    event = adapter.normalize(rows[0])
    assert event.source == "retailrocket"
    assert event.event_type == "view"
    assert event.entity_id.startswith("rr:item:")
    assert event.payload["visitor_id"].startswith("rr:visitor:")
    assert event.provenance["dataset"] == "retailrocket"


def test_all_sample_events_valid() -> None:
    adapter = RetailrocketAdapter(Path("data/samples"), events_file="retailrocket_events_sample.csv")
    for raw in adapter.read():
        event = adapter.normalize(raw)
        errors = validate_event(event)
        assert errors == [], f"validation errors: {errors}"


def test_missing_file_raises() -> None:
    import pytest

    adapter = RetailrocketAdapter(Path("/nonexistent"))
    with pytest.raises(FileNotFoundError):
        list(adapter.read())