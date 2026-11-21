"""Synthetic operational event generator.

Generates controlled operational events (inventory, checkout, payment) with
explicit provenance. Never presented as real observations.
"""

from __future__ import annotations

import random
from datetime import datetime, timezone, timedelta
from typing import Iterable

from src.models.canonical_event import CanonicalEvent, make_event_id

GENERATOR_VERSION = "0.1.0"

INVENTORY_EVENT_TYPES = ["stock_depleted", "stock_replenished", "inventory_updated"]


def generate_inventory_events(
    product_ids: list[str],
    count: int,
    seed: int = 42,
) -> Iterable[CanonicalEvent]:
    """Generate synthetic inventory events for the given product ids."""
    rng = random.Random(seed)
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for i in range(count):
        pid = rng.choice(product_ids)
        event_type = rng.choice(INVENTORY_EVENT_TYPES)
        quantity = rng.randint(0, 50)
        event_time = (base + timedelta(seconds=i)).isoformat().replace("+00:00", "Z")
        source_event_id = f"gen-{i:06d}"
        event_id = make_event_id("synthetic", source_event_id, event_time)
        yield CanonicalEvent(
            event_id=event_id,
            event_type=event_type,
            event_time=event_time,
            ingestion_time=event_time,
            source="synthetic",
            source_event_id=source_event_id,
            entity_type="product",
            entity_id=pid,
            payload={
                "product_id": pid,
                "quantity_on_hand": quantity,
                "threshold": 5,
            },
            provenance={
                "generator_version": GENERATOR_VERSION,
                "generation_rule_id": "inventory_v1",
                "seed": seed,
            },
        )