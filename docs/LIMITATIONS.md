# Limitations

**Project:** E-commerce Real-Time Intelligence & Event Streaming Platform

## Data

- Retailrocket values are hashed (opaque product/visitor IDs).
- ~10% of Retailrocket events lack item properties.
- Olist has no clickstream; customer_id is per-order.
- Sources are independent: no cross-source joins; cross-source analysis is
  side-by-side only.
- Synthetic data is simulated and never presented as real.

## Processing

- Single-node Spark; not production scale.
- Micro-batch latency is the floor for end-to-end latency.
- Event-time watermarks may drop very late events.
- Checkpoint recovery requires the checkpoint path to be intact.

## Infrastructure

- Local only; no cloud deployment (Azure is target architecture, not implemented).
- No paid resources; no production-grade auth/secrets management.
- Kafka retention is local-disk limited.

## Metrics

- No cross-source conversion rates.
- No margin/profitability (no cost data).
- Benchmarks are local single-node only.