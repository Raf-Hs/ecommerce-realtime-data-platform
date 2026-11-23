# Event Catalog

**Project:** E-commerce Real-Time Intelligence & Event Streaming Platform

## Schema version

Current: `1.0.0` (defined in `src/models/canonical_event.py`).

## Canonical envelope

All events share the canonical envelope defined in `docs/data-dictionary/DATA_DICTIONARY.md`.

## Event types

### Behavioral (Retailrocket)

| Event type | Source | Description | Payload fields |
|---|---|---|---|
| `view` | retailrocket | Customer viewed a product | visitor_id, item_id, transaction_id |
| `addtocart` | retailrocket | Customer added a product to cart | visitor_id, item_id, transaction_id |
| `transaction` | retailrocket | Customer purchased a product | visitor_id, item_id, transaction_id |

### Transactional (Olist)

| Event type | Source | Description | Payload fields |
|---|---|---|---|
| `order_created` | olist | New order placed | order_id, customer_id, status |
| `order_item_added` | olist | Item added to an order | order_id, product_id, seller_id, price, freight_value |
| `payment_recorded` | olist | Payment recorded for an order | order_id, payment_type, payment_value, installments |

### Transactional (UCI Online Retail II)

| Event type | Source | Description | Payload fields |
|---|---|---|---|
| `purchase` | uci_online_retail | Product purchased (positive quantity) | invoice, stock_code, description, quantity, price, line_total, customer_id, country |
| `cancellation` | uci_online_retail | Order cancelled (invoice starts with C) | same as purchase |
| `return` | uci_online_retail | Product returned (negative quantity) | same as purchase |
| `adjustment` | uci_online_retail | Zero-quantity adjustment | same as purchase |

### Synthetic operational

| Event type | Source | Description | Payload fields |
|---|---|---|---|
| `inventory_updated` | synthetic | Inventory level changed | product_id, quantity_on_hand, threshold |
| `stock_depleted` | synthetic | Product out of stock | product_id, quantity_on_hand, threshold |
| `stock_replenished` | synthetic | Product restocked | product_id, quantity_on_hand, threshold |
| `product_price_changed` | synthetic | Product price changed | (defined in generator) |
| `checkout_started` | synthetic | Checkout initiated | (defined in generator) |
| `payment_attempted` | synthetic | Payment attempt | (defined in generator) |
| `payment_failed` | synthetic | Payment failure | (defined in generator) |

## Validation rules

Defined in `src/validation/event_validator.py`:

- `event_id` must be non-empty.
- `event_type` must be in the valid set (listed above).
- `event_time` must be non-empty.
- `source` must be one of: `retailrocket`, `olist`, `uci_online_retail`, `synthetic`.
- `entity_id` must be non-empty and start with a source prefix (`rr:`, `olist:`, `uci:`, `syn:`).

## Kafka topics

| Topic | Content | Key |
|---|---|---|
| `clickstream-events` | Retailrocket behavior | itemid |
| `transaction-events` | Olist orders/payments | order_id |
| `product-events` | Catalog updates | product_id |
| `inventory-events` | Synthetic stock | product_id |
| `invalid-events` | Schema-invalid records | source |
| `dead-letter-events` | Poison messages | source |

## Example: canonical event (Retailrocket view)

```json
{
  "event_id": "a1b2c3...",
  "event_type": "view",
  "event_time": "2015-06-01T12:34:56Z",
  "ingestion_time": "2026-01-01T00:00:00Z",
  "source": "retailrocket",
  "source_event_id": "42",
  "entity_type": "product",
  "entity_id": "rr:item:98765",
  "payload": {
    "visitor_id": "rr:visitor:111",
    "item_id": "rr:item:98765",
    "transaction_id": null
  },
  "schema_version": "1.0.0",
  "provenance": {
    "dataset": "retailrocket",
    "file": "events.csv",
    "row_number": 42
  }
}
```

## Example: synthetic inventory event

```json
{
  "event_id": "syn:inv:...",
  "event_type": "stock_depleted",
  "event_time": "2026-01-01T00:00:05Z",
  "source": "synthetic",
  "source_event_id": "gen-000001",
  "entity_type": "product",
  "entity_id": "syn:product:42",
  "payload": {
    "product_id": "syn:product:42",
    "quantity_on_hand": 0,
    "threshold": 5
  },
  "schema_version": "1.0.0",
  "provenance": {
    "generator_version": "0.1.0",
    "generation_rule_id": "stock_depletion_v1",
    "seed": 42
  }
}
```