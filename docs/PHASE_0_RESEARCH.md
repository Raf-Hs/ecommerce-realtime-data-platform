# Phase 0 — Business Research and Architecture

**Project:** E-commerce Real-Time Intelligence & Event Streaming Platform
**Phase:** 0 — Business Research & Architecture
**Status:** Research complete — awaiting approval before implementation
**Language of all repository artifacts:** English

This document captures the Phase 0 research, source evaluation, integration feasibility,
business metrics, architecture proposal, technology evaluation, roadmap, risks, and
documentation plan. It is the single source of truth for the decisions made before any
code is written. No application code, Kafka deployment, or repository scaffolding
beyond this document and the README exists yet.

---

## A. Business Story

### The company

We work with a fictional company called **NovaCart**, a mid-sized online marketplace
selling consumer goods across multiple categories (electronics, home & living, fashion,
sports, and everyday essentials). NovaCart operates a single storefront website, a
mobile web experience, and a small network of third-party sellers that list products on
the marketplace. Customers browse, search, add items to carts, and place orders. Sellers
manage their own inventory and fulfill orders.

NovaCart is fictional, but its problems are realistic and common in mid-market
e-commerce.

### Current state and pain points

1. **Fragmented data.** Customer behavior (clicks, views, cart additions) lives in the
   web analytics pipeline. Orders and payments live in the transactional order
   management system. Product attributes and availability live in the catalog service.
   These systems were built independently and do not share identifiers or schemas.
2. **Batch reporting only.** The current reporting runs nightly. By the time a product
   surge, a stockout, or a drop in engagement is visible, the opportunity to react has
   passed.
3. **No unified view of demand.** The business cannot reliably answer "which products
   are getting attention but not converting to carts?" because behavior and transactions
   are not joined by a trusted key — and in reality they cannot be joined at all across
   the independent datasets we have.
4. **No data quality visibility.** Invalid, duplicate, or late events are silently
   dropped. There is no record of what was rejected or why.
5. **No replay or recovery.** If a consumer fails, there is no documented way to
   reprocess events or measure the impact.

### What NovaCart needs

A centralized, event-driven data platform that:

- Ingests events from multiple independent sources through a common event backbone.
- Processes events continuously with event-time semantics, watermarks, and
  deduplication.
- Enforces data quality at defined boundaries and never silently discards records.
- Persists raw, validated, and aggregated data in a layered Data Lake.
- Produces a small number of meaningful, well-defined business outputs.
- Is reproducible locally, observable, and recoverable.

### What this platform will NOT do

- It will not join Retailrocket visitor/product identifiers to Olist customer/product
  identifiers. They are independent datasets with no shared key.
- It will not compute cross-source conversion rates (e.g., "Retailrocket views → Olist
  purchases"). That would be a fabricated relationship.
- It will not present synthetic events as real observations.
- It will not promise exactly-once end-to-end processing without demonstrating it.

---

## B. Data Source Research

### Source A — Retailrocket E-commerce Dataset (mandatory)

- **URL:** https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset
- **License:** CC BY-NC-SA 4.0 (non-commercial, share-alike). Verified from the
  Kaggle dataset page metadata.
- **Purpose:** Primary historical clickstream and behavioral dataset.
- **Files:**
  - `events.csv`
  - `item_properties_part1.csv`
  - `item_properties_part2.csv`
  - `category_tree.csv`
- **Schema (verified from dataset documentation):**
  - `events.csv`: `visitorid`, `itemid`, `event`, `transactionid`, `timestamp`
    - `event` ∈ {`view`, `addtocart`, `transaction`}
  - `item_properties_part{1,2}.csv`: `timestamp`, `itemid`, `property`, `value`
    - Properties include `categoryid`, `available`, and hashed property names/values.
  - `category_tree.csv`: `categoryid`, `parentid`
- **Scale (published figures, to be re-verified against downloaded files):**
  - Events: 2,756,101 total — 2,664,312 views, 69,332 add to carts,
    22,457 transactions.
  - Unique visitors: 1,407,580.
  - Collection period: ~4.5 months.
  - Item properties: 20,275,902 rows describing 417,053 unique items.
  - Category tree: 1,669 rows.
- **Identifiers:** `visitorid` (visitor), `itemid` (product), `transactionid`
  (transaction, present on transaction events), `categoryid`.
- **Temporal information:** Event timestamps (Unix ms). Item properties are stored as a
  change log with per-property timestamps (weekly snapshots merged into change-log form).
- **Business value:** Core behavioral signal — what products get attention, cart
  additions, and transactions within a single storefront. Availability flag supports
  inventory-related analysis.
- **Limitations / data quality notes:**
  - All values except `categoryid` and `available` are hashed (confidentiality). Product
    names and brands are not recoverable.
  - ~90% of events have matching item properties; ~10% do not.
  - `transactionid` semantics are not fully documented; treat as an opaque transaction
    reference.
  - Timestamps are historical (2015-era dataset); replay will preserve original
    event time and add an ingestion time.
  - No customer demographics, no pricing in clear text, no seller dimension.
- **Integration role:** Source of truth for behavioral events and product availability
  within the Retailrocket domain.

### Source B — Olist Brazilian E-commerce Dataset (mandatory)

- **URL:** https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
- **License:** CC BY-NC-SA 4.0 (reported by Kaggle/community; verify on the data card
  before redistribution).
- **Purpose:** Real transactional and operational data from a Brazilian marketplace.
- **Files (9 CSVs):**
  - `olist_customers_dataset.csv`
  - `olist_orders_dataset.csv`
  - `olist_order_items_dataset.csv`
  - `olist_products_dataset.csv`
  - `olist_order_payments_dataset.csv`
  - `olist_order_reviews_dataset.csv`
  - `olist_sellers_dataset.csv`
  - `olist_geolocation_dataset.csv`
  - `product_category_name_translation.csv`
- **Schema (verified from community documentation):**
  - `customers`: `customer_id`, `customer_unique_id`, `customer_zip_code_prefix`,
    `customer_city`, `customer_state` (99,441 rows)
  - `orders`: `order_id`, `customer_id`, `order_status`, `order_purchase_timestamp`,
    `order_approved_at`, `order_delivered_carrier_date`,
    `order_delivered_customer_date`, `order_estimated_delivery_date` (99,441 rows)
  - `order_items`: `order_id`, `order_item_id`, `product_id`, `seller_id`,
    `shipping_limit_date`, `price`, `freight_value` (112,650 rows)
  - `products`: `product_id`, `product_category_name`, `product_name_lenght`,
    `product_description_lenght`, `product_photos_qty`, `product_weight_g`,
    `product_length_cm`, `product_height_cm`, `product_width_cm` (32,951 rows)
  - `payments`: `order_id`, `payment_sequential`, `payment_type`,
    `payment_installments`, `payment_value` (103,886 rows)
  - `reviews`: `review_id`, `order_id`, `review_score`, `review_comment_title`,
    `review_comment_message`, `review_creation_date`, `review_answer_timestamp`
    (99,224 rows)
  - `sellers`: `seller_id`, `seller_zip_code_prefix`, `seller_city`, `seller_state`
    (3,095 rows)
  - `geolocation`: `geolocation_zip_code_prefix`, `geolocation_lat`,
    `geolocation_lng`, `geolocation_city`, `geolocation_state`
  - `category_translation`: `product_category_name`,
    `product_category_name_english` (71 rows)
- **Scale:** ~100,000 orders, September 2016 – September 2018, multiple marketplaces
  in Brazil.
- **Identifiers:** `order_id`, `customer_id` / `customer_unique_id`, `product_id`,
  `seller_id`.
- **Temporal information:** Multiple timestamps per order (purchase, approval, carrier
  handoff, customer delivery, estimated delivery); review creation/answer timestamps.
- **Business value:** Real operational lifecycle — order status, payments, logistics,
  reviews, seller geography. Strong source for transaction activity and fulfillment
  monitoring.
- **Limitations / data quality notes:**
  - No clickstream or browsing data; only completed/near-completed commerce.
  - `customer_id` is per-order (a customer can have multiple `customer_id` values);
    `customer_unique_id` is the stable person key.
  - Missing values in product dimensions and reviews are common.
  - Geolocation table has duplicate zip prefixes.
  - Portuguese category names require the translation table.
  - Order status values include `canceled`, `unavailable`, etc.
- **Integration role:** Source of truth for transactional and operational events.

### Source C — Proposed additional product catalog source

Two candidates were investigated. The recommendation is to use **one** of them; both are
documented so the choice is explicit.

**Candidate C1 — Instacart Market Basket Analysis (recommended for product taxonomy)**

- **URL:** https://www.kaggle.com/datasets/psparks/instacart-market-basket-analysis
  (alternative mirror: https://www.kaggle.com/datasets/yasserh/instacart-online-grocery-basket-analysis-dataset)
- **License:** Not clearly stated on the Kaggle page; this is a competition dataset
  originally released by Instacart. **License verification is a required Phase 0/Phase 1
  task before any file is committed or redistributed.** Treat as research-only until
  verified.
- **Files:** `aisles.csv`, `departments.csv`, `products.csv`, `orders.csv`,
  `order_products__prior.csv`, `order_products__train.csv`
- **Schema (verified from community documentation):**
  - `products`: `product_id`, `product_name`, `aisle_id`, `department_id`
  - `aisles`: `aisle_id`, `aisle`
  - `departments`: `department_id`, `department`
  - `orders`: `order_id`, `user_id`, `eval_set`, `order_number`, `order_dow`,
    `order_hour_of_day`, `days_since_prior_order`
  - `order_products__*`: `order_id`, `product_id`, `add_to_cart_order`,
    `reordered`
- **Scale:** ~3.4M orders, ~200k users, ~50k products.
- **Business value:** A human-readable product taxonomy (product name, aisle,
  department) that complements Retailrocket's hashed categories. Useful for
  demonstrating a product catalog adapter and for synthetic inventory/catalog events.
- **Limitations:** Grocery domain differs from NovaCart's general marketplace; license
  unverified; large (~700 MB).

**Candidate C2 — UCI Online Retail II (fallback, license-clear)**

- **URL:** https://archive.ics.uci.edu/dataset/502/online+retail+ii
- **License:** CC BY 4.0 (verified, UCI page).
- **Scale:** ~525,461 transaction lines, UK-based online retailer, 2009-12 to 2011-12.
- **Schema:** `Invoice`, `StockCode`, `Description`, `Quantity`, `InvoiceDate`,
  `Price`, `Customer ID`, `Country`.
- **Business value:** Clear license, real transactions with product descriptions and
  quantities; useful as a second transactional source and for stock/quantity modeling.
- **Limitations:** Another transactional source (overlaps with Olist's role); no
  clickstream; older data; UK giftware niche.

**Recommendation:** Use **C1 (Instacart)** as the primary Source C candidate for its
product catalog, subject to license verification. If the license cannot be confirmed as
usable, fall back to **C2 (UCI Online Retail II)**. In either case, Source C is treated
as a **product catalog enrichment**, not a behavior source, and its identifiers are
never joined to Retailrocket or Olist.

### Source D — Synthetic Operational Events (controlled)

Public datasets do not provide inventory movements, checkout/payment attempts, or
price changes at event level. These will be generated synthetically with explicit
schemas and provenance.

- **Examples:** `inventory_updated`, `stock_depleted`, `stock_replenished`,
  `checkout_started`, `payment_attempted`, `payment_failed`, `product_price_changed`.
- **Rules (to be finalized in Phase 2):**
  - Every synthetic event carries `source = "synthetic"`, a `generator_version`, and a
    `generation_rule_id`.
  - Synthetic events reference synthetic or source-derived product identifiers only
    within their own domain; they are never presented as observations from Retailrocket
    or Olist.
  - Generation is deterministic given a seed (reproducible).
  - Rates, distributions, and edge cases (duplicates, late events, invalid payloads)
    are configurable.
- **Business value:** Fills operational gaps and enables testing of failure/recovery
  paths that real datasets cannot exercise.

---

## C. Integration Feasibility

### Direct integration (same source, joinable)

- **Retailrocket:** `events` ↔ `item_properties` via `itemid`; `category_tree` via
  `categoryid`. These joins are valid within Source A.
- **Olist:** all nine tables join via `order_id`, `customer_id`, `product_id`,
  `seller_id`. Valid within Source B.
- **Instacart:** `order_products` ↔ `products` ↔ `aisles`/`departments`. Valid within
  Source C.

### Cross-source integration (NOT directly joinable)

- Retailrocket `visitorid`/`itemid` and Olist `customer_id`/`product_id` are
  independent identifier spaces. **No join is valid.** We will not fabricate one.
- Retailrocket categories (numeric, hashed) and Olist categories (Portuguese names) and
  Instacart departments are unrelated taxonomies. No mapping will be invented.
- There is no shared customer, order, or product key across sources.

### Canonical data model strategy

Because direct joins are impossible, we define a **canonical event envelope** that
every source maps into, while preserving source-specific identifiers:

```
{
  "event_id":        "uuid (deterministic from source + source_event_id)",
  "event_type":      "view | addtocart | transaction | order_created | ...",
  "event_time":      "ISO-8601 UTC (original source timestamp)",
  "ingestion_time":  "ISO-8601 UTC (when the producer emitted it)",
  "source":          "retailrocket | olist | instacart | synthetic",
  "source_event_id": "original identifier in the source system",
  "entity_type":     "visitor | customer | product | order | ...",
  "entity_id":       "source-prefixed id, e.g. rr:item:123, olist:product:abc",
  "payload":         { ... source-specific fields ... },
  "schema_version":  "semver",
  "provenance":      { "dataset", "file", "row_number" | "generator_version" }
}
```

Key rules:

1. **Source-prefixed identifiers** prevent accidental cross-source joins (`rr:` vs
   `olist:`).
2. **`entity_id` is never treated as globally unique across sources.**
3. Cross-source analysis is limited to **independently computed aggregates** (e.g.,
   "top products by views in Retailrocket" and "top products by revenue in Olist"
   presented side by side), never to joined records.
4. Any analysis that appears to connect sources must be labeled **simulated** and
   documented with its assumptions.

### Where synthetic data is necessary

- Inventory movements and stock levels (no public source provides these at event level).
- Checkout/payment attempt events (Olist has payments, but not attempt/failure events).
- Price change events (Retailrocket has price as a time-stamped property, but no
  explicit "price changed" event).
- Controlled failure injection (duplicates, late events, malformed payloads) for
  reliability testing.

---

## D. Business Metrics

A small, defensible set. Each metric states its formula, source, technical definition,
and limitations. **No cross-source conversion rates are defined.**

### M1 — Product engagement (views and cart additions per product per time window)

- **Business definition:** How much customer attention a product receives over time.
- **Formula:** `views(product, window)` = count of `view` events;
  `cart_additions(product, window)` = count of `addtocart` events.
- **Source:** Retailrocket `events`.
- **Technical:** Spark windowed aggregation over `event_time`, keyed by `itemid`,
  filtered by `event_type`, grouped into tumbling windows (e.g., 1 hour, 1 day).
- **Limitations:** Hashed item IDs are not human-readable; "product" is an opaque ID.
  Only ~90% of events have item properties.

### M2 — View-to-cart ratio (per product)

- **Business definition:** Of the products that receive views, how many convert to
  cart additions. A proxy for product appeal / price / availability friction.
- **Formula:** `cart_additions / views` per product per window (guard against
  divide-by-zero; emit null when views = 0).
- **Source:** Retailrocket `events`.
- **Limitations:** Not a true conversion rate (no session linkage beyond visitor);
  cannot be tied to purchases because purchase events exist but are not linked to the
  same visitor's prior views in a verifiable way across the hashed data. Label as
  **engagement ratio**, not conversion rate.

### M3 — Product demand signal (cart-addition trend)

- **Business definition:** Products with rising cart additions over recent windows.
- **Formula:** `cart_additions(window_t) - cart_additions(window_t-1)` and
  percentage change, per product.
- **Source:** Retailrocket `events`.
- **Limitations:** Trend is descriptive; no causal claim.

### M4 — Transaction activity (orders, revenue, payment mix)

- **Business definition:** Volume and value of completed commerce.
- **Formula:** order count, sum of `price` (order items), sum of `payment_value`,
  distribution by `payment_type` and `order_status`, per time window.
- **Source:** Olist `orders`, `order_items`, `payments`.
- **Limitations:** Historical (2016–2018); no real-time source; revenue is line-item
  price + freight, not margin.

### M5 — Inventory availability signal

- **Business definition:** Which products are available and how availability changes.
- **Formula:** `available` flag per item over time (Retailrocket item properties);
  synthetic `stock_depleted` / `stock_replenished` / `inventory_updated` events with
  `quantity_on_hand`.
- **Source:** Retailrocket item properties (`available`) + synthetic events.
- **Limitations:** `available` is a point-in-time snapshot from the dataset, not a
  live feed; synthetic stock levels are simulated.

### M6 — Data quality and pipeline reliability metrics

- **Business definition:** How trustworthy and performant the platform is.
- **Metrics:** total events, valid events, invalid events, rejected events, duplicate
  candidates, processing failures, events per second, processing latency (event time →
  sink time), consumer lag per topic/partition.
- **Source:** All pipelines (instrumentation).
- **Limitations:** Measured on the local single-node environment; not representative
  of production scale.

### M7 — Late-arriving and out-of-order event counts

- **Business definition:** How much data arrives late and how the system handles it.
- **Formula:** count of events with `event_time < watermark` (dropped) and events
  within the allowed lateness window (accepted).
- **Source:** Spark Structured Streaming metrics.

---

## E. Architecture Proposal

### Conceptual architecture (text diagram)

```
DATA SOURCES
  A: Retailrocket (events, item_properties, category_tree)
  B: Olist (9 transactional tables)
  C: Instacart (product catalog)  [license to verify]
  D: Synthetic operational events
        |
        v
SOURCE INGESTION & ADAPTERS  (Python)
  - CSV readers with schema validation
  - Source-specific normalizers
  - Historical event replay (configurable speed, batching, delays)
  - Synthetic event generators (seeded, deterministic)
  - Provenance tagging
        |
        v
APACHE KAFKA
  - Topics: clickstream-events, transaction-events, product-events,
            inventory-events, invalid-events, dead-letter-events
  - Producers (idempotent where supported), retries, DLQ routing
  - Partitions, keys, retention, consumer groups
        |
        v
STREAM PROCESSING  (Apache Spark Structured Streaming)
  - Parse JSON payloads
  - Validate against event schemas
  - Normalize to canonical envelope
  - Deduplicate by event_id (stateful)
  - Event-time processing + watermarks
  - Windowed aggregations
  - Route invalid records to invalid-events / DLQ
        |
        v
DATA LAKE  (local filesystem, Parquet)
  Bronze : raw events + ingestion metadata (append-only)
  Silver : validated, normalized, deduplicated events
  Gold   : business-ready aggregates and metrics
        |
        v
DATA CONSUMPTION
  - PostgreSQL (Gold tables, serving)
  - SQL analytics
  - Lightweight monitoring (Kafka UI, Spark metrics, custom counters)
```

### Source ingestion design

- **Adapters** are per-source modules under `src/ingestion/` with a common interface:
  `read() -> DataFrame`, `normalize() -> list[CanonicalEvent]`, `validate()`.
- **Replay producers** read normalized events and publish to Kafka with:
  - configurable replay speed (e.g., 1x, 10x, 100x, or "as fast as possible"),
  - original `event_time` preserved in payload,
  - `ingestion_time` set at publish time,
  - deterministic `event_id` (hash of source + source_event_id),
  - configurable batching and controlled delays,
  - retry with backoff, and DLQ routing on failure.
- **Synthetic generator** runs on a schedule/timer, emits operational events, and is
  independently controllable.

### Kafka topic strategy (initial proposal, to be validated in Phase 3)

| Topic | Content | Key | Partitions (initial) | Retention |
|---|---|---|---|---|
| `clickstream-events` | Retailrocket view/addtocart/transaction | `itemid` (product) | 6 | 7 days |
| `transaction-events` | Olist order/payment/review/seller events | `order_id` | 6 | 14 days |
| `product-events` | Catalog updates (incl. Instacart-derived) | `product_id` | 3 | 14 days |
| `inventory-events` | Synthetic stock/availability events | `product_id` | 3 | 7 days |
| `invalid-events` | Schema-invalid records (recoverable) | `source` | 3 | 30 days |
| `dead-letter-events` | Unprocessable / poison messages | `source` | 3 | 30 days |

Rationale for keys: product-keyed clickstream keeps per-product ordering within a
partition; order-keyed transactions keep per-order ordering. Cross-entity ordering is
not guaranteed (and not required).

Open questions (to be resolved via ADR):
- JSON vs Avro (start JSON for simplicity, evaluate Avro + Schema Registry later).
- Partition counts are initial guesses; revisit after throughput measurement.
- Retention is local-disk limited.

### Event schemas

A canonical envelope (above) plus per-type payloads. Example — clickstream view:

```json
{
  "event_id": "rr:evt:a1b2c3...",
  "event_type": "view",
  "event_time": "2015-06-01T12:34:56Z",
  "ingestion_time": "2026-01-01T00:00:00Z",
  "source": "retailrocket",
  "source_event_id": "12345678",
  "entity_type": "product",
  "entity_id": "rr:item:98765",
  "payload": {
    "visitor_id": "rr:visitor:111",
    "item_id": "rr:item:98765",
    "transaction_id": null
  },
  "schema_version": "1.0.0",
  "provenance": { "dataset": "retailrocket", "file": "events.csv", "row_number": 42 }
}
```

Example — synthetic inventory event:

```json
{
  "event_id": "syn:inv:...",
  "event_type": "stock_depleted",
  "event_time": "2026-01-01T00:00:05Z",
  "source": "synthetic",
  "source_event_id": "gen-000001",
  "entity_type": "product",
  "entity_id": "syn:product:42",
  "payload": { "product_id": "syn:product:42", "quantity_on_hand": 0, "threshold": 5 },
  "schema_version": "1.0.0",
  "provenance": { "generator_version": "0.1.0", "generation_rule_id": "stock_depletion_v1", "seed": 42 }
}
```

Schemas will be stored under `schemas/` (JSON Schema) and versioned.

### Spark Structured Streaming design

- **Read** from Kafka topics using `readStream.format("kafka")`.
- **Parse** JSON with a defined schema; malformed → `invalid-events` + DLQ.
- **Validate:** required fields, valid event types, valid timestamps, source-prefixed
  IDs, duplicate detection.
- **Normalize** to canonical envelope; write to Bronze (raw) and Silver (validated).
- **Deduplicate** statefully by `event_id` with a watermark.
- **Event time:** use `event_time` column; configure watermarks (e.g., 10 minutes
  allowed lateness, tunable).
- **Windowed aggregations:** tumbling windows (1 min / 5 min / 1 hour / 1 day) for
  product engagement, demand signals; output to Gold.
- **Checkpointing:** to local path; enables recovery and exactly-once sink semantics
  where supported (file sink).
- **Sinks:** Parquet (Bronze/Silver/Gold) + PostgreSQL (Gold serving tables).
- **Trigger:** processing-time trigger (e.g., 10 seconds) for near-real-time; also
  evaluate micro-batch vs continuous.
- **Failure handling:** checkpoint recovery, retry, DLQ for poison records.

### Data Lake layers

- **Bronze** (`data/processed/bronze/`): raw Kafka payloads + ingestion metadata,
  append-only, Parquet, partitioned by `source` and `ingestion_date`.
- **Silver** (`.../silver/`): validated, normalized, deduplicated canonical events,
  Parquet, partitioned by `source` and `event_date`.
- **Gold** (`.../gold/`): business aggregates (product engagement, demand signals,
  transaction summaries, inventory activity, data quality metrics), Parquet + PostgreSQL.

Storage format: **Parquet** (columnar, compressed, schema evolution friendly). Evaluate
Apache Iceberg later (ADR) — not in initial scope to avoid unnecessary complexity.

### Monitoring strategy

- Kafka: broker health, topic/partition counts, consumer group lag (Kafka UI or
  `kafka-consumer-groups.sh`).
- Spark: query progress, batch duration, input rows/sec, processed rows/sec, state
  store size, watermark (Spark UI / structured streaming progress).
- Application: structured logs (JSON) with event counts, validation failures, DLQ
  counts, throughput, latency.
- Data quality: per-batch counters persisted to Gold (`dq_metrics` table) and to logs.
- Lightweight: no paid/external monitoring. Prefer built-in UIs + logs + Postgres.

---

## F. Technology Evaluation

| Technology | Role | Why necessary | Alternative considered |
|---|---|---|---|
| Python 3.x | Ingestion, producers, tests | Ecosystem, Kafka/Spark clients, readability | Java/Scala (heavier, less portfolio-friendly) |
| SQL | Analytics, serving queries | Standard, portable | — |
| PostgreSQL | Serving layer (Gold) | Reliable, free, SQL analytics | DuckDB (consider for ad-hoc analytics later) |
| Apache Kafka | Event backbone | Decoupling, replay, retention, ordering | RabbitMQ (less suited to replay/streaming) |
| Apache Spark Structured Streaming | Stream processing | Event time, watermarks, state, scale | Flink (steeper curve; Spark more common) |
| Parquet | Lake storage | Columnar, compressed, schema evolution | CSV/JSON (inefficient), Iceberg (later) |
| Docker Compose | Local infra | Reproducible, isolated | Manual installs (fragile) |
| Ubuntu/WSL2 | Dev environment | Required by project | — |
| pytest | Testing | Standard Python testing | unittest |
| GitHub Actions | CI | Free, standard | — |

Principle: **prefer simple, reliable, free, local-first.** No cloud, no paid services,
no unnecessary technologies. Each addition must be justified by a requirement.

---

## G. Implementation Roadmap

| Phase | Goal | Key deliverables | Acceptance criteria |
|---|---|---|---|
| 0 | Research & architecture | This doc, README, ADRs 001–003 | Approved by user before coding |
| 1 | Local infrastructure | Repo init, venv, docker-compose (Kafka + ZK/KRaft, Postgres), topics, producer/consumer smoke test | `docker compose up` works; produce/consume round-trip passes |
| 2 | Multi-source ingestion | Source adapters, replay producers, synthetic generators, provenance | Each source normalizes to canonical envelope; replay configurable |
| 3 | Kafka reliability | Schemas, validation, retries, DLQ, consumer groups, offsets | Invalid records routed, not dropped; recovery documented |
| 4 | Spark Structured Streaming | Parse, validate, dedup, event time, watermarks, checkpoints, sinks | End-to-end Bronze/Silver populated; recovery from checkpoint works |
| 5 | Data Lake & business outputs | Bronze/Silver/Gold, metrics tables, Postgres serving | Metrics queryable; definitions match doc |
| 6 | Reliability & performance | Failure injection, recovery tests, benchmarks (throughput/latency/lag), late events | Results documented, no fabricated numbers |
| 7 | Portfolio delivery | Docs complete, diagrams, README, code review, CI | Repo reproducible by a third party |

Progress will be tracked distinguishing: **Researched / Designed / Implemented / Tested /
Documented / Demonstrated.**

---

## H. Risks and Limitations

### Technical risks

- **Resource constraints:** Spark + Kafka on a single WSL2 machine. Mitigate with
  small samples, configurable batch sizes, and documented minimum specs.
- **License uncertainty (Source C):** Instacart license unverified. Mitigation: verify
  before use; fall back to UCI Online Retail II.
- **Hashed data:** Retailrocket product IDs are opaque; metrics are by opaque ID.
- **Clock/timezone:** historical timestamps are Unix seconds/ms; must normalize to UTC
  ISO-8601. Late-event handling must be tuned to replay speed.

### Data quality risks

- Missing item properties for ~10% of Retailrocket events.
- Missing product dimensions/reviews in Olist.
- Duplicate events in replay (must be deduped).
- Out-of-order arrival during replay (watermarks must handle).

### Integration risks

- Cross-source joins are impossible; any apparent cross-source insight must be
  labeled simulated. Risk of accidental misuse in documentation — mitigated by review.
- Synthetic data could be mistaken for real; mitigated by mandatory provenance fields
  and clear labeling.

### Operational risks

- Checkpoint corruption / schema evolution breaking recovery.
- Disk growth from retained topics and Parquet files.
- No production-grade auth/secrets management (local dev only).

### Honesty commitments

- No fabricated benchmark numbers.
- No undocumented synthetic relationships.
- No claim of exactly-once without demonstration.
- No cross-source conversion rates.

---

## I. Documentation Plan

| File | Purpose |
|---|---|
| `README.md` | Project overview, quick start, architecture summary, status |
| `docs/business/BUSINESS_CASE.md` | Business context, problem, objectives, metrics |
| `docs/data-sources/DATA_SOURCES.md` | Source research, licenses, schemas, limitations |
| `docs/data-dictionary/DATA_DICTIONARY.md` | Canonical model, field definitions, types |
| `docs/event-schemas/EVENT_CATALOG.md` | Event types, schemas, versions, examples |
| `docs/architecture/ARCHITECTURE.md` | Architecture, components, data flow |
| `docs/data-quality/DATA_QUALITY.md` | Validation rules, metrics, DLQ policy |
| `docs/PIPELINE_OPERATIONS.md` | Runbook: start/stop, replay, recovery |
| `docs/testing/TESTING_STRATEGY.md` | Test approach, fixtures, reliability tests |
| `docs/benchmarks/PERFORMANCE_BENCHMARKS.md` | Measured throughput/latency/lag |
| `docs/FAILURE_RECOVERY.md` | Failure scenarios and recovery procedures |
| `docs/LIMITATIONS.md` | Known limitations and scope boundaries |
| `docs/CONTRIBUTING.md` | Dev setup, conventions, commit style |
| `docs/decisions/ADR-*.md` | Architecture Decision Records |
| `docs/PHASE_0_RESEARCH.md` | This document |

ADRs to create in Phase 0/1:
- ADR-001: Multi-source data integration strategy
- ADR-002: Historical event replay architecture
- ADR-003: Kafka topic organization
- ADR-004: Event identification and deduplication
- ADR-005: Event serialization format
- ADR-006: Spark Structured Streaming
- ADR-007: Data Lake storage format
- ADR-008: Checkpointing and recovery
- ADR-009: Data quality and invalid event handling
- ADR-010: Local infrastructure architecture

---

## J. Final Recommendation

**Recommended architecture:** A local, Docker-Compose-based, event-driven platform with
Kafka as the event backbone, Spark Structured Streaming as the processing engine, a
three-layer (Bronze/Silver/Gold) Parquet Data Lake on the local filesystem, and
PostgreSQL as the serving layer, with synthetic events filling operational gaps and
explicit provenance throughout.

**Why this is the most appropriate design for this business problem:**

1. **Multi-source by construction.** The canonical event envelope with source-prefixed
   IDs makes independent sources coexist without fabricating joins.
2. **Honest about limits.** Cross-source analysis is restricted to side-by-side
   aggregates; synthetic data is labeled; no exactly-once claim without proof.
3. **Demonstrates core competencies.** Kafka (producers, consumers, topics,
   partitions, groups, offsets, retries, DLQ), Spark Structured Streaming (event time,
   watermarks, dedup, checkpoints, sinks), data quality, lake layering, recovery.
4. **Local and reproducible.** Docker Compose + Python + free tooling; no cloud
   dependency; a reviewer can run it.
5. **Quality-first.** Data quality metrics and DLQ are first-class, not afterthoughts.
6. **Right-sized.** A small number of meaningful metrics; no unnecessary
   technologies (no Iceberg, no Flink, no cloud) until justified by measurement.

### Verified vs. assumed vs. recommended

- **Verified:** dataset URLs, file names, schemas, published record counts, licenses
  (Retailrocket CC BY-NC-SA 4.0; Olist CC BY-NC-SA 4.0 reported; UCI Online Retail II
  CC BY 4.0), event types, collection periods.
- **Assumed (to be verified against downloaded files):** exact row counts, null rates,
  timestamp ranges, file sizes, Instacart license.
- **Recommended (engineering decisions, to be validated):** topic names, partition
  counts, retention, watermark durations, window sizes, trigger intervals.

### Citations

- Retailrocket dataset: https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset
- Olist dataset: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
- Instacart dataset: https://www.kaggle.com/datasets/psparks/instacart-market-basket-analysis
- UCI Online Retail II: https://archive.ics.uci.edu/dataset/502/online+retail+ii
- Apache Kafka documentation: https://kafka.apache.org/documentation/
- Spark Structured Streaming: https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html

---

**Phase 0 status: Research complete. Awaiting user approval before implementation.**