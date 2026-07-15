from pathlib import Path
import sqlite3

import pandas as pd
import plotly.express as px

# =====================================================
# Configuration
# =====================================================

DB_PATH = "data/ecommerce.db"
CHARTS_DIR = Path("charts")

CHARTS_DIR.mkdir(parents=True, exist_ok=True)

# =====================================================
# Database Connection
# =====================================================

conn = sqlite3.connect(DB_PATH)

# =====================================================
# Helper Function
# =====================================================

def save_chart(fig, filename):
    fig.update_layout(
        template="plotly_white",
        font=dict(size=14),
        title_x=0.5,
        width=1200,
        height=700
    )

    fig.write_image(
        CHARTS_DIR / filename,
        scale=3
    )

    print(f"✓ Saved {filename}")


# =====================================================
# Chart 1 - Revenue by Category
# =====================================================

query = """
SELECT
    product_category,
    ROUND(SUM(price),2) AS revenue
FROM analytics_orders
GROUP BY product_category
ORDER BY revenue DESC
LIMIT 10;
"""

df = pd.read_sql(query, conn)

fig = px.bar(
    df,
    x="product_category",
    y="revenue",
    text_auto=".2s",
    title="Top 10 Product Categories by Revenue"
)

save_chart(fig, "01_category_revenue.png")


# =====================================================
# Chart 2 - Monthly Revenue Trend
# =====================================================

query = """
SELECT
    strftime('%Y-%m', order_purchase_timestamp) AS month,
    ROUND(SUM(price),2) AS revenue
FROM analytics_orders
WHERE order_purchase_timestamp IS NOT NULL
GROUP BY month
HAVING month IS NOT NULL
ORDER BY month;
"""

df = pd.read_sql(query, conn)

fig = px.line(
    df,
    x="month",
    y="revenue",
    markers=True,
    title="Monthly Revenue Trend"
)

save_chart(fig, "02_monthly_revenue.png")


# =====================================================
# Chart 3 - Top Customers
# =====================================================

query = """
SELECT
    customer_unique_id,
    ROUND(SUM(price),2) AS revenue
FROM analytics_orders
GROUP BY customer_unique_id
ORDER BY revenue DESC
LIMIT 10;
"""

df = pd.read_sql(query, conn)

fig = px.bar(
    df,
    x="customer_unique_id",
    y="revenue",
    text_auto=".2s",
    title="Top 10 Customers by Revenue"
)

save_chart(fig, "03_top_customers.png")


# =====================================================
# Chart 4 - Payment Methods
# =====================================================

query = """
SELECT
    payment_type,
    COUNT(DISTINCT order_id) AS orders
FROM analytics_orders
GROUP BY payment_type
ORDER BY orders DESC;
"""

df = pd.read_sql(query, conn)

fig = px.pie(
    df,
    names="payment_type",
    values="orders",
    title="Payment Method Distribution"
)

save_chart(fig, "04_payment_methods.png")


# =====================================================
# Chart 5 - Order Status
# =====================================================

query = """
SELECT
    order_status,
    COUNT(*) AS total_orders
FROM analytics_orders
GROUP BY order_status
ORDER BY total_orders DESC;
"""

df = pd.read_sql(query, conn)

fig = px.bar(
    df,
    x="order_status",
    y="total_orders",
    text_auto=True,
    title="Order Status Distribution"
)

save_chart(fig, "05_order_status.png")


# =====================================================
# Chart 6 - Top Products
# =====================================================

query = """
SELECT
    product_id,
    ROUND(SUM(price),2) AS revenue
FROM analytics_orders
GROUP BY product_id
ORDER BY revenue DESC
LIMIT 10;
"""

df = pd.read_sql(query, conn)

fig = px.bar(
    df,
    x="product_id",
    y="revenue",
    text_auto=".2s",
    title="Top 10 Products by Revenue"
)

save_chart(fig, "06_top_products.png")


# =====================================================
# Close Connection
# =====================================================

conn.close()

print("\nAll charts generated successfully!")