# End-to-End Streaming Validation

**Project:** E-commerce Real-Time Intelligence & Event Streaming Platform

## Pipeline

```
Event Producer -> Kafka -> Spark Structured Streaming -> Bronze (Delta) -> Silver (Delta) -> Gold (Delta) -> PostgreSQL
```

## Reproducible execution

```bash
# 1. Start infrastructure
docker compose up -d
python scripts/create_topics.py

# 2. Run end-to-end validation
python scripts/e2e_streaming_test.py
```

The script seeds 30 canonical events into `clickstream-events`, runs the Spark
streaming job with `availableNow` trigger, and verifies Bronze, Silver, and Gold.

## Measured results (local environment)

| Layer | Rows | Notes |
|---|---|---|
| Bronze (raw) | 241 | Includes accumulated messages from prior runs; append-only |
| Silver (validated, deduped) | 81 | Deduplicated by event_id; 30 new seeded events included |
| Gold (product engagement) | 5 | Per-product views, cart additions, view-to-cart ratio |

## Streaming semantics

- **Watermark:** 10 minutes (configurable via `WATERMARK_DELAY`).
- **Window:** 1 hour tumbling (configurable via `GOLD_WINDOW`).
- **Deduplication:** by `event_id` within watermark window.
- **Checkpoint:** per-sink paths under `SPARK_CHECKPOINT_PATH`.

## Gold streaming behavior

The continuous Gold streaming job (`src/streaming/gold_streaming.py`) uses
event-time windowed aggregation with a watermark. A window is emitted only when
the watermark exceeds the window end time. With a single micro-batch, the
watermark does not advance beyond the first batch's max event time, so windows
may not emit until a subsequent micro-batch. This is standard Spark Structured
Streaming behavior and is documented here rather than worked around.

The batch Gold path (`compute_product_engagement`) produces equivalent results
and is used for validation. Both paths share the same aggregation logic.

## Recovery behavior

- Spark checkpointing enables restart from the last committed offset.
- Re-running with `availableNow` trigger processes only new (uncommitted) data.
- Idempotent sinks (Delta append with dedup) prevent duplicate rows on replay.

## Remaining limitations

- Gold streaming requires a second micro-batch to emit windows (watermark semantics).
- Single-node execution; not representative of production scale.
- No late-arriving event test beyond watermark configuration.