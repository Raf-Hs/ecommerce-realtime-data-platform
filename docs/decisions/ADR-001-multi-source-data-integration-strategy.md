# ADR-001: Multi-Source Data Integration Strategy

## Status

Accepted (Phase 0)

## Context

NovaCart's data is spread across independent systems. The project mandates at least
three independent public datasets (Retailrocket, Olist, plus a product catalog
source) plus synthetic operational events. These datasets have no shared identifiers.

## Problem

How do we integrate multiple independent data sources into one platform without
fabricating relationships between unrelated identifiers?

## Options considered

1. **Direct join across sources.** Map Retailrocket `itemid` to Olist `product_id`,
   Retailrocket `visitorid` to Olist `customer_id`. Rejected: no valid key exists;
   any mapping would be invented.
2. **Shared surrogate keys via fuzzy matching.** Match products by name/category.
   Rejected: Retailrocket values are hashed; categories are unrelated taxonomies.
   Would fabricate relationships.
3. **Canonical event envelope with source-prefixed identifiers.** Each source maps
   into a common envelope; identifiers are prefixed (`rr:`, `olist:`, `syn:`) and
   never treated as globally unique. Cross-source analysis is limited to
   side-by-side aggregates. Accepted.
4. **Single merged dataset.** Collapse all sources into one table. Rejected: loses
   provenance and implies false linkage.

## Decision

Adopt option 3. Define a canonical event envelope; preserve source-specific
identifiers with source prefixes; restrict cross-source analysis to independently
computed aggregates; label any simulated connection explicitly.

## Rationale

- Prevents accidental cross-source joins at the schema level.
- Preserves provenance and lineage.
- Makes the "no fabricated joins" rule enforceable by code (prefixed IDs, no
  cross-source foreign keys).
- Still delivers a unified operational view through the event backbone.

## Consequences

- Cross-source "conversion rate" metrics are out of scope; documented as a
  limitation.
- Business outputs are per-source or side-by-side, not joined.
- Synthetic events must use their own identifier namespace and be labeled.

## Trade-offs

- Less impressive-looking cross-source analytics, but honest and defensible.
- Slightly more schema boilerplate (envelope fields on every event).