"""Tests for the synthetic event generator."""

from src.producers.synthetic import generate_inventory_events
from src.validation.event_validator import validate_event


def test_generates_requested_count() -> None:
    events = list(generate_inventory_events(["syn:product:1", "syn:product:2"], 10, seed=1))
    assert len(events) == 10


def test_deterministic_with_seed() -> None:
    a = [e.event_id for e in generate_inventory_events(["syn:product:1"], 5, seed=7)]
    b = [e.event_id for e in generate_inventory_events(["syn:product:1"], 5, seed=7)]
    assert a == b


def test_all_synthetic_events_valid() -> None:
    for event in generate_inventory_events(["syn:product:1", "syn:product:2"], 20, seed=2):
        assert event.source == "synthetic"
        assert event.entity_id.startswith("syn:")
        assert event.provenance["generator_version"]
        assert validate_event(event) == []


def test_provenance_present() -> None:
    event = next(generate_inventory_events(["syn:product:1"], 1, seed=3))
    assert "generation_rule_id" in event.provenance
    assert event.provenance["seed"] == 3