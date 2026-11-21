# ADR-008: Checkpointing and Recovery

## Status

Accepted (Phase 0)

## Context

Spark Structured Streaming must recover from failures without reprocessing
everything or losing state.

## Problem

How to checkpoint state and enable recovery?

## Options considered

1. No checkpointing (reprocess all). Rejected: not scalable, no recovery.
2. Manual offset management. Rejected: error-prone, reinvents Spark's mechanism.
3. Spark checkpointing to a durable path (local FS now, ADLS Gen2 later).
   Accepted: built-in, supports exactly-once sink semantics for supported sinks,
   stores offsets and state.

## Decision

Use Spark checkpointing to a configurable path (local filesystem in dev). Document
the path, backup, and recovery procedure. Store checkpoints alongside the lake but
in a separate directory.

## Rationale

- Built-in, well-tested, supports stateful operations.
- Portable to ADLS Gen2.

## Consequences

- Checkpoint schema is tied to the query; changing the query may invalidate
  checkpoints (documented).
- Checkpoint storage must be durable enough for the recovery claims made.

## Trade-offs

- Checkpoint growth over time; requires cleanup policy.