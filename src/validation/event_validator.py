"""Validation rules for canonical events."""

from __future__ import annotations

from src.models.canonical_event import CanonicalEvent

VALID_EVENT_TYPES = {
    "view",
    "addtocart",
    "transaction",
    "order_created",
    "order_item_added",
    "payment_recorded",
    "payment_attempted",
    "payment_failed",
    "inventory_updated",
    "stock_depleted",
    "stock_replenished",
    "product_price_changed",
    "checkout_started",
}


def validate_event(event: CanonicalEvent) -> list[str]:
    """Return a list of validation errors. Empty list means valid."""
    errors: list[str] = []
    if not event.event_id:
        errors.append("missing event_id")
    if event.event_type not in VALID_EVENT_TYPES:
        errors.append(f"invalid event_type: {event.event_type}")
    if not event.event_time:
        errors.append("missing event_time")
    if event.source not in {"retailrocket", "olist", "instacart", "synthetic"}:
        errors.append(f"unknown source: {event.source}")
    if not event.entity_id:
        errors.append("missing entity_id")
    if not event.entity_id.startswith(
        ("rr:", "olist:", "instacart:", "syn:")
    ):
        errors.append(f"entity_id missing source prefix: {event.entity_id}")
    return errors