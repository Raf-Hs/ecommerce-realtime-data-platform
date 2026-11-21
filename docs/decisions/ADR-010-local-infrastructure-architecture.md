# ADR-010: Local Infrastructure Architecture

## Status

Accepted (Phase 0)

## Context

The project must run locally on Ubuntu via WSL2, be reproducible, and avoid paid
cloud services.

## Problem

How to provide Kafka, Spark, and PostgreSQL locally with minimal friction?

## Options considered

1. **Manual native installs.** Fragile, environment-specific, hard to reproduce.
2. **Kubernetes / Helm.** Over-engineered for a single developer laptop.
3. **Docker Compose.** Declarative, reproducible, isolated, well-supported by
   Kafka and Postgres images. Accepted.

## Decision

Use Docker Compose for Kafka (and ZooKeeper or KRaft), PostgreSQL, and any
lightweight UI. Run Python/Spark on the host (or in a container if needed) against
the Compose network. Pin image versions. Document resource requirements.

## Rationale

- Reproducible by a third party with one command.
- Isolates infrastructure from the host Python environment.
- Aligns with the stated environment (Docker Desktop + WSL2).

## Consequences

- Single-node only; not representative of production scale (documented).
- Resource limits on WSL2 must be respected; sample data sizes tuned accordingly.
- Kafka image choice (Confluent vs. Bitnami vs. Apache) to be finalized in Phase 1.

## Implementation (Phase 1)

- Kafka: `apache/kafka:3.9.0` in KRaft mode (no ZooKeeper), single node,
  internal listener on `kafka:29092`.
- PostgreSQL: `postgres:16`, host port `5433`.
- Optional Kafka UI via `docker compose --profile ui`.

## Trade-offs

- Docker adds a dependency, but removes far larger manual-setup risk.