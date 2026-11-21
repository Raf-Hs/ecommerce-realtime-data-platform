# Engineering Gap Analysis

**Project:** E-commerce Real-Time Intelligence & Event Streaming Platform
**Date:** 2026-11-21
**Basis:** Actual repository contents (no assumptions).

## 1. Repository assessment (actual state)

The repository contains documentation only. There is no application code, no
infrastructure configuration, no tests, and no Git history.

| Path | Type | Notes |
|---|---|---|
| `README.md` | Doc | High-level overview; references forthcoming docs |
| `docs/PHASE_0_RESEARCH.md` | Doc | Full Phase 0 research (A–J) |
| `docs/decisions/ADR-001-*.md` | Doc | Multi-source integration strategy |
| `docs/decisions/ADR-002-*.md` | Doc | Historical replay architecture |
| `docs/decisions/ADR-003-*.md` | Doc | Kafka topic organization |
| `docs/decisions/ADR-010-*.md` | Doc | Local infrastructure architecture |

**Not present (verified by inspection):** source code, Docker Compose, tests, CI
workflows, data files, schemas, assets, `.gitignore`, `.env.example`,
`requirements.txt`, Git repository.

## 2. Gap analysis against engineering standards

| Area | Current State | Required Improvement | Priority |
|---|---|---|---|
| Business story | Drafted in Phase 0 doc; not yet a standalone business case | Create `docs/business/BUSINESS_CASE.md` with full narrative; add visual flow | High |
| Data sources | Researched and documented in Phase 0 doc | Split into `docs/data-sources/DATA_SOURCES.md`; add schema diagrams | High |
| Architecture | Text diagram only; no Mermaid visuals; no Azure/Delta alignment | Create `docs/architecture/ARCHITECTURE.md` with Mermaid diagrams and Azure alignment section | High |
| Kafka | Designed (ADR-003) but not implemented | Implement in Phase 3; add producer/consumer tests | Medium (deferred) |
| Spark | Designed but not implemented | Implement in Phase 4; align with PySpark/Databricks | Medium (deferred) |
| Azure alignment | Not addressed | Add Azure target architecture (Databricks, Delta, ADLS Gen2, Monitor) as designed/proposed; document local vs. cloud status | High |
| Data Lakehouse | Parquet proposed | Decide on Delta Lake (ADR-007); document local vs. Azure | High |
| Documentation | Partial; no visual assets; no project status tracker | Add Mermaid diagrams, `docs/PROJECT_STATUS.md`, full doc set | High |
| Visual assets | None | Create `docs/assets/` with Mermaid-rendered diagrams | Medium |
| Testing | None | Define strategy doc; implement in later phases | Medium (deferred) |
| Reliability | Designed (DLQ, retries) but not implemented | Implement in Phase 3–4 | Medium (deferred) |
| Multi-source integration | Strategy defined (ADR-001) | Keep; reinforce with schema-level enforcement plan | Medium |
| Code organization | No code yet | Establish `src/`, `tests/`, `schemas/`, `scripts/` skeleton | High |
| Configuration | None | Add `.env.example`, `.gitignore`, `requirements.txt` | High |
| CI/CD | None | Add GitHub Actions workflow in Phase 7 | Low (deferred) |
| Project tracking | None | Add `docs/PROJECT_STATUS.md` | High |

## 3. Azure and Lakehouse alignment assessment

The project currently targets a local stack (Kafka, Spark, Parquet, Postgres). The
shared engineering standards require alignment with **Azure Databricks, PySpark,
Delta Lake, ADLS Gen2, Azure Monitor, and (where justified) Azure Data Factory**.

**Decision:** Do not deploy paid Azure resources now. Instead:

- Adopt **Delta Lake** as the storage format (open source, runs locally via
  `delta-spark`), which is the same format used on Databricks + ADLS Gen2. This
  makes the local implementation directly portable.
- Target **Azure Databricks** as the managed Spark runtime for cloud deployment;
  local Spark remains the development runtime.
- Target **ADLS Gen2** as the cloud storage backend; local filesystem is the
  development backend.
- Target **Azure Monitor** for observability in cloud deployments; local monitoring
  uses Spark UI + Kafka UI + structured logs.
- **Azure Data Factory** is not required for this project's streaming focus; it is
  documented as an optional orchestration layer for batch ingestion only.

Status labels used throughout docs: `Implemented (local)`, `Designed (not
implemented)`, `Proposed (future)`.

## 4. Unnecessary complexity identified

- None yet (no code). The design intentionally excludes Iceberg, Flink, and cloud
  services to keep scope honest. This is retained.

## 5. Prioritized implementation order

1. Documentation and visual foundation (architecture, business case, data sources,
   project status, ADRs 004–009).
2. Repository skeleton and configuration files (`.gitignore`, `.env.example`,
   `requirements.txt`, directory structure).
3. Phase 1 infrastructure (Docker Compose) — requires Docker; to be done next with
   user approval.
4. Subsequent phases per roadmap.

## 6. What this analysis does not change

- The business scope and multi-source strategy (ADR-001) are retained.
- The "no fabricated joins" rule is retained and strengthened.
- Phase 0 research conclusions are retained.