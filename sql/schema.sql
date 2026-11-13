-- Olist — PostgreSQL schema. Load the 9 raw CSVs with \copy (headers included).
-- All money in BRL. Dates are timestamps; order_id is the grain of fact_orders.
CREATE SCHEMA IF NOT EXISTS olist;

CREATE TABLE olist.customers (
    customer_id TEXT PRIMARY KEY, customer_unique_id TEXT NOT NULL,
    customer_zip_code_prefix INT, customer_city TEXT, customer_state CHAR(2));

CREATE TABLE olist.orders (
    order_id TEXT PRIMARY KEY, customer_id TEXT REFERENCES olist.customers(customer_id),
    order_status TEXT, order_purchase_timestamp TIMESTAMP, order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP, order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP);

CREATE TABLE olist.order_items (
    order_id TEXT REFERENCES olist.orders(order_id), order_item_id INT,
    product_id TEXT, seller_id TEXT, shipping_limit_date TIMESTAMP,
    price NUMERIC(10,2), freight_value NUMERIC(10,2),
    PRIMARY KEY (order_id, order_item_id));

CREATE TABLE olist.order_payments (
    order_id TEXT REFERENCES olist.orders(order_id), payment_sequential INT,
    payment_type TEXT, payment_installments INT, payment_value NUMERIC(10,2),
    PRIMARY KEY (order_id, payment_sequential));

CREATE TABLE olist.order_reviews (
    review_id TEXT PRIMARY KEY, order_id TEXT REFERENCES olist.orders(order_id),
    review_score INT CHECK (review_score BETWEEN 1 AND 5),
    review_comment_title TEXT, review_comment_message TEXT,
    review_creation_date TIMESTAMP, review_answer_timestamp TIMESTAMP);

CREATE TABLE olist.products (
    product_id TEXT PRIMARY KEY, product_category_name TEXT,
    product_name_length INT, product_description_length INT,
    product_photos_qty INT, product_weight_g INT,
    product_length_cm INT, product_height_cm INT, product_width_cm INT);

CREATE TABLE olist.sellers (
    seller_id TEXT PRIMARY KEY, seller_zip_code_prefix INT,
    seller_city TEXT, seller_state CHAR(2));

CREATE TABLE olist.category_translation (
    product_category_name TEXT PRIMARY KEY, product_category_name_english TEXT);

CREATE INDEX idx_orders_purchase ON olist.orders (order_purchase_timestamp);
CREATE INDEX idx_items_order ON olist.order_items (order_id);
CREATE INDEX idx_reviews_order ON olist.order_reviews (order_id);
