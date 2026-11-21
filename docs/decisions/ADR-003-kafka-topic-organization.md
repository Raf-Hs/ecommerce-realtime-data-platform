# ADR-003: Kafka Topic Organization

## Status

Accepted (Phase 0, initial proposal — partition counts subject to benchmarking)

## Context

Multiple sources and event types must be organized into Kafka topics with sensible
keys, partitioning, and retention.

## Problem

How to organize topics to balance ordering guarantees, throughput, and
operational simplicity?

## Options considered

1. **One topic per source file.** Too granular; many topics, low volume each.
2. **One topic per event type, source-agnostic.** Loses source isolation and makes
   DLQ routing ambiguous.
3. **Domain-oriented topics by business domain, with source as a field.** Topics:
   `clickstream-events`, `transaction-events`, `product-events`,
   `inventory-events`, plus `invalid-events` and `dead-letter-events`. Accepted.

## Decision

Adopt option 3. Keys: product id for clickstream/inventory/product events, order
id for transaction events, source for invalid/DLQ. Initial partitions: 6 for
high-volume topics, 3 for others. Retention: 7–30 days depending on topic.

## Rationale

- Domain-oriented topics map to consumer groups and business outputs.
- Product/order keys preserve per-entity ordering within a partition.
- Separate invalid/DLQ topics ensure bad records are never silently dropped.

## Consequences

- Cross-entity ordering is not guaranteed (acceptable).
- Partition counts are initial guesses; must be revisited after throughput
  measurement (Phase 6).
- Retention is local-disk limited.

## Trade-offs

- Fewer topics than per-event-type, but enough isolation for independent
  consumers.