# E-commerce Real-Time Intelligence & Event Streaming Platform

> Status: **Implementation complete through Milestone 3 (E2E streaming validated).**
> 31 automated tests passing. GitHub synchronized.

## Overview

NovaCart is a fictional mid-sized online marketplace. Its data is fragmented across
independent systems (clickstream, transactions, catalog, inventory) and its reporting
is batch-only, so it cannot see customer behavior or operational changes in time.

This project builds a **local, reproducible, event-driven data platform** that
integrates multiple independent sources (Retailrocket, Olist, UCI Online Retail II,
synthetic) through Apache Kafka, processes them with Apache Spark Structured
Streaming, enforces data quality, persists a three-layer (Bronze/Silver/Gold)
Delta Lake, and serves business-ready metrics through PostgreSQL.

## Data sources

1. **Retailrocket E-commerce Dataset** (CC BY-NC-SA 4.0) — clickstream + item
   properties + category tree.
2. **Olist Brazilian E-commerce Dataset** (CC BY-NC-SA 4.0) — transactions,
   payments, logistics, reviews, sellers.
3. **UCI Online Retail II** (CC BY 4.0) — UK retail transactions, product catalog.
4. **Synthetic operational events** — inventory, checkout, payment, price changes
   (explicitly labeled, never presented as real).

Retailrocket and Olist are independent datasets. Their identifiers are never joined.

## Tech stack

**Local implementation:** Python, SQL, PostgreSQL, Apache Kafka, Apache Spark /
PySpark, Delta Lake, Docker Compose, pytest, GitHub Actions.

**Azure target architecture (designed, not implemented):** Azure Databricks,
ADLS Gen2, Azure Monitor, Azure Data Factory (batch orchestration only).

Local-first, free, open source. Azure items are target architecture only — no paid
resources are created.

## Validation

End-to-end streaming validation passed:
- Bronze: 241 rows (raw Kafka events)
- Silver: 81 rows (deduplicated canonical events)
- Gold: 5 rows (product engagement per product)

Run: `python scripts/e2e_streaming_test.py`

## Quick start

```bash
# 1. Clone and set up Python
git clone https://github.com/Raf-Hs/ecommerce-realtime-data-platform.git
cd ecommerce-realtime-data-platform
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# 2. Start infrastructure
docker compose up -d

# 3. Create Kafka topics
python scripts/create_topics.py

# 4. Validate connectivity
python scripts/kafka_smoke_test.py
python scripts/postgres_smoke_test.py

# 5. Run unit tests
python -m pytest tests/unit -q
```

Java 17+ is required for Spark. See `infrastructure/spark/README.md`.

## Documentation

- [Business case](docs/business/BUSINESS_CASE.md)
- [Data sources](docs/data-sources/DATA_SOURCES.md)
- [Data dictionary](docs/data-dictionary/DATA_DICTIONARY.md)
- [Event catalog](docs/event-schemas/EVENT_CATALOG.md)
- [Architecture](docs/architecture/ARCHITECTURE.md)
- [Azure alignment](docs/architecture/AZURE_ALIGNMENT.md)
- [Phase 0 research](docs/PHASE_0_RESEARCH.md)
- [Engineering gap analysis](docs/ENGINEERING_GAP_ANALYSIS.md)
- [Implementation inventory](docs/IMPLEMENTATION_INVENTORY.md)
- [Project status](docs/PROJECT_STATUS.md)
- [Data quality](docs/data-quality/DATA_QUALITY.md)
- [Testing strategy](docs/testing/TESTING_STRATEGY.md)
- [Monitoring](docs/MONITORING.md)
- [E2E validation](docs/E2E_VALIDATION.md)
- [Pipeline operations](docs/PIPELINE_OPERATIONS.md)
- [Failure recovery](docs/FAILURE_RECOVERY.md)
- [Limitations](docs/LIMITATIONS.md)
- [Performance benchmarks](docs/benchmarks/PERFORMANCE_BENCHMARKS.md)
- [Contributing](docs/CONTRIBUTING.md)
- [Decisions (ADRs)](docs/decisions/)

## License

Project code: to be decided (likely MIT/Apache-2.0). Datasets retain their own
licenses; see `docs/data-sources/DATA_SOURCES.md`.

## Status

Implementation complete through Milestone 3. E2E streaming validated.
31 automated tests passing. See `docs/PROJECT_STATUS.md`.