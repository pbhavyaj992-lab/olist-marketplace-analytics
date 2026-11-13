-- 1. Monthly GMV (delivered orders)
SELECT date_trunc('month', o.order_purchase_timestamp) AS month,
       COUNT(*) AS orders, SUM(i.price) AS gmv_brl
FROM olist.orders o JOIN olist.order_items i USING (order_id)
WHERE o.order_status = 'delivered'
GROUP BY 1 ORDER BY 1;

-- 2. GMV and average review by category (English names). 610 products have
-- a blank category name, so they group as 'uncategorised' (1,451 orders,
-- 1,603 items, BRL 179,535.28) instead of NULL, so the file sums to GMV.
SELECT COALESCE(t.product_category_name_english, 'uncategorised') AS category,
       COUNT(DISTINCT i.order_id) AS orders, SUM(i.price) AS gmv_brl,
       AVG(r.review_score) AS avg_review
FROM olist.order_items i
JOIN olist.products p USING (product_id)
LEFT JOIN olist.category_translation t USING (product_category_name)
LEFT JOIN olist.order_reviews r USING (order_id)
GROUP BY 1 ORDER BY gmv_brl DESC;

-- 3. Late delivery vs review score (the headline finding)
SELECT (o.order_delivered_customer_date > o.order_estimated_delivery_date) AS is_late,
       COUNT(*) AS orders, AVG(r.review_score) AS avg_review,
       100.0 * AVG(CASE WHEN r.review_score = 1 THEN 1 ELSE 0 END) AS pct_1_star
FROM olist.orders o LEFT JOIN olist.order_reviews r USING (order_id)
WHERE o.order_status = 'delivered'
GROUP BY 1;

-- 4. Reconciliation: GMV vs payments
SELECT (SELECT SUM(price) FROM olist.order_items) AS gmv_brl,
       (SELECT SUM(freight_value) FROM olist.order_items) AS freight_brl,
       (SELECT SUM(payment_value) FROM olist.order_payments) AS paid_brl;

-- 5. GMV by state
SELECT c.customer_state, COUNT(DISTINCT o.order_id) AS orders, SUM(i.price) AS gmv_brl
FROM olist.orders o JOIN olist.customers c USING (customer_id)
JOIN olist.order_items i USING (order_id)
WHERE o.order_status = 'delivered'
GROUP BY 1 ORDER BY gmv_brl DESC;

-- 6. Payment mix
SELECT payment_type, COUNT(*) AS transactions, SUM(payment_value) AS paid_brl
FROM olist.order_payments GROUP BY 1 ORDER BY paid_brl DESC;
