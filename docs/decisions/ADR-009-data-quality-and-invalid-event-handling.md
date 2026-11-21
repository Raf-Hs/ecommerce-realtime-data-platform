# ADR-009: Data Quality and Invalid Event Handling

## Status

Accepted (Phase 0)

## Context

Data quality is a central concern. Invalid records must never be silently
dropped.

## Problem

How to validate events and handle invalid ones?

## Options considered

1. Drop invalid records. Rejected: violates the "never silently discard" rule.
2. Fail the whole batch on any invalid record. Rejected: too brittle; one bad
   record stalls the pipeline.
3. Validate at boundaries; route invalid records to `invalid-events` topic and
   DLQ; track counters. Accepted.

## Decision

Validate at ingestion and Spark boundaries. Route schema-invalid records to
`invalid-events`; route unprocessable/poison records to `dead-letter-events`.
Track per-batch counters (total, valid, invalid, rejected, duplicates) in logs and
Gold `dq_metrics`. Preserve source payload and provenance for investigation.

## Rationale

- No silent data loss.
- Pipeline continues past bad records.
- Full auditability.

## Consequences

- Invalid-events topic and DLQ require retention and monitoring.
- Validation rules must be kept in sync with schemas.

## Trade-offs

- More topics and storage, justified by reliability and auditability.