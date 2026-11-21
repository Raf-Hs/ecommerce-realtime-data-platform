# ADR-006: Spark Structured Streaming

## Status

Accepted (Phase 0)

## Context

The project requires distributed stream processing with event-time semantics,
watermarks, and recovery.

## Problem

Which stream processing engine?

## Options considered

1. Apache Flink. Rejected: steeper learning curve, less common in portfolio
   contexts, smaller Python ecosystem.
2. Kafka Streams. Rejected: Java-centric, less suited to the Python/Spark
   specialization target.
3. Spark Structured Streaming. Accepted: unified with batch, strong Python/PySpark
   support, event time + watermarks + checkpointing built in, portable to
   Azure Databricks.

## Decision

Use Spark Structured Streaming (PySpark) as the processing engine. Target Azure
Databricks as the managed runtime for cloud deployment; local Spark for
development.

## Rationale

- Aligns with the specialization (PySpark, Databricks).
- Event time, watermarks, stateful dedup, checkpointing are first-class.
- Same code runs locally and on Databricks.

## Consequences

- Single-node local Spark is not production scale; documented as a limitation.
- Micro-batch latency (trigger interval) is the floor for end-to-end latency.

## Trade-offs

- Heavier than Kafka Streams for simple cases, but necessary for the
  distributed-processing demonstration.