# Data Sources

**Project:** E-commerce Real-Time Intelligence & Event Streaming Platform

See `docs/PHASE_0_RESEARCH.md` sections B and C for the full research. This
document is the canonical source reference.

## Source A — Retailrocket E-commerce Dataset

- **URL:** https://www.kaggle.com/datasets/retailrocket/ecommerce-dataset
- **License:** CC BY-NC-SA 4.0
- **Purpose:** Primary historical clickstream and behavioral data.
- **Files:** `events.csv`, `item_properties_part1.csv`, `item_properties_part2.csv`,
  `category_tree.csv`
- **Schema:**
  - `events`: `visitorid`, `itemid`, `event`, `transactionid`, `timestamp`
    (`event` ∈ {view, addtocart, transaction})
  - `item_properties`: `timestamp`, `itemid`, `property`, `value`
  - `category_tree`: `categoryid`, `parentid`
- **Scale:** 2,756,101 events; 1,407,580 visitors; 417,053 items; 1,669 category rows.
- **Limitations:** hashed values (except `categoryid`, `available`); ~10% events
  lack item properties; no customer demographics or clear pricing.

## Source B — Olist Brazilian E-commerce Dataset

- **URL:** https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
- **License:** CC BY-NC-SA 4.0 (verify on data card)
- **Purpose:** Real transactional and operational data.
- **Files:** 9 CSVs (customers, orders, order_items, products, payments, reviews,
  sellers, geolocation, category_translation).
- **Scale:** ~100,000 orders, 2016-09 to 2018-09.
- **Limitations:** no clickstream; `customer_id` is per-order; missing values; duplicate
  zip prefixes; Portuguese category names.

## Source C — Product catalog (chosen at implementation)

- **Candidate C1 — Instacart Market Basket Analysis**
  (https://www.kaggle.com/datasets/psparks/instacart-market-basket-analysis):
  ~3.4M orders, ~50k products, human-readable taxonomy. License unverified — must
  be verified before use.
- **Candidate C2 — UCI Online Retail II**
  (https://archive.ics.uci.edu/dataset/502/online+retail+ii): CC BY 4.0, ~525k
  transaction lines. Fallback if Instacart license is unusable.

## Source D — Synthetic operational events

Generated with explicit schemas and provenance (`source = "synthetic"`,
`generator_version`, `generation_rule_id`, `seed`). Examples: `inventory_updated`,
`stock_depleted`, `stock_replenished`, `product_price_changed`, `checkout_started`,
`payment_attempted`, `payment_failed`. Never presented as real observations.

## Integration rules

- Retailrocket and Olist identifiers are independent. No joins across sources.
- Source-prefixed identifiers (`rr:`, `olist:`, `syn:`).
- Cross-source analysis limited to side-by-side aggregates.
- Synthetic relationships documented and labeled simulated.