# Power BI model — Olist Marketplace Analytics

No .pbix is in this repo (no Power BI Desktop here). Build it from this document:
load `data/clean/fact_orders.csv` and the `output/*.csv` aggregates, or connect
Power BI to the PostgreSQL schema in `sql/schema.sql`.

## Star schema
- **FactOrders** (grain: one row per order) — `data/clean/fact_orders.csv`.
  Keys: order_id, customer_id. Measures live here: gmv, freight, paid, review_score,
  delivery_days, is_late, is_delivered.
- **DimCustomer** — customer_id, customer_unique_id, customer_state, customer_city.
- **DimDate** — purchase_date, purchase_month, year, month, quarter.
- **DimCategory** — from products + category_translation (English names).
- **DimPaymentType** — credit_card, boleto, voucher, debit_card.
- Relationships: FactOrders → DimCustomer (many-to-one), → DimDate, → DimCategory.

## DAX measures (paste into Power BI)
```dax
GMV = SUM(FactOrders[gmv])
Freight = SUM(FactOrders[freight])
Paid = SUM(FactOrders[paid])
Orders = COUNTROWS(FactOrders)
Delivered Orders = CALCULATE(COUNTROWS(FactOrders), FactOrders[order_status] = "delivered")
Avg Order Value = DIVIDE([GMV], [Delivered Orders])
Avg Review Score = AVERAGE(FactOrders[review_score])
Late Delivery Rate % = 100 * DIVIDE(
    CALCULATE(COUNTROWS(FactOrders), FactOrders[is_late] = 1, FactOrders[order_status] = "delivered"),
    [Delivered Orders])
Pct 1-Star Reviews = 100 * DIVIDE(
    CALCULATE(COUNTROWS(FactOrders), FactOrders[review_score] = 1), COUNTROWS(FactOrders))
GMV Share % = DIVIDE([GMV], CALCULATE([GMV], ALL(FactOrders)))
```

## Pages
1. **Overview** — GMV, orders, avg order value, avg review; monthly GMV line; GMV by state map/bar.
2. **Categories** — GMV, orders and avg review by category; late rate by category.
3. **Delivery vs reviews** — late vs on-time review distribution; avg delivery days by state; RJ spotlight.
4. **Payments** — payment mix, instalments, paid vs GMV reconciliation card.
