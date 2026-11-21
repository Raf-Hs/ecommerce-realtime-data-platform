# Kafka Infrastructure

## Components

- **Kafka broker (KRaft mode, no ZooKeeper):** `apache/kafka:3.9.0`, single node.
- **PostgreSQL 16:** serving layer.
- **Kafka UI (optional, profile `ui`):** `provectuslabs/kafka-ui`.

## Start

```bash
docker compose up -d
docker compose ps
```

## Create topics

```bash
.venv/bin/python scripts/create_topics.py
```

## Smoke tests

```bash
.venv/bin/python scripts/kafka_smoke_test.py
.venv/bin/python scripts/postgres_smoke_test.py
```

## Kafka UI (optional)

```bash
docker compose --profile ui up -d
# open http://localhost:8080
```

## Stop

```bash
docker compose down          # keep volumes
docker compose down -v       # remove volumes (destructive)
```

## Notes

- Kafka advertised to host as `localhost:9092`; internal (container) as `kafka:29092`.
- Postgres host port is `5433` to avoid clashing with any existing local Postgres.
- Topics are auto-created on first produce, but `create_topics.py` creates them with
  the intended partition counts.