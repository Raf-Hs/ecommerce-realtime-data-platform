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

## Source C — UCI Online Retail II (implemented)

- **URL:** https://archive.ics.uci.edu/dataset/502/online+retail+ii
- **License:** CC BY 4.0 (verified).
- **Purpose:** Transactional data from a UK-based online retailer (giftware).
- **Files:** Excel workbook with two sheets:
  - `Year 2009-2010` (525,461 rows)
  - `Year 2010-2011` (541,910 rows)
  - Combined: ~1.07M rows.
- **Schema (verified against downloaded file):**
  - `Invoice` (string): invoice number; prefix "C" denotes cancellation.
  - `StockCode` (string): product code.
  - `Description` (string): product name (2,928 missing in 2009-2010 sheet).
  - `Quantity` (int): units per line; negative for returns.
  - `InvoiceDate` (datetime): transaction timestamp.
  - `Price` (float): unit price; 3,687 zero-price rows; some negative.
  - `Customer ID` (float): customer identifier (107,927 missing in 2009-2010 sheet).
  - `Country` (string): customer country (40 distinct).
- **Scale:** 28,816 unique invoices, 4,632 stock codes, 4,383 customers, 40 countries.
  Quantity range -9,600..19,152; Price range -53,594.36..25,111.10.
- **Date range:** 2009-12-01 to 2011-12-09.
- **Adapter:** `src/ingestion/uci_online_retail.py` (UCIOnlineRetailAdapter).
- **Event types produced:** `purchase`, `cancellation`, `return`, `adjustment`.
- **Limitations:**
  - No clickstream or browsing data.
  - ~20% of rows lack a Customer ID (guest purchases).
  - Description missing on ~2,928 rows.
  - Negative quantities and prices require careful handling (returns, adjustments).
  - UK giftware niche; not representative of all e-commerce.
  - Timestamps have no timezone (assumed UTC).
- **Alternative (optional): Instacart Market Basket Analysis**
  (https://www.kaggle.com/datasets/psparks/instacart-market-basket-analysis):
  ~3.4M orders, ~50k products. License unverified — may be used only after
  license verification.

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