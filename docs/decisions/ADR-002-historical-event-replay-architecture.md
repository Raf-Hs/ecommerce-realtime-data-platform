# ADR-002: Historical Event Replay Architecture

## Status

Accepted (Phase 0)

## Context

The datasets are historical, not live. The platform must simulate continuous
operation by replaying historical events into Kafka while remaining clearly
distinguishable from genuinely live ingestion.

## Problem

How to replay historical data into Kafka with configurable speed, preserved
original timestamps, and reproducible results, without confusing historical and
live data?

## Options considered

1. **Batch dump directly into the lake, bypassing Kafka.** Rejected: defeats the
   purpose of demonstrating Kafka-based streaming and recovery.
2. **Naive replay at full speed with no controls.** Rejected: not reproducible,
   not tunable, hard to test.
3. **Configurable replay producers.** Preserve original `event_time`, set
   `ingestion_time` at publish, deterministic `event_id`, configurable speed,
   batching, delays, retries, DLQ. Accepted.

## Decision

Adopt option 3. Build replay producers per source with explicit configuration:
replay speed multiplier, batch size, inter-batch delay, max in-flight, retry
policy, and DLQ routing. Always preserve `event_time`; always generate
`ingestion_time`. Mark every event's `source` and provenance.

## Rationale

- Makes historical vs. live distinction explicit in the data.
- Enables reproducible benchmarks and failure injection.
- Supports restart/replay from a checkpoint or from the beginning.

## Consequences

- Replay speed must be tuned to watermark durations (fast replay can outrun
  watermarks and create artificial late events).
- Producers must be idempotent on `event_id` to support safe re-runs.

## Trade-offs

- More producer code and configuration, but necessary for a credible streaming
  demo.