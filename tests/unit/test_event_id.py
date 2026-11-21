"""Tests for deterministic event id generation."""

from src.models.canonical_event import make_event_id


def test_event_id_deterministic() -> None:
    a = make_event_id("retailrocket", "42", "2015-06-01T00:00:00Z")
    b = make_event_id("retailrocket", "42", "2015-06-01T00:00:00Z")
    assert a == b


def test_event_id_differs_by_source() -> None:
    a = make_event_id("retailrocket", "42", "2015-06-01T00:00:00Z")
    b = make_event_id("olist", "42", "2015-06-01T00:00:00Z")
    assert a != b


def test_event_id_is_hex_sha256() -> None:
    eid = make_event_id("retailrocket", "1", "2015-06-01T00:00:00Z")
    assert len(eid) == 64
    int(eid, 16)  # raises if not hex