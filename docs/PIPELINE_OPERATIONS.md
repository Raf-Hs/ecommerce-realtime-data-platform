# Pipeline Operations

**Project:** E-commerce Real-Time Intelligence & Event Streaming Platform

## Start

```bash
docker compose up -d
python scripts/create_topics.py
```

## Replay historical data

```bash
python -m src.producers.replay  # (CLI TBD)
```

Replay speed, batch size, and delays are controlled via environment variables
(see `.env.example`).

## Run Spark streaming

```bash
export JAVA_HOME=~/jdk/jdk-17.0.13+11
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.13:4.2.0,io.delta:delta-spark_4.2_2.13:4.4.1 \
    src/streaming/spark_streaming.py
```

## Run Gold aggregation

```bash
python scripts/run_gold_aggregation.py
```

## Stop

```bash
docker compose down
```

## Recovery

See `docs/FAILURE_RECOVERY.md`.