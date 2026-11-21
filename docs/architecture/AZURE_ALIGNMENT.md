# Azure Alignment (Target Architecture)

**Project:** E-commerce Real-Time Intelligence & Event Streaming Platform

Status: **Designed, not implemented.** No paid Azure resources are created.

## Service mapping

| Local component | Azure target | Responsibility |
|---|---|---|
| Apache Spark (local) | Azure Databricks | Managed Spark runtime for streaming + batch |
| Delta Lake (local FS) | ADLS Gen2 + Delta | Cloud storage with ACID, time travel |
| Kafka (Docker) | Azure Event Hubs (Kafka API) or self-managed Kafka on AKS | Event backbone (optional) |
| PostgreSQL (Docker) | Azure Database for PostgreSQL | Serving layer |
| Structured logs | Azure Monitor / Log Analytics | Observability |
| Docker Compose | Azure Data Factory (batch orchestration) | Optional batch ingestion orchestration |
| Secrets (.env) | Azure Key Vault | Secret management |

## Data flow (Azure)

```
Sources → ADF (batch ingestion) / Kafka (streaming)
  → Azure Databricks (PySpark Structured Streaming)
  → ADLS Gen2 (Bronze / Silver / Gold Delta)
  → Azure Database for PostgreSQL (serving)
  → Azure Monitor (metrics, alerts)
```

## Migration strategy (local → Azure)

1. Replace local filesystem paths with `abfss://` ADLS Gen2 paths.
2. Run the same PySpark code on a Databricks cluster (no code change needed).
3. Move secrets from `.env` to Key Vault; reference via Databricks secret scopes.
4. Replace local Postgres with Azure Database for PostgreSQL.
5. Configure Azure Monitor for Spark metrics and alerts.
6. (Optional) Use ADF for scheduled batch ingestion of historical datasets.

## Authentication & security

- Service principals or managed identities for Databricks → ADLS Gen2.
- Key Vault for credentials; no secrets in code.
- Network: VNet injection for Databricks; private endpoints for storage and DB.

## Cost considerations

- Databricks: pay-per-DBU; use autoscaling and spot instances for dev.
- ADLS Gen2: pay per storage + transactions; lifecycle policies for old data.
- Azure Monitor: pay per ingestion volume.
- No resources created in this project; all are target architecture.

## What stays local

- Kafka (Docker) may remain self-managed for cost control.
- Development and testing stay local; cloud is for production-grade runs.