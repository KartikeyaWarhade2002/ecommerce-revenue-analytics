import sqlite3
import pandas as pd

# =====================================================
# Connect to SQLite
# =====================================================

DB_PATH = "data/ecommerce.db"

conn = sqlite3.connect(DB_PATH)

print("=" * 100)
print("E-COMMERCE REVENUE ANALYTICS")
print("=" * 100)

# =====================================================
# Query 1
# Top Revenue Products
# =====================================================

query_1 = """
SELECT
    product_id,
    product_category,
    ROUND(SUM(price), 2) AS revenue
FROM analytics_orders
GROUP BY product_id, product_category
ORDER BY revenue DESC
LIMIT 10;
"""

top_products = pd.read_sql_query(query_1, conn)

print("\nTOP 10 REVENUE PRODUCTS")
print("-" * 80)
print(top_products)

# =====================================================
# Query 2
# Revenue by Category
# =====================================================

query_2 = """
SELECT
    product_category,
    ROUND(SUM(price), 2) AS revenue
FROM analytics_orders
GROUP BY product_category
ORDER BY revenue DESC;
"""

category_revenue = pd.read_sql_query(query_2, conn)

print("\nCATEGORY REVENUE")
print("-" * 80)
print(category_revenue.head(10))

# =====================================================
# Query 3
# Top Customers
# =====================================================

query_3 = """
SELECT
    customer_unique_id,
    customer_city,
    customer_state,
    ROUND(SUM(price), 2) AS total_spent
FROM analytics_orders
GROUP BY
    customer_unique_id,
    customer_city,
    customer_state
ORDER BY total_spent DESC
LIMIT 10;
"""

top_customers = pd.read_sql_query(query_3, conn)

print("\nTOP CUSTOMERS")
print("-" * 80)
print(top_customers)

# =====================================================
# Query 4
# Monthly Revenue
# =====================================================

query_4 = """
SELECT
    strftime('%Y-%m', order_purchase_timestamp) AS month,
    ROUND(SUM(price), 2) AS revenue
FROM analytics_orders
GROUP BY month
ORDER BY month;
"""

monthly_revenue = pd.read_sql_query(query_4, conn)

print("\nMONTHLY REVENUE")
print("-" * 80)
print(monthly_revenue)

# =====================================================
# Query 5
# Average Order Value
# =====================================================

query_5 = """
SELECT
    ROUND(AVG(order_total), 2) AS average_order_value
FROM
(
    SELECT
        order_id,
        SUM(price) AS order_total
    FROM analytics_orders
    GROUP BY order_id
);
"""

aov = pd.read_sql_query(query_5, conn)

print("\nAVERAGE ORDER VALUE")
print("-" * 80)
print(aov)

# =====================================================
# Query 6
# Repeat Customer Rate
# =====================================================

query_6 = """
SELECT
ROUND(
100.0 *
SUM(CASE WHEN order_count > 1 THEN 1 ELSE 0 END)
/
COUNT(*),
2
) AS repeat_customer_rate
FROM
(
SELECT
customer_unique_id,
COUNT(DISTINCT order_id) AS order_count
FROM analytics_orders
GROUP BY customer_unique_id
);
"""

repeat_rate = pd.read_sql_query(query_6, conn)

print("\nREPEAT CUSTOMER RATE")
print("-" * 80)
print(repeat_rate)

# =====================================================
# Query 7
# Payment Method
# =====================================================

query_7 = """
SELECT
payment_type,
COUNT(DISTINCT order_id) AS orders,
ROUND(SUM(payment_value),2) AS revenue
FROM analytics_orders
GROUP BY payment_type
ORDER BY revenue DESC;
"""

payment_analysis = pd.read_sql_query(query_7, conn)

print("\nPAYMENT METHOD ANALYSIS")
print("-" * 80)
print(payment_analysis)

# =====================================================
# Query 8
# Order Status
# =====================================================

query_8 = """
SELECT
    order_status,
    COUNT(DISTINCT order_id) AS total_orders
FROM analytics_orders
GROUP BY order_status
ORDER BY total_orders DESC;
"""

order_status = pd.read_sql_query(query_8, conn)

print("\nORDER STATUS")
print("-" * 80)
print(order_status)

# =====================================================
# Close Connection
# =====================================================

conn.close()

print("\nAnalysis Complete.")