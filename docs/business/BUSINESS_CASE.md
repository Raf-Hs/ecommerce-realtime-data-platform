# Business Case

**Project:** E-commerce Real-Time Intelligence & Event Streaming Platform

## 1. Company context

NovaCart is a fictional mid-sized online marketplace selling consumer goods across
multiple categories (electronics, home & living, fashion, sports, everyday
essentials). It operates a single storefront website, a mobile web experience, and
a network of third-party sellers. Customers browse, search, add to cart, and
purchase. Sellers manage inventory and fulfill orders.

## 2. Business problem

NovaCart's data is fragmented across independent systems:

1. Customer behavior (clicks, views, cart additions) lives in the web analytics
   pipeline.
2. Orders, payments, and logistics live in the transactional order management
   system.
3. Product attributes and availability live in the catalog service.
4. Inventory movements are not captured as events at all.

These systems were built independently and do not share identifiers or schemas.

## 3. Why existing infrastructure is insufficient

- **Batch reporting only.** Reports run nightly; by the time a surge, stockout, or
  engagement drop is visible, the reaction window has closed.
- **No unified demand view.** "Which products get attention but not carts?" cannot
  be answered reliably because behavior and transactions are not joinable by a
  trusted key — and in reality they cannot be joined at all across the independent
  datasets.
- **No data quality visibility.** Invalid, duplicate, or late events are silently
  dropped with no record of what was rejected or why.
- **No replay or recovery.** A failed consumer cannot be recovered in a documented
  way, and impact cannot be measured.
- **No provenance.** There is no lineage from a metric back to its source record.

## 4. Why multiple sources are necessary

No single source answers the business questions. Behavior (Retailrocket) shows
attention; transactions (Olist) show completed commerce; catalog (Instacart/UCI)
shows product taxonomy; synthetic events cover operational gaps (inventory,
checkout, payments). Combining them — without fabricating joins — is the core of
the platform's value.

## 5. Business objectives

1. Provide near-real-time visibility into product engagement and demand signals.
2. Monitor transaction activity and payment mix.
3. Track product availability and inventory events.
4. Enforce data quality with full provenance and rejection tracking.
5. Demonstrate recoverable, observable streaming infrastructure.
6. Produce a small set of well-defined, defensible business outputs.

## 6. Business questions the platform answers

- Which products receive the most customer attention?
- How are customer interactions changing over time?
- Which products receive views but few cart additions?
- Which products show rising demand (cart additions)?
- What is the transaction volume and payment mix?
- Which products are available, and how does availability change?
- How quickly can changes in customer activity be detected?
- How reliable is the event infrastructure (throughput, latency, lag, DQ)?

## 7. What the platform does NOT answer

- Cross-source conversion rates (Retailrocket views → Olist purchases). Not
  computable; identifiers are independent.
- Customer journeys spanning sources. Not computable.
- Margin or profitability (no cost data).

## 8. Business outputs

1. Real-time product engagement monitoring (views, cart additions per product per
   window).
2. Customer interaction analysis (engagement ratios, trends).
3. Product demand signals (rising cart additions).
4. Inventory event monitoring (availability + synthetic stock events).
5. Transaction activity monitoring (orders, revenue, payment mix).
6. Data quality and pipeline reliability reporting.

## 9. Success criteria

- End-to-end pipeline runs locally via Docker Compose.
- Events flow from sources through Kafka through Spark into Delta Lake and Postgres.
- Data quality metrics are produced and visible.
- Recovery from checkpoint is demonstrated.
- Documentation is complete and accurate to implementation.