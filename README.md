# E-commerce Real-Time Intelligence & Event Streaming Platform

> Status: **Phase 0 — Research & Architecture (in progress).** No application code yet.

## Overview

NovaCart is a fictional mid-sized online marketplace. Its data is fragmented across
independent systems (clickstream, transactions, catalog, inventory) and its reporting
is batch-only, so it cannot see customer behavior or operational changes in time.

This project builds a **local, reproducible, event-driven data platform** that
integrates multiple independent sources through Apache Kafka, processes them with
Apache Spark Structured Streaming, enforces data quality, persists a three-layer
(Bronze/Silver/Gold) Parquet Data Lake, and serves business-ready metrics through
PostgreSQL.

## Data sources

1. **Retailrocket E-commerce Dataset** (CC BY-NC-SA 4.0) — clickstream + item
   properties + category tree.
2. **Olist Brazilian E-commerce Dataset** (CC BY-NC-SA 4.0) — transactions,
   payments, logistics, reviews, sellers.
3. **Instacart Market Basket Analysis** (license to verify) — product catalog
   enrichment; fallback: UCI Online Retail II (CC BY 4.0).
4. **Synthetic operational events** — inventory, checkout, payment, price changes
   (explicitly labeled, never presented as real).

Retailrocket and Olist are independent datasets. Their identifiers are never joined.

## Tech stack (planned)

**Local implementation:** Python, SQL, PostgreSQL, Apache Kafka, Apache Spark /
PySpark, Delta Lake, Docker Compose, pytest, GitHub Actions.

**Azure target architecture (designed, not implemented):** Azure Databricks,
ADLS Gen2, Azure Monitor, Azure Data Factory (batch orchestration only).

Local-first, free, open source. Azure items are target architecture only — no paid
resources are created.

## Documentation

- [Business case](docs/business/BUSINESS_CASE.md)
- [Data sources](docs/data-sources/DATA_SOURCES.md)
- [Architecture](docs/architecture/ARCHITECTURE.md)
- [Phase 0 research](docs/PHASE_0_RESEARCH.md)
- [Engineering gap analysis](docs/ENGINEERING_GAP_ANALYSIS.md)
- [Project status](docs/PROJECT_STATUS.md)
- [Data quality](docs/data-quality/DATA_QUALITY.md)
- [Testing strategy](docs/testing/TESTING_STRATEGY.md)
- [Contributing](docs/CONTRIBUTING.md)
- [Decisions (ADRs)](docs/decisions/)

## License

Project code: to be decided (likely MIT/Apache-2.0). Datasets retain their own
licenses; see `docs/data-sources/DATA_SOURCES.md`.

## Status

Phase 0 complete. Awaiting approval before implementation.