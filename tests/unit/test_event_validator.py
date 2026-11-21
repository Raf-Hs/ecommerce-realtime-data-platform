"""Tests for event validation."""

from src.models.canonical_event import CanonicalEvent, make_event_id
from src.validation.event_validator import validate_event


def _make_event(**overrides) -> CanonicalEvent:
    base = dict(
        event_id=make_event_id("retailrocket", "1", "2015-06-01T00:00:00Z"),
        event_type="view",
        event_time="2015-06-01T00:00:00Z",
        ingestion_time="2026-01-01T00:00:00Z",
        source="retailrocket",
        source_event_id="1",
        entity_type="product",
        entity_id="rr:item:100",
        payload={},
    )
    base.update(overrides)
    return CanonicalEvent(**base)


def test_valid_event() -> None:
    assert validate_event(_make_event()) == []


def test_invalid_event_type() -> None:
    errors = validate_event(_make_event(event_type="bogus"))
    assert any("invalid event_type" in e for e in errors)


def test_missing_source_prefix() -> None:
    errors = validate_event(_make_event(entity_id="item:100"))
    assert any("source prefix" in e for e in errors)


def test_unknown_source() -> None:
    errors = validate_event(_make_event(source="foo"))
    assert any("unknown source" in e for e in errors)