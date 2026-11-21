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

GitHub Actions: lint (ruff), type check (mypy optional), pytest. Added in Phase 7.

## 4. Status

Designed (not implemented). First tests in Phase 2 (ingestion).