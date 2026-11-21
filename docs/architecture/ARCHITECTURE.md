# Architecture

**Project:** E-commerce Real-Time Intelligence & Event Streaming Platform

## 1. Overview

NovaCart's platform is a local-first, event-driven data platform. It ingests events
from multiple independent sources through Apache Kafka, processes them with Apache
Spark Structured Streaming, enforces data quality, persists a three-layer
(Bronze/Silver/Gold) Delta Lake, and serves business-ready metrics through
PostgreSQL. The design is portable to Azure (Databricks + ADLS Gen2) without
structural change.

Status legend used throughout:
- **Implemented (local)** — running code/config in the repo.
- **Designed** — specified, not yet implemented.
- **Proposed** — future, not committed.

## 2. System architecture

```mermaid
flowchart LR
    subgraph SOURCES["Data Sources"]
        A[Retailrocket<br/>clickstream + item props]
        B[Olist<br/>transactions + ops]
        C[Instacart / UCI<br/>product catalog]
        D[Synthetic<br/>operational events]
    end

    subgraph INGEST["Ingestion & Adapters (Python)"]
        E[CSV readers]
        F[Source normalizers]
        G[Replay producers]
        H[Synthetic generators]
    end

    subgraph KAFKA["Apache Kafka"]
        T1[clickstream-events]
        T2[transaction-events]
        T3[product-events]
        T4[inventory-events]
        T5[invalid-events]
        T6[dead-letter-events]
    end

    subgraph SPARK["Spark Structured Streaming"]
        P1[Parse + validate]
        P2[Normalize]
        P3[Deduplicate]
        P4[Event time + watermarks]
        P5[Windowed aggregates]
    end

    subgraph LAKE["Delta Lake (local)"]
        BR[Bronze<br/>raw events]
        SI[Silver<br/>validated events]
        GO[Gold<br/>business aggregates]
    end

    subgraph SERVE["Consumption"]
        PG[(PostgreSQL)]
        MON[Monitoring<br/>Spark UI / Kafka UI / logs]
    end

    A & B & C & D --> E --> F --> G & H
    G & H --> KAFKA
    KAFKA --> P1 --> P2 --> P3 --> P4 --> P5
    P1 -. invalid .-> T5
    P1 -. poison .-> T6
    P2 --> BR
    P3 --> SI
    P5 --> GO
    GO --> PG
    SPARK -. metrics .-> MON
```

## 3. Data flow

```mermaid
sequenceDiagram
    participant Src as Source file
    participant Adp as Adapter
    participant Prd as Replay producer
    participant K as Kafka
    participant Sp as Spark
    participant L as Delta Lake
    participant Pg as PostgreSQL

    Src->>Adp: read rows
    Adp->>Adp: validate + normalize to canonical envelope
    Adp->>Prd: canonical events
    Prd->>K: publish (key=entity id, event_time preserved, ingestion_time=now)
    K->>Sp: consume batch
    Sp->>Sp: parse JSON, validate schema
    Sp->>L: write Bronze (raw)
    Sp->>Sp: dedup by event_id (stateful + watermark)
    Sp->>L: write Silver (validated)
    Sp->>Sp: windowed aggregates
    Sp->>L: write Gold (aggregates)
    Sp->>Pg: upsert Gold serving tables
```

## 4. Canonical data model

```mermaid
erDiagram
    CANONICAL_EVENT {
        string event_id PK
        string event_type
        timestamp event_time
        timestamp ingestion_time
        string source
        string source_event_id
        string entity_type
        string entity_id
        json payload
        string schema_version
        json provenance
    }
    BRONZE_RAW {
        string kafka_topic
        int kafka_partition
        bigint kafka_offset
        string raw_payload
        timestamp ingestion_time
    }
    SILVER_EVENT {
        string event_id PK
        string event_type
        timestamp event_time
        string source
        string entity_id
    }
    GOLD_PRODUCT_ENGAGEMENT {
        string product_id
        timestamp window_start
        bigint views
        bigint cart_additions
        double view_to_cart_ratio
    }
    BRONZE_RAW ||--o{ SILVER_EVENT : "validate & normalize"
    SILVER_EVENT ||--o{ GOLD_PRODUCT_ENGAGEMENT : "aggregate"
```

Identifiers are source-prefixed (`rr:`, `olist:`, `syn:`) and are never joined
across sources.

## 5. Kafka topic strategy

| Topic | Domain | Key | Partitions (initial) | Retention |
|---|---|---|---|---|
| `clickstream-events` | Retailrocket behavior | `itemid` | 6 | 7 days |
| `transaction-events` | Olist orders/payments | `order_id` | 6 | 14 days |
| `product-events` | Catalog updates | `product_id` | 3 | 14 days |
| `inventory-events` | Synthetic stock | `product_id` | 3 | 7 days |
| `invalid-events` | Schema-invalid | `source` | 3 | 30 days |
| `dead-letter-events` | Poison messages | `source` | 3 | 30 days |

## 6. Data Lakehouse layers (Delta Lake)

```mermaid
flowchart TD
    B[Bronze<br/>raw Kafka payloads + ingestion metadata<br/>append-only] --> S[Silver<br/>validated, normalized, deduplicated<br/>canonical events]
    S --> G[Gold<br/>business aggregates + DQ metrics]
    G --> PG[(PostgreSQL<br/>serving)]
```

- **Format:** Delta Lake (open source; Parquet + transaction log). Runs locally via
  `delta-spark`; designed to port to ADLS Gen2 + Databricks without code change.
- **Partitioning:** by `source` and date.
- **Schema evolution:** supported by Delta; controlled via schema version field.

## 7. Azure alignment (designed, not implemented)

| Layer | Local (implemented/planned) | Azure target (designed) | Status |
|---|---|---|---|
| Processing runtime | Apache Spark (local) | Azure Databricks | Designed |
| Storage | Delta Lake on local FS | ADLS Gen2 + Delta | Designed |
| Orchestration | Docker Compose + scripts | Azure Data Factory (batch only) | Proposed |
| Monitoring | Spark UI, Kafka UI, logs | Azure Monitor | Designed |
| Secrets | `.env` (local) | Azure Key Vault | Proposed |

No paid Azure resources are created. All Azure items are documented as target
architecture only.

## 8. Monitoring strategy

- **Kafka:** broker health, topic/partition counts, consumer group lag.
- **Spark:** query progress, batch duration, input/processed rows per second,
  state store size, watermark.
- **Application:** structured JSON logs with event counts, validation failures,
  DLQ counts, throughput, latency.
- **Data quality:** per-batch counters persisted to Gold (`dq_metrics`) and logs.

## 9. Technology stack

See `docs/PHASE_0_RESEARCH.md` section F and `README.md`. Core: Python, SQL,
PostgreSQL, Kafka, Spark/PySpark, Delta Lake, Docker Compose, pytest, GitHub
Actions. Azure components are target architecture only.