# Data Dictionary

**Project:** E-commerce Real-Time Intelligence & Event Streaming Platform

## Canonical event model

Every source is normalized into a single envelope (`CanonicalEvent`) so that
downstream processing is source-agnostic while preserving source-specific
identifiers and provenance.

Defined in: `src/models/canonical_event.py`

### Field definitions

| Field | Type | Required | Description |
|---|---|---|---|
| `event_id` | string (SHA-256 hex) | Yes | Deterministic ID: `sha256(source \| source_event_id \| event_time)`. Enables idempotent replay. |
| `event_type` | string (enum) | Yes | Type of event. See Event Catalog. |
| `event_time` | ISO-8601 UTC string | Yes | Original source timestamp, preserved during replay. |
| `ingestion_time` | ISO-8601 UTC string | Yes | Timestamp when the producer emitted the event. |
| `source` | string (enum) | Yes | Source system: `retailrocket`, `olist`, `uci_online_retail`, `synthetic`. |
| `source_event_id` | string | Yes | Original identifier in the source system (or generated ID for synthetic). |
| `entity_type` | string | Yes | Type of entity: `product`, `order`, `visitor`, `customer`. |
| `entity_id` | string (source-prefixed) | Yes | Source-prefixed entity ID, e.g. `rr:item:100`, `olist:order:abc`, `uci:product:X`, `syn:product:42`. Never joined across sources. |
| `payload` | JSON object (string) | Yes | Source-specific fields. Schema varies by event type. |
| `schema_version` | string (semver) | Yes | Schema version, currently `1.0.0`. |
| `provenance` | JSON object | Yes | Origin metadata: dataset, file, row number, generator version, seed, license. |

### Source identifier prefixes

| Prefix | Source | Example |
|---|---|---|
| `rr:` | Retailrocket | `rr:item:100`, `rr:visitor:1` |
| `olist:` | Olist | `olist:order:abc`, `olist:product:xyz` |
| `uci:` | UCI Online Retail II | `uci:product:85048`, `uci:customer:13085` |
| `syn:` | Synthetic | `syn:product:42` |

### Source-specific field mappings

#### Retailrocket (events.csv)

| Source column | Canonical field | Notes |
|---|---|---|
| `visitorid` | `payload.visitor_id` | Prefixed as `rr:visitor:{id}` |
| `itemid` | `entity_id`, `payload.item_id` | Prefixed as `rr:item:{id}` |
| `event` | `event_type` | view, addtocart, transaction |
| `transactionid` | `payload.transaction_id` | Null for non-transaction events |
| `timestamp` | `event_time` | Unix milliseconds → ISO-8601 UTC |

#### Olist

| Source table | Event type | Key fields |
|---|---|---|
| `olist_orders_dataset.csv` | `order_created` | order_id, customer_id, order_status, order_purchase_timestamp |
| `olist_order_items_dataset.csv` | `order_item_added` | order_id, product_id, seller_id, price, freight_value |
| `olist_order_payments_dataset.csv` | `payment_recorded` | order_id, payment_type, payment_value, installments |

#### UCI Online Retail II

| Source column | Canonical field | Notes |
|---|---|---|
| `Invoice` | `payload.invoice` | Prefix "C" → cancellation event type |
| `StockCode` | `entity_id` | Prefixed as `uci:product:{code}` |
| `Description` | `payload.description` | "unknown" if missing |
| `Quantity` | `payload.quantity` | Negative for returns |
| `InvoiceDate` | `event_time` | `YYYY-MM-DD HH:MM:SS` → ISO-8601 UTC (assumed UTC) |
| `Price` | `payload.price` | Unit price; 0 for some rows |
| `Customer ID` | `payload.customer_id` | Null for guest purchases (~20% missing) |
| `Country` | `payload.country` | Customer country |

#### Synthetic

| Field | Description |
|---|---|
| `payload.product_id` | Product ID (synthetic namespace) |
| `payload.quantity_on_hand` | Stock level |
| `payload.threshold` | Low-stock threshold |
| `provenance.generator_version` | Generator version string |
| `provenance.generation_rule_id` | Rule identifier |
| `provenance.seed` | Random seed for reproducibility |

### Bronze layer

Raw Kafka payloads + ingestion metadata. Append-only. Parquet/Delta format.
Columns: Kafka metadata (topic, partition, offset, timestamp) + raw payload + ingestion time.

### Silver layer

Validated, normalized, deduplicated canonical events. Delta format.
Columns: all CanonicalEvent fields + Kafka metadata.

### Gold layer

Business-ready aggregates. Delta format + PostgreSQL serving.

| Table | Columns | Description |
|---|---|---|
| `gold_product_engagement` | window_start, window_end, product_id, views, cart_additions, view_to_cart_ratio | Per-product engagement per time window |

### PostgreSQL serving tables

| Table | Primary key | Description |
|---|---|---|
| `gold_product_engagement` | (window_start, product_id) | Upserted from Gold Delta layer |