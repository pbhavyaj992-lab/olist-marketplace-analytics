# Data dictionary — Olist (raw files, `data/raw/`)

| File | Rows | Grain | Key columns |
|---|---|---|---|
| olist_customers_dataset.csv | 99,441 | customer | customer_id, customer_unique_id, customer_state, customer_city |
| olist_orders_dataset.csv | 99,441 | order | order_id, customer_id, order_status, order_purchase_timestamp, order_delivered_customer_date, order_estimated_delivery_date |
| olist_order_items_dataset.csv | 112,650 | order line | order_id, product_id, seller_id, price (BRL), freight_value (BRL) |
| olist_order_payments_dataset.csv | 103,886 | payment | order_id, payment_type, payment_installments, payment_value (BRL) |
| olist_order_reviews_dataset.csv | 99,224 | review | order_id, review_score (1–5), review_comment_message (may contain newlines) |
| olist_products_dataset.csv | 32,951 | product | product_id, product_category_name (Portuguese) |
| olist_sellers_dataset.csv | 3,095 | seller | seller_id, seller_state, seller_city |
| olist_geolocation_dataset.csv | 1,000,163 | zip prefix | geolocation_zip_code_prefix, lat, lng |
| product_category_name_translation.csv | 71 | category | product_category_name, product_category_name_english |

Clean fact: `data/clean/fact_orders.csv` (99,441 rows, one per order) with gmv, freight,
paid, review_score, delivery_days, is_late, is_delivered, purchase_month.
