# ADR-007: Data Lake Storage Format

## Status

Accepted (Phase 0)

## Context

Bronze/Silver/Gold layers need a storage format. The specialization targets
Delta Lake on Azure Databricks + ADLS Gen2.

## Problem

Parquet vs. Delta Lake vs. Apache Iceberg?

## Options considered

1. Raw Parquet only. Rejected: no ACID, no schema enforcement, no time travel;
   harder to demonstrate reliability.
2. Apache Iceberg. Rejected for now: less direct fit with the Databricks
   specialization; revisit if needed.
3. Delta Lake (Parquet + transaction log). Accepted: ACID, schema enforcement,
   time travel, open source, runs locally via `delta-spark`, native on
   Databricks + ADLS Gen2.

## Decision

Use Delta Lake for all three layers, running locally via `delta-spark`. Underlying
files are Parquet. Port to ADLS Gen2 + Databricks without code change.

## Rationale

- Aligns with the Azure Databricks specialization.
- Demonstrates ACID, schema enforcement, time travel — credibility for
  reliability claims.
- Local-first, free, open source.

## Consequences

- Adds a dependency (`delta-spark`) and Spark version constraints.
- Local filesystem is not as durable as cloud storage; documented as a limitation.

## Trade-offs

- More complexity than raw Parquet, justified by the reliability and Azure
  alignment benefits.