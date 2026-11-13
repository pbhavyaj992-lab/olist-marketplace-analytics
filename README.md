# Olist Marketplace Analytics

**Dataset:** Brazilian E-Commerce Public Dataset by Olist
**Scale:** 1,550,922 rows across 9 CSV files; 99,441 orders; 112,650 order items.

## Business question
Which product categories and states drive marketplace GMV, and where does late delivery destroy review scores?

## Licence and commercial use
**Licence: CC BY-NC-SA 4.0 — portfolio / learning use ONLY, never sellable.**
Attribution to Olist is required, and any adaptation must be shared under the same licence (ShareAlike). Do not sell this project, its outputs or the data.

## Data source and how to reproduce
Source: Kaggle dataset `olistbr/brazilian-ecommerce` — https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
Obtained without a login from Olist's own public GitHub repository `olist/work-at-olist-data` (folder `datasets/`), which hosts the same 9 CSV files. To reproduce from Kaggle instead: create a free Kaggle account, download the dataset, unzip, and place the 9 CSVs in `data/raw/` with their original names, then run `python3 scripts/01_clean_analyse.py`.

**Status: REAL DATA PROCESSED.** Every figure below was computed from the real
dataset by `scripts/01_clean_analyse.py`. Nothing is fabricated. See
`output/reconciliation.txt` for the full reconciliation.

## Key figures (from `output/kpis.txt`)
- total_raw_rows_all_9_files: 1550922
- orders: 99441
- orders_delivered: 96478
- delivered_share_pct: 97.02
- orders_cancelled: 625
- gmv_brl_items_price: 13591643.7
- freight_brl: 2256599.44
- paid_brl_payments: 16008872.12
- paid_minus_gmv_plus_freight_brl: 160628.98
- avg_order_value_brl: 137.04
- avg_review_score: 4.09
- late_delivery_rate_pct_delivered: 8.11
- avg_delivery_days_delivered: 12.56
- customers: 96096
- sellers: 3095
- products: 32951
- date_min: 2016-09-04
- date_max: 2018-10-17

## What the data actually says
- Late delivery destroys reviews: delivered on time averages 4.29 stars, delivered late averages 2.57. 45.2% of late orders get 1 star, against 6.6% of on-time orders.
- Only 8.11% of delivered orders are late, but those 7,826 orders carry the review damage — fix delivery promises in RJ (13.5% late, 15.3 days average) before spending on acquisition.
- Sao Paulo is the marketplace: 40,501 orders and BRL 5,067,633.16 of GMV, 37.3% of the total.
- Health and beauty is the largest category (BRL 1,258,681.34), followed by watches and gifts (BRL 1,205,005.68).
- Credit card is 78.3% of money paid (BRL 12,542,084.19); boleto is second at BRL 2,869,361.27.
- Reconciliation: GMV from order items is BRL 13,591,643.70; payments total BRL 16,008,872.12. The BRL 160,628.98 gap (1.0%) is orders paid but cancelled or not yet fulfilled — see output/reconciliation.txt.

## The decision this answers
Tighten the delivery promise (estimated date) for RJ and for the categories with the worst late rates, and prioritise seller operations in Sao Paulo, where one late delivery costs the most review damage.

## Reconciliation
```
OLIST — RECONCILIATION (computed from the real files, 2026-11-13)
raw rows customers: 99441
raw rows geolocation: 1000163
raw rows orders: 99441
raw rows order_items: 112650
raw rows order_payments: 103886
raw rows order_reviews: 99224
raw rows products: 32951
raw rows sellers: 3095
raw rows category_translation: 71
TOTAL raw rows (9 files): 1550922
GMV = sum(price) over order_items: BRL 13,591,643.70
Freight = sum(freight_value): BRL 2,256,599.44
Paid = sum(payment_value): BRL 16,008,872.12
Paid - (GMV + freight): BRL 160,628.98 (small gap = orders paid but cancelled/unfulfilled, and rounding)
Orders present in items: 98666; in payments: 99440; in orders table: 99441
Per-file scope (each output file sums only to its own defined total):
monthly_gmv.csv and state_summary.csv: DELIVERED orders only, sum to BRL 13,221,498.11 over 96,478 orders. Gap to headline GMV is BRL 370,145.59 of non-delivered orders.
category_summary.csv: ALL order items by product category, including an 'uncategorised' row for items whose product has no category in the products table (610 products, 1,603 items, BRL 179,535.28). With that row it sums to headline GMV.
payment_type_summary.csv: all payments, sums to Paid above. order_status_counts.csv: all orders, sums to 99,441. delivery_vs_review.csv: delivered orders only.
Note: the 'orders' column in category_summary.csv counts an order once per category it appears in, so it does not sum to the order total.
```

## What is in this folder
- `data/raw/` — the real source file(s), as downloaded.
- `data/clean/` — cleaned fact table / sample produced by the pipeline.
- `data/data_dictionary.md` — column meanings, grains, caveats.
- `scripts/01_clean_analyse.py` — the full reproducible pipeline (clean + analyse + reconcile).
- `sql/schema.sql` — PostgreSQL schema for the same model.
- `sql/analysis_queries.sql` — the key analytical queries in SQL.
- `powerbi/model.md` — star schema, DAX measures and page plan (no .pbix in this repo; build it from this document).
- `excel/` — Excel dashboard workbook built from the real aggregates.
- `output/` — aggregate CSVs, `kpis.txt`, `reconciliation.txt`.

## Stack
Power BI, DAX, Python (pandas), SQL, PostgreSQL, Excel. Built by Bhavya Patel.
