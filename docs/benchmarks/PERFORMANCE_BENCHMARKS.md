# Performance Benchmarks

**Project:** E-commerce Real-Time Intelligence & Event Streaming Platform

All figures are measured on the local development environment described below.
No figures are fabricated.

## Environment

- OS: Ubuntu (WSL2) on Windows
- CPU: (host machine)
- Kafka: Apache Kafka 3.9.0, single node, KRaft mode
- Python: 3.14 (venv)
- Client: kafka-python 3.0.13, acks=all, idempotent producer

## Producer throughput

| Run | Events | Sent | Failed | Elapsed (s) | Events/sec |
|---|---|---|---|---|---|
| 1 | 5000 | 5000 | 0 | 3.897 | 1283.0 |

Measured via `scripts/benchmark_producer.py` using synthetic inventory events
published to `novacart-bench-test` with replay_speed=1000, batch_size=500.

## Notes

- Throughput is limited by per-message Kafka round-trips and acks=all.
- Single-node, local environment only; not representative of production scale.
- Spark-side throughput and end-to-end latency are not yet measured (Phase 6).