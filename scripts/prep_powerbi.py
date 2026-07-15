from pathlib import Path

import pandas as pd

# =====================================================
# Paths
# =====================================================

INPUT_FILE = Path("data/processed/analytics_orders.csv")
OUTPUT_FILE = Path("data/processed/powerbi_dataset.csv")

# =====================================================
# Read Dataset
# =====================================================

df = pd.read_csv(
    INPUT_FILE,
    parse_dates=[
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ],
)

# =====================================================
# Create Date Features
# =====================================================

df["order_year"] = df["order_purchase_timestamp"].dt.year
df["order_month"] = df["order_purchase_timestamp"].dt.month
df["order_month_name"] = df["order_purchase_timestamp"].dt.strftime("%B")
df["order_quarter"] = df["order_purchase_timestamp"].dt.quarter
df["order_day"] = df["order_purchase_timestamp"].dt.day
df["order_weekday"] = df["order_purchase_timestamp"].dt.day_name()

# =====================================================
# Delivery Metrics
# =====================================================

df["delivery_days"] = (
    df["order_delivered_customer_date"] -
    df["order_purchase_timestamp"]
).dt.days

df["estimated_delivery_days"] = (
    df["order_estimated_delivery_date"] -
    df["order_purchase_timestamp"]
).dt.days

df["delivery_delay"] = (
    df["delivery_days"] -
    df["estimated_delivery_days"]
)

# =====================================================
# Revenue Metrics
# =====================================================

df["total_price"] = df["price"] + df["freight_value"]

# =====================================================
# Save
# =====================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("=" * 80)
print("Power BI dataset created successfully.")
print(f"Rows    : {len(df):,}")
print(f"Columns : {len(df.columns)}")
print(f"Saved to: {OUTPUT_FILE}")
print("=" * 80)