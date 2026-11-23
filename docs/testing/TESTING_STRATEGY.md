# Testing Strategy

**Project:** E-commerce Real-Time Intelligence & Event Streaming Platform

## 1. Test levels

- **Unit tests:** adapters, normalizers, validators, event ID generation,
  synthetic generators. (pytest)
- **Integration tests:** Kafka produce/consume round-trip, Spark transformations
  on small fixtures, Delta read/write.
- **Data quality tests:** null rates, uniqueness, referential integrity within a
  source, schema conformance.
- **Reliability tests:** duplicate handling, late events, consumer restart,
  checkpoint recovery, DLQ routing.

## 2. Fixtures

Small, deterministic sample datasets under `tests/fixtures/` (never commit full
datasets). Replay speed set to "as fast as possible" in tests.

## 3. CI

GitHub Actions workflow at `.github/workflows/ci.yml` runs unit tests on push/PR.

## 4. Test inventory (actual)

- **Unit tests (15):** event ID determinism, Retailrocket adapter, Olist adapter,
  UCI adapter, event validator, synthetic generator, replay producer.
- **Integration tests (8):** Kafka round-trip, DLQ routing, Gold aggregation,
  Spark smoke, E2E streaming.
- **Reliability tests (2):** dedup by event_id, late-arriving events.
- **Total: 31 tests, all passing.**

## 5. Status

Implemented. 31 tests passing. CI workflow committed (push requires `workflow` scope).