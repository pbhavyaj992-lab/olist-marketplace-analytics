"""Olist Brazilian E-Commerce — clean + analyse (real data, CC BY-NC-SA 4.0).
Business question: which categories and states drive marketplace GMV, and where
does late delivery destroy review scores?
Run:  python3 scripts/01_clean_analyse.py   (from the project folder)
Reads data/raw/*.csv, writes data/clean/ + output/*.csv + output/reconciliation.txt
"""
import os
import pandas as pd
import numpy as np

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(BASE, "data", "raw")
CLEAN = os.path.join(BASE, "data", "clean")
OUT = os.path.join(BASE, "output")
os.makedirs(CLEAN, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

def safe_mode(s):
    m = s.dropna().mode()
    return m.iloc[0] if len(m) else None

def load(name):
    return pd.read_csv(os.path.join(RAW, name))

orders = load("olist_orders_dataset.csv")
items = load("olist_order_items_dataset.csv")
payments = load("olist_order_payments_dataset.csv")
reviews = load("olist_order_reviews_dataset.csv")
customers = load("olist_customers_dataset.csv")
products = load("olist_products_dataset.csv")
sellers = load("olist_sellers_dataset.csv")
geo = load("olist_geolocation_dataset.csv")
trans = load("product_category_name_translation.csv")

raw_counts = {
    "customers": len(customers), "geolocation": len(geo), "orders": len(orders),
    "order_items": len(items), "order_payments": len(payments),
    "order_reviews": len(reviews), "products": len(products),
    "sellers": len(sellers), "category_translation": len(trans),
}
total_raw_rows = sum(raw_counts.values())
print("RAW ROW COUNTS:", raw_counts, "TOTAL:", total_raw_rows)

for c in ["order_purchase_timestamp", "order_approved_at",
          "order_delivered_carrier_date", "order_delivered_customer_date",
          "order_estimated_delivery_date"]:
    orders[c] = pd.to_datetime(orders[c], errors="coerce")
reviews["review_creation_date"] = pd.to_datetime(reviews["review_creation_date"], errors="coerce")

# ---- reconciliation: GMV from items vs payments ---------------------------
gmv_items = items["price"].sum()
freight_items = items["freight_value"].sum()
paid = payments["payment_value"].sum()
n_orders_items = items["order_id"].nunique()
n_orders_payments = payments["order_id"].nunique()
print(f"GMV (sum price, items) = BRL {gmv_items:,.2f}")
print(f"Freight (items)         = BRL {freight_items:,.2f}")
print(f"Paid (payments)         = BRL {paid:,.2f}")
print(f"Paid - (GMV+freight)    = BRL {paid - (gmv_items + freight_items):,.2f}")
print(f"Orders in items: {n_orders_items}, in payments: {n_orders_payments}, in orders table: {len(orders)}")

# ---- order-level fact ------------------------------------------------------
cat_en = dict(zip(trans["product_category_name"], trans["product_category_name_english"]))
prod_cat = products[["product_id", "product_category_name"]].copy()
prod_cat["category_en"] = prod_cat["product_category_name"].map(cat_en).fillna(prod_cat["product_category_name"])

item_cat = items.merge(prod_cat, on="product_id", how="left")
order_gmv = item_cat.groupby("order_id").agg(
    gmv=("price", "sum"), freight=("freight_value", "sum"),
    n_items=("order_item_id", "count"),
    main_category=("category_en", safe_mode),
).reset_index()
order_pay = payments.groupby("order_id").agg(
    paid=("payment_value", "sum"),
    n_payments=("payment_type", "count"),
    main_payment_type=("payment_type", safe_mode),
).reset_index()
order_rev = reviews.sort_values("review_creation_date").groupby("order_id").agg(
    review_score=("review_score", "last"), n_reviews=("review_score", "count")).reset_index()

fact = (orders.merge(order_gmv, on="order_id", how="left")
              .merge(order_pay, on="order_id", how="left")
              .merge(order_rev, on="order_id", how="left")
              .merge(customers[["customer_id", "customer_state", "customer_city"]],
                     on="customer_id", how="left"))
fact["purchase_date"] = fact["order_purchase_timestamp"].dt.date
fact["purchase_month"] = fact["order_purchase_timestamp"].dt.to_period("M").astype(str)
fact["delivery_days"] = (fact["order_delivered_customer_date"] - fact["order_purchase_timestamp"]).dt.total_seconds() / 86400
fact["estimated_days"] = (fact["order_estimated_delivery_date"] - fact["order_purchase_timestamp"]).dt.total_seconds() / 86400
fact["is_late"] = (fact["order_delivered_customer_date"] > fact["order_estimated_delivery_date"]).astype("Int64")
fact["is_delivered"] = (fact["order_status"] == "delivered").astype(int)
fact.to_csv(os.path.join(CLEAN, "fact_orders.csv"), index=False)

# ---- KPIs ------------------------------------------------------------------
delivered = fact[fact["order_status"] == "delivered"]
kpis = {
    "total_raw_rows_all_9_files": total_raw_rows,
    "orders": len(orders),
    "orders_delivered": int((fact["order_status"] == "delivered").sum()),
    "delivered_share_pct": round(100 * (fact["order_status"] == "delivered").mean(), 2),
    "orders_cancelled": int((fact["order_status"] == "canceled").sum()),
    "gmv_brl_items_price": round(float(gmv_items), 2),
    "freight_brl": round(float(freight_items), 2),
    "paid_brl_payments": round(float(paid), 2),
    "paid_minus_gmv_plus_freight_brl": round(float(paid - (gmv_items + freight_items)), 2),
    "avg_order_value_brl": round(float(delivered["gmv"].mean()), 2),
    "avg_review_score": round(float(fact["review_score"].mean()), 2),
    "late_delivery_rate_pct_delivered": round(100 * delivered["is_late"].mean(), 2),
    "avg_delivery_days_delivered": round(float(delivered["delivery_days"].mean()), 2),
    "customers": int(customers["customer_unique_id"].nunique()),
    "sellers": len(sellers),
    "products": len(products),
    "date_min": str(fact["order_purchase_timestamp"].min().date()),
    "date_max": str(fact["order_purchase_timestamp"].max().date()),
}
with open(os.path.join(OUT, "kpis.txt"), "w") as f:
    for k, v in kpis.items():
        f.write(f"{k}: {v}\n")
print(kpis)

# ---- aggregates ------------------------------------------------------------
monthly = (fact[fact["order_status"] == "delivered"]
           .groupby("purchase_month").agg(orders=("order_id", "count"),
                                          gmv_brl=("gmv", "sum"),
                                          avg_review=("review_score", "mean"),
                                          late_rate_pct=("is_late", lambda s: 100 * s.mean()))
           .reset_index())
monthly.to_csv(os.path.join(OUT, "monthly_gmv.csv"), index=False)

cat_items = item_cat.copy()
# 610 products exist in the products table but have no product_category_name,
# so their 1,603 items (BRL 179,535.28) have no category and would vanish from
# a groupby on category_en. Label them "uncategorised" instead of dropping
# them, so category_summary.csv sums back to headline GMV.
cat_items["category_en"] = cat_items["category_en"].fillna("uncategorised")

cat = (cat_items.groupby("category_en").agg(orders=("order_id", "nunique"),
                                           items_sold=("order_item_id", "count"),
                                           gmv_brl=("price", "sum"),
                                           avg_price_brl=("price", "mean"))
       .reset_index().sort_values("gmv_brl", ascending=False))
cat_rev = (fact.merge(cat_items[["order_id", "category_en"]].drop_duplicates(),
                      on="order_id", how="left")
           .groupby("category_en").agg(avg_review=("review_score", "mean"),
                                       late_rate_pct=("is_late", lambda s: 100 * s.mean()))
           .reset_index())
cat = cat.merge(cat_rev, on="category_en", how="left")
cat.to_csv(os.path.join(OUT, "category_summary.csv"), index=False)

state = (fact[fact["order_status"] == "delivered"]
         .groupby("customer_state").agg(orders=("order_id", "count"),
                                        gmv_brl=("gmv", "sum"),
                                        avg_review=("review_score", "mean"),
                                        late_rate_pct=("is_late", lambda s: 100 * s.mean()),
                                        avg_delivery_days=("delivery_days", "mean"))
         .reset_index().sort_values("gmv_brl", ascending=False))
state.to_csv(os.path.join(OUT, "state_summary.csv"), index=False)

delivery_review = (delivered.groupby("is_late").agg(
    orders=("order_id", "count"), avg_review=("review_score", "mean"),
    pct_1_star=("review_score", lambda s: 100 * (s == 1).mean()),
    pct_5_star=("review_score", lambda s: 100 * (s == 5).mean()),
    avg_delivery_days=("delivery_days", "mean")).reset_index())
delivery_review["delivery"] = delivery_review["is_late"].map({0: "on_time", 1: "late"})
delivery_review.to_csv(os.path.join(OUT, "delivery_vs_review.csv"), index=False)

pay = (payments.groupby("payment_type").agg(transactions=("payment_value", "count"),
                                            paid_brl=("payment_value", "sum"),
                                            avg_payment_brl=("payment_value", "mean"))
       .reset_index().sort_values("paid_brl", ascending=False))
pay.to_csv(os.path.join(OUT, "payment_type_summary.csv"), index=False)

status = fact["order_status"].value_counts().reset_index()
status.columns = ["order_status", "orders"]
status.to_csv(os.path.join(OUT, "order_status_counts.csv"), index=False)

delivered_gmv = float(delivered["gmv"].sum())
with open(os.path.join(OUT, "reconciliation.txt"), "w") as f:
    f.write("OLIST — RECONCILIATION (computed from the real files, 2026-11-13)\n")
    for k, v in raw_counts.items():
        f.write(f"raw rows {k}: {v}\n")
    f.write(f"TOTAL raw rows (9 files): {total_raw_rows}\n")
    f.write(f"GMV = sum(price) over order_items: BRL {gmv_items:,.2f}\n")
    f.write(f"Freight = sum(freight_value): BRL {freight_items:,.2f}\n")
    f.write(f"Paid = sum(payment_value): BRL {paid:,.2f}\n")
    f.write(f"Paid - (GMV + freight): BRL {paid - (gmv_items + freight_items):,.2f} "
            "(small gap = orders paid but cancelled/unfulfilled, and rounding)\n")
    f.write(f"Orders present in items: {n_orders_items}; in payments: {n_orders_payments}; "
            f"in orders table: {len(orders)}\n")
    f.write("Per-file scope (each output file sums only to its own defined total):\n")
    f.write("monthly_gmv.csv and state_summary.csv: DELIVERED orders only, "
            f"sum to BRL {delivered_gmv:,.2f} over {len(delivered)} orders. "
            f"Gap to headline GMV is BRL {gmv_items - delivered_gmv:,.2f} of "
            "non-delivered orders.\n")
    f.write("category_summary.csv: ALL order items by product category, including an "
            "'uncategorised' row for items whose product has no category in the "
            "products table (610 products, 1,603 items, BRL 179,535.28). With that "
            "row it sums to headline GMV.\n")
    f.write("payment_type_summary.csv: all payments, sums to Paid above. "
            "order_status_counts.csv: all orders, sums to 99,441. "
            "delivery_vs_review.csv: delivered orders only.\n")
    f.write("Note: the 'orders' column in category_summary.csv counts an order once "
            "per category it appears in, so it does not sum to the order total.\n")
print("DONE — outputs in", OUT)
