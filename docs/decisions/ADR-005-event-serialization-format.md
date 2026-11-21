# ADR-005: Event Serialization Format

## Status

Accepted (Phase 0)

## Context

Events must be serialized for Kafka transport and storage.

## Problem

JSON vs. Avro (with Schema Registry) for Kafka messages?

## Options considered

1. Avro + Schema Registry from the start. Rejected for initial scope: adds
   infrastructure (Schema Registry) and complexity before the pipeline exists.
2. JSON with a documented schema (JSON Schema files in `schemas/`). Accepted for
   Phase 1–4.
3. Protobuf. Rejected: no clear advantage over Avro/JSON here.

## Decision

Start with JSON, validated against JSON Schema files stored in `schemas/`. Revisit
Avro + Schema Registry in Phase 6 if schema evolution or size becomes a problem.
Document the migration path.

## Rationale

- Faster to implement and debug during development.
- Human-readable, easy to inspect in Kafka.
- Schema files still provide a contract.

## Consequences

- Larger message sizes than Avro.
- Schema enforcement is application-side, not broker-side.
- Migration to Avro later requires producer/consumer updates.

## Trade-offs

- Simplicity now vs. stricter contracts later; revisit with measurement.