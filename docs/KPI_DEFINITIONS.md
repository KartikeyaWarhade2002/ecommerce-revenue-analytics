# KPI Definitions

## Table Grain

**1 Row = 1 Order Item**

---

## Revenue

**Definition**

SUM(price)

---

## Freight Cost

**Definition**

SUM(freight_value)

---

## Total Orders

**Definition**

DISTINCTCOUNT(order_id)

---

## Total Customers

**Definition**

DISTINCTCOUNT(customer_unique_id)

---

## Products Sold

**Definition**

COUNT(product_id)

---

## Unique Products

**Definition**

DISTINCTCOUNT(product_id)

---

## Average Order Value (AOV)

**Definition**

Revenue
/
Total Orders

---

## Repeat Customer Rate

**Definition**

Customers with more than one order
/
Total Customers

---

## Delivered Orders

**Definition**

DISTINCTCOUNT(order_id)

WHERE order_status = 'delivered'

---

## Average Delivery Days

**Definition**

AVG(delivery_days)

---

## Average Freight Cost

**Definition**

Freight Cost
/
Total Orders

---

## Payment Method Distribution

**Definition**

COUNT(payment_type)

GROUP BY payment_type

---

## Revenue by Product Category

**Definition**

SUM(price)

GROUP BY product_category_name
