# Data Quality

**Project:** E-commerce Real-Time Intelligence & Event Streaming Platform

## 1. Principle

Invalid records are never silently discarded. Every record is either accepted into
Silver or routed to `invalid-events` / `dead-letter-events`, with counters tracked.

## 2. Validation boundaries

1. **Ingestion (Python adapters):** file existence, column presence, type
   coercion, null checks on required identifiers, timestamp parseability.
2. **Kafka producer:** payload serialization, required envelope fields.
3. **Spark (parsing):** JSON schema conformance, required fields, valid event
   types, valid timestamps, source-prefixed IDs.
4. **Spark (business):** duplicate detection by `event_id`, unknown source
   rejection, late-arrival handling.

## 3. Metrics (per batch)

- `total_events`
- `valid_events`
- `invalid_events`
- `rejected_events`
- `duplicate_candidates`
- `processing_failures`
- `events_per_second`
- `processing_latency_ms` (event_time → sink_time)
- `late_arriving_events`

Persisted to Gold `dq_metrics` table and structured logs.

## 4. DLQ policy

- `invalid-events`: schema-invalid but recoverable records (retain 30 days).
- `dead-letter-events`: unprocessable/poison records (retain 30 days).
- Both preserve original payload + provenance + rejection reason.

## 5. Status

Designed (not implemented). Implementation in Phases 3–4.