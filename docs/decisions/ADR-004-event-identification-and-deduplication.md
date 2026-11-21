# ADR-004: Event Identification and Deduplication

## Status

Accepted (Phase 0)

## Context

Replay and reprocessing can produce duplicate events. Downstream aggregates must
not double-count.

## Problem

How to identify events uniquely and deduplicate in a streaming pipeline?

## Options considered

1. Source-native IDs only. Rejected: not globally unique across sources; replay
   can re-emit.
2. UUID generated at ingestion. Rejected: non-deterministic; re-runs produce
   different IDs, breaking idempotency.
3. Deterministic `event_id` = hash(source, source_event_id, event_time). Accepted.
   Reproducible across replays; enables idempotent processing.

## Decision

Adopt option 3. Deduplicate statefully in Spark by `event_id` within a watermark
window. Late duplicates beyond the watermark are accepted as a documented
limitation.

## Rationale

- Deterministic IDs make replay idempotent.
- Stateful dedup integrates with Spark's watermark mechanism.
- Clear, auditable rule.

## Consequences

- Dedup state grows with the watermark window; must be sized to memory.
- Events arriving later than the watermark may be re-processed; documented as a
  limitation (M7).

## Trade-offs

- Hash collisions are theoretically possible; mitigated by using a strong hash and
  including enough fields.