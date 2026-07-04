from pathlib import Path
import sqlite3

import pandas as pd


# =====================================================
# Paths
# =====================================================

RAW_DATA = Path("data/raw")
PROCESSED_DATA = Path("data/processed")

PROCESSED_DATA.mkdir(parents=True, exist_ok=True)

DB_PATH = Path("data/ecommerce.db")


# =====================================================
# Read CSV Files
# =====================================================

customers = pd.read_csv(RAW_DATA / "olist_customers_dataset.csv")

orders = pd.read_csv(
    RAW_DATA / "olist_orders_dataset.csv",
    parse_dates=[
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
)

order_items = pd.read_csv(
    RAW_DATA / "olist_order_items_dataset.csv",
    parse_dates=["shipping_limit_date"],
)

payments = pd.read_csv(
    RAW_DATA / "olist_order_payments_dataset.csv"
)

products = pd.read_csv(
    RAW_DATA / "olist_products_dataset.csv"
)

category_translation = pd.read_csv(
    RAW_DATA / "product_category_name_translation.csv"
)


# =====================================================
# Display Dataset Shapes
# =====================================================

print("\nDataset Shapes")
print("-" * 40)

datasets = {
    "Customers": customers,
    "Orders": orders,
    "Order Items": order_items,
    "Payments": payments,
    "Products": products,
    "Category Translation": category_translation,
}

for name, df in datasets.items():
    print(f"{name:<25} {df.shape}")

# =====================================================
# Translate Product Categories to English
# =====================================================

products = products.merge(
    category_translation,
    on="product_category_name",
    how="left"
)

products.drop(columns=["product_category_name"], inplace=True)

products.rename(
    columns={
        "product_category_name_english": "product_category"
    },
    inplace=True
)


# =====================================================
# Merge Orders + Customers
# =====================================================

analytics = orders.merge(
    customers,
    on="customer_id",
    how="left"
)

print(f"\nAfter Orders + Customers : {analytics.shape}")


# =====================================================
# Merge Order Items
# =====================================================

analytics = analytics.merge(
    order_items,
    on="order_id",
    how="left"
)

print(f"After Order Items       : {analytics.shape}")


# =====================================================
# Merge Products
# =====================================================

analytics = analytics.merge(
    products,
    on="product_id",
    how="left"
)

print(f"After Products          : {analytics.shape}")


# =====================================================
# Aggregate Payments
# One Row Per Order
# =====================================================

payments_agg = (
    payments
    .groupby("order_id", as_index=False)
    .agg(
        payment_value=("payment_value", "sum"),
        payment_installments=("payment_installments", "max"),
        payment_type=("payment_type", "first")
    )
)

print(f"\nPayments Before Aggregation : {payments.shape}")
print(f"Payments After Aggregation  : {payments_agg.shape}")


# =====================================================
# Merge Payments
# =====================================================

analytics = analytics.merge(
    payments_agg,
    on="order_id",
    how="left"
)

print(f"After Payments             : {analytics.shape}")

# =====================================================
# Data Cleaning
# =====================================================

# Remove duplicate rows
analytics = analytics.drop_duplicates()

# Fill missing product categories
analytics["product_category"] = analytics["product_category"].fillna("Unknown")

# Fill missing product information
product_columns = [
    "product_name_lenght",
    "product_description_lenght",
    "product_photos_qty",
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm",
]

for column in product_columns:
    analytics[column] = analytics[column].fillna(0)

# Fill missing payment information
analytics["payment_type"] = analytics["payment_type"].fillna("Unknown")
analytics["payment_installments"] = analytics["payment_installments"].fillna(0)
analytics["payment_value"] = analytics["payment_value"].fillna(0)

print("\nAfter Cleaning")
print("-" * 40)
print(f"Rows    : {analytics.shape[0]:,}")
print(f"Columns : {analytics.shape[1]}")

print("\nMissing Values")
print(analytics.isna().sum())

# =====================================================
# Save Analytics Dataset
# =====================================================

OUTPUT_CSV = PROCESSED_DATA / "analytics_orders.csv"

analytics.to_csv(
    OUTPUT_CSV,
    index=False
)

print(f"\nDataset saved to:\n{OUTPUT_CSV}")

# =====================================================
# Save to SQLite
# =====================================================

conn = sqlite3.connect(DB_PATH)

analytics.to_sql(
    "analytics_orders",
    conn,
    if_exists="replace",
    index=False,
)

conn.close()

print(f"\nSQLite database saved to:\n{DB_PATH}")