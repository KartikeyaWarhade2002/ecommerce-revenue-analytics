## TABLE GRAIN

1 Row = 1 Order Item

---

Revenue
Definition:
SUM(price)

---

Freight Cost
Definition:
SUM(freight_value)

---

Total Orders
Definition:
DISTINCTCOUNT(order_id)

---

Total Customers
Definition:
DISTINCTCOUNT(customer_unique_id)

---

Products Sold
Definition:
COUNT(product_id)

---

Unique Products
Definition:
DISTINCTCOUNT(product_id)

---

Average Order Value

Revenue / Total Orders

---

Repeat Customer Rate

Customers with more than one order
/
Total Customers

---

Delivered Orders

DISTINCTCOUNT(order_id)
WHERE order_status='delivered'
