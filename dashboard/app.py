"""
E-Commerce Analytics Dashboard
Built with Streamlit — reads analytics_orders.csv (order/item/customer/product/payment level data)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ----------------------------------------------------------------------------
# Page config
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = "D:/Data Analytics Projects/ecommerce-revenue-analytics/data/processed/analytics_orders.csv"

# ----------------------------------------------------------------------------
# Data loading
# ----------------------------------------------------------------------------
@st.cache_data
def load_data(path):
    df = pd.read_csv(path)

    date_cols = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
        "shipping_limit_date",
    ]
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Derived fields
    df["order_year"] = df["order_purchase_timestamp"].dt.year
    df["order_month"] = df["order_purchase_timestamp"].dt.to_period("M").astype(str)
    df["order_date"] = df["order_purchase_timestamp"].dt.date
    df["order_dow"] = df["order_purchase_timestamp"].dt.day_name()

    # Delivery time in days (purchase -> delivered to customer)
    df["delivery_days"] = (
        df["order_delivered_customer_date"] - df["order_purchase_timestamp"]
    ).dt.total_seconds() / 86400

    # Delivery vs estimate (negative = early, positive = late)
    df["delivery_delta_days"] = (
        df["order_delivered_customer_date"] - df["order_estimated_delivery_date"]
    ).dt.total_seconds() / 86400

    df["product_category"] = df["product_category"].fillna("unknown")
    df["customer_state"] = df["customer_state"].fillna("unknown")
    df["payment_type"] = df["payment_type"].fillna("unknown")

    # Data-quality flag: order_status says "delivered" but no delivery timestamp
    # was ever recorded. We do NOT fabricate a date for these — they're kept as
    # NaN in delivery_days / delivery_delta_days (correctly excluded from any
    # delivery-time math) and instead surfaced explicitly so they're never a
    # silent mystery in an export.
    df["flag_delivered_missing_date"] = (
        (df["order_status"] == "delivered") & (df["order_delivered_customer_date"].isna())
    )

    return df


try:
    df_raw = load_data(DATA_PATH)
except FileNotFoundError:
    st.error(
        f"Could not find `{DATA_PATH}`. Place `analytics_orders.csv` in the same "
        "folder as this app, or update DATA_PATH at the top of app.py."
    )
    st.stop()

# ----------------------------------------------------------------------------
# Sidebar filters
# ----------------------------------------------------------------------------
st.sidebar.title("🔎 Filters")

min_date = df_raw["order_purchase_timestamp"].min().date()
max_date = df_raw["order_purchase_timestamp"].max().date()

date_range = st.sidebar.date_input(
    "Order date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

states = sorted(df_raw["customer_state"].dropna().unique().tolist())
selected_states = st.sidebar.multiselect("Customer state", options=states, default=[])

categories = sorted(df_raw["product_category"].dropna().unique().tolist())
selected_categories = st.sidebar.multiselect("Product category", options=categories, default=[])

payment_types = sorted(df_raw["payment_type"].dropna().unique().tolist())
selected_payments = st.sidebar.multiselect("Payment type", options=payment_types, default=[])

order_statuses = sorted(df_raw["order_status"].dropna().unique().tolist())
selected_statuses = st.sidebar.multiselect("Order status", options=order_statuses, default=[])

st.sidebar.markdown("---")
st.sidebar.caption(f"Dataset: {len(df_raw):,} order-item rows")
st.sidebar.caption(f"Range: {min_date} → {max_date}")

# Apply filters
df = df_raw[
    (df_raw["order_purchase_timestamp"].dt.date >= start_date)
    & (df_raw["order_purchase_timestamp"].dt.date <= end_date)
]
if selected_states:
    df = df[df["customer_state"].isin(selected_states)]
if selected_categories:
    df = df[df["product_category"].isin(selected_categories)]
if selected_payments:
    df = df[df["payment_type"].isin(selected_payments)]
if selected_statuses:
    df = df[df["order_status"].isin(selected_statuses)]

if df.empty:
    st.warning("No data matches the selected filters. Adjust filters in the sidebar.")
    st.stop()

# ----------------------------------------------------------------------------
# Order-level view
# ----------------------------------------------------------------------------
# `df` is item-level: one row per order-item. Fields like payment_value,
# payment_installments, payment_type, order_status, and the delivery dates are
# order-level facts that get duplicated onto every item-row of a multi-item
# order. Summing or averaging those fields directly on `df` silently multiplies
# every order that has more than one item. `price` and `freight_value` ARE
# genuinely per-item and are safe to sum on `df` directly.
# Use `orders_df` (one row per order) for anything order-level; keep using
# `df` for anything genuinely item-level (price, freight, product attributes).
orders_df = df.drop_duplicates(subset="order_id").copy()

# ----------------------------------------------------------------------------
# Header
# ----------------------------------------------------------------------------
st.title("📊 E-Commerce Analytics Dashboard")
st.caption(
    f"Showing {len(df):,} order items · {df['order_id'].nunique():,} orders · "
    f"{start_date} to {end_date}"
)

# ----------------------------------------------------------------------------
# Data-quality callout (only appears if the current filter contains anomalies)
# ----------------------------------------------------------------------------
dq_count = int(orders_df["flag_delivered_missing_date"].sum())
if dq_count > 0:
    with st.expander(
        f"⚠️ Data quality note: {dq_count} order(s) marked delivered with no delivery date on record",
        expanded=False,
    ):
        st.write(
            "These orders have order_status = delivered but their "
            "order_delivered_customer_date was never recorded in the source data. "
            "No date has been invented for them, since that would quietly distort "
            "every delivery-time chart. Instead they are:"
        )
        st.markdown(
            "- Included in revenue, order counts, and the Delivered % KPI "
            "(the order itself is real and marked complete)\n"
            "- Excluded from delivery_days, delivery_delta_days, and every "
            "chart built from them, since there is nothing to measure without a date\n"
            "- Flagged in a flag_delivered_missing_date column, visible in "
            "the Raw Data tab and included in CSV exports"
        )
        flag_cols = [
            "order_id", "order_status", "order_purchase_timestamp", "order_approved_at",
            "order_delivered_carrier_date", "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ]
        st.dataframe(
            orders_df.loc[orders_df["flag_delivered_missing_date"], flag_cols],
            use_container_width=True,
        )

# ----------------------------------------------------------------------------
# KPI row
# ----------------------------------------------------------------------------
total_revenue = df["price"].sum()  # price is per-item — safe to sum on df
total_orders = df["order_id"].nunique()
avg_order_value = total_revenue / total_orders  # revenue ÷ orders — matches standard AOV definition
unique_customers = df["customer_unique_id"].nunique()
avg_delivery_days = orders_df["delivery_days"].mean()  # order-level, not item-weighted
delivered_pct = (orders_df["order_status"] == "delivered").mean() * 100  # order-level, not item-weighted

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Total Revenue", f"${total_revenue:,.0f}")
k2.metric("Total Orders", f"{total_orders:,}")
k3.metric("Avg Order Value", f"${avg_order_value:,.2f}")
k4.metric("Unique Customers", f"{unique_customers:,}")
k5.metric(
    "Avg Delivery Time",

    f"{avg_delivery_days:,.1f} days",
    help=f"Calculated only from orders with a recorded delivery date. "
         f"{dq_count} delivered order(s) with no delivery date are excluded from this average.",
)
k6.metric(
    "Delivered %",
    f"{delivered_pct:,.1f}%",
    help=f"Based on order_status. Includes {dq_count} order(s) marked delivered "
         "that are missing a delivery timestamp (see data quality note above).",
)

st.markdown("---")

# ----------------------------------------------------------------------------
# Tabs
# ----------------------------------------------------------------------------
tab_sales, tab_products, tab_geo, tab_ops, tab_customers, tab_data = st.tabs(
    ["💰 Sales", "📦 Products", "🗺️ Geography", "🚚 Operations", "👥 Customers", "📄 Raw Data"]
)

# ---- SALES TAB ---------------------------------------------------------
with tab_sales:
    col1, col2 = st.columns((2, 1))

    with col1:
        st.subheader("Revenue Over Time")
        monthly = (
            df.groupby("order_month")
            .agg(revenue=("price", "sum"), orders=("order_id", "nunique"))
            .reset_index()
            .sort_values("order_month")
        )
        fig = px.line(
            monthly, x="order_month", y="revenue", markers=True,
            labels={"order_month": "Month", "revenue": "Revenue ($)"},
        )
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Payment Types")
        pay_counts = df.groupby("payment_type")["order_id"].nunique().reset_index()
        pay_counts.columns = ["payment_type", "orders"]
        fig = px.pie(pay_counts, names="payment_type", values="orders", hole=0.45)
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Orders by Day of Week")
        dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        dow_counts = df.groupby("order_dow")["order_id"].nunique().reindex(dow_order).reset_index()
        dow_counts.columns = ["day", "orders"]
        fig = px.bar(dow_counts, x="day", y="orders")
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        st.subheader("Order Status Breakdown")
        status_counts = df.groupby("order_status")["order_id"].nunique().reset_index()
        status_counts.columns = ["status", "orders"]
        status_counts = status_counts.sort_values("orders", ascending=True)
        fig = px.bar(status_counts, x="orders", y="status", orientation="h")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Installments Distribution")
    inst = orders_df["payment_installments"].value_counts().sort_index().reset_index()
    inst.columns = ["installments", "count"]
    fig = px.bar(inst, x="installments", y="count", labels={"count": "Orders"})
    st.plotly_chart(fig, use_container_width=True)

# ---- PRODUCTS TAB -------------------------------------------------------
with tab_products:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top 15 Categories by Revenue")
        cat_rev = (
            df.groupby("product_category")["price"]
            .sum()
            .sort_values(ascending=False)
            .head(15)
            .reset_index()
        )
        fig = px.bar(cat_rev, x="price", y="product_category", orientation="h",
                     labels={"price": "Revenue ($)", "product_category": "Category"})
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Top 15 Categories by Order Volume")
        cat_vol = (
            df.groupby("product_category")["order_id"]
            .nunique()
            .sort_values(ascending=False)
            .head(15)
            .reset_index()
        )
        cat_vol.columns = ["product_category", "orders"]
        fig = px.bar(cat_vol, x="orders", y="product_category", orientation="h")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Price Distribution by Category (Top 10 by volume)")
    top10 = df["product_category"].value_counts().head(10).index
    fig = px.box(df[df["product_category"].isin(top10)], x="product_category", y="price")
    fig.update_layout(xaxis_title="Category", yaxis_title="Price ($)")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Avg Price vs Avg Freight by Category (Top 15 by volume)")
    top15 = df["product_category"].value_counts().head(15).index
    pf = df[df["product_category"].isin(top15)].groupby("product_category").agg(
        avg_price=("price", "mean"), avg_freight=("freight_value", "mean")
    ).reset_index()
    fig = go.Figure()
    fig.add_bar(name="Avg Price", x=pf["product_category"], y=pf["avg_price"])
    fig.add_bar(name="Avg Freight", x=pf["product_category"], y=pf["avg_freight"])
    fig.update_layout(barmode="group", xaxis_title="Category", yaxis_title="$")
    st.plotly_chart(fig, use_container_width=True)

# ---- GEOGRAPHY TAB -------------------------------------------------------
with tab_geo:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Revenue by State")
        state_rev = df.groupby("customer_state")["price"].sum().sort_values(ascending=False).reset_index()
        fig = px.bar(state_rev, x="customer_state", y="price",
                     labels={"customer_state": "State", "price": "Revenue ($)"})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Orders by State")
        state_orders = df.groupby("customer_state")["order_id"].nunique().sort_values(ascending=False).reset_index()
        state_orders.columns = ["customer_state", "orders"]
        fig = px.bar(state_orders, x="customer_state", y="orders",
                     labels={"customer_state": "State"})
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Top 15 Cities by Order Volume")
    city_orders = (
        df.groupby("customer_city")["order_id"]
        .nunique()
        .sort_values(ascending=False)
        .head(15)
        .reset_index()
    )
    city_orders.columns = ["city", "orders"]
    fig = px.bar(city_orders, x="orders", y="city", orientation="h")
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

# ---- OPERATIONS TAB -------------------------------------------------------
with tab_ops:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Delivery Time Distribution (days)")
        delivered = orders_df.dropna(subset=["delivery_days"])
        delivered = delivered[(delivered["delivery_days"] >= 0) & (delivered["delivery_days"] <= 60)]
        fig = px.histogram(delivered, x="delivery_days", nbins=40)
        fig.update_layout(xaxis_title="Delivery time (days)", yaxis_title="Orders")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("On-Time vs Late Deliveries")
        delta = orders_df.dropna(subset=["delivery_delta_days"]).copy()
        delta["on_time"] = delta["delivery_delta_days"].apply(lambda x: "Late" if x > 0 else "On time / early")
        counts = delta["on_time"].value_counts().reset_index()
        counts.columns = ["status", "orders"]
        fig = px.pie(counts, names="status", values="orders", hole=0.45,
                     color="status", color_discrete_map={"Late": "#e74c3c", "On time / early": "#2ecc71"})
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Avg Delivery Time by State")
    state_delivery = orders_df.dropna(subset=["delivery_days"]).groupby("customer_state")["delivery_days"].mean().sort_values(ascending=False).reset_index()
    fig = px.bar(state_delivery, x="customer_state", y="delivery_days",
                 labels={"customer_state": "State", "delivery_days": "Avg delivery (days)"})
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Freight Value vs Product Weight")
    sample = df.dropna(subset=["product_weight_g", "freight_value"])
    if len(sample) > 5000:
        sample = sample.sample(5000, random_state=42)
    fig = px.scatter(sample, x="product_weight_g", y="freight_value", opacity=0.4,
                      labels={"product_weight_g": "Product weight (g)", "freight_value": "Freight ($)"})
    st.plotly_chart(fig, use_container_width=True)

# ---- CUSTOMERS TAB -------------------------------------------------------
with tab_customers:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Orders per Customer")
        cust_orders = df.groupby("customer_unique_id")["order_id"].nunique()
        repeat_rate = (cust_orders > 1).mean() * 100
        st.metric("Repeat Customer Rate", f"{repeat_rate:.1f}%")
        dist = cust_orders.value_counts().sort_index().head(10).reset_index()
        dist.columns = ["orders_per_customer", "num_customers"]
        fig = px.bar(dist, x="orders_per_customer", y="num_customers")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Top 10 Customers by Spend")
        top_cust = (
            orders_df.groupby("customer_unique_id")["payment_value"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
            .reset_index()
        )
        top_cust["customer_unique_id"] = top_cust["customer_unique_id"].str[:8] + "…"
        fig = px.bar(top_cust, x="payment_value", y="customer_unique_id", orientation="h",
                     labels={"payment_value": "Total spend ($)", "customer_unique_id": "Customer"})
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig, use_container_width=True)

# ---- RAW DATA TAB -------------------------------------------------------
with tab_data:
    st.subheader("Filtered Data")

    st.dataframe(df, use_container_width=True, height=500)
    st.caption(
        f"{len(df):,} rows shown · flag_delivered_missing_date column marks orders "
        "with order_status = delivered but no order_delivered_customer_date on record."
    )

    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download filtered data as CSV",
        data=csv_bytes,
        file_name="filtered_orders.csv",
        mime="text/csv",
    )