Grafana dashboard creation is not intuitive for beginners. Here is the exact, **click-by-click**, **type-exactly-this** procedure to create all four panels.

This produces a working dashboard every time.

# Create the Grafana Dashboard and Panels

---

# 1. Open Grafana

In your browser:

```
http://localhost:3000
```

Login:

```
Username: admin
Password: admin
```

---

# 2. Create a New Dashboard

Left-sidebar → **Dashboards**
Top-right → **New → New Dashboard**

You will now see an empty dashboard with one panel placeholder.

---

# 3. Create Panel 1 — total_deliveries

### Step A — Click "Add visualization"

Click **Add visualization**.

### Step B — Select Data Source

You will see a list of data sources.
Click **Prometheus**.

### Step C — Enter the query

In the query editor, type:

```
total_deliveries
```

Press **Enter** or click outside.

You will see a graph with values.

### Step D — Save the panel

Top-right:
Click **Apply** → Name the panel:

```
Total Deliveries
```

Click **Save**.

---

# 4. Create Panel 2 — pending_deliveries

### Step A — Add new panel

Top-right → **Add panel** → **Add new panel**

### Step B — Enter query

```
pending_deliveries
```

### Step C — Save panel

Click **Apply** → Name it:

```
Pending Deliveries
```

---

# 5. Create Panel 3 — on_the_way_deliveries

### Add new panel:

Top-right → **Add panel** → **Add new panel**

### Query:

```
on_the_way_deliveries
```

### Save:

Apply → Name:

```
On The Way Deliveries
```

---

# 6. Create Panel 4 — Average Delivery Time

This uses the Summary type:

* Prometheus automatically creates:
  `average_delivery_time_sum`
  `average_delivery_time_count`

The average is:

```
average_delivery_time_sum / average_delivery_time_count
```

### Add new panel:

**Add panel → Add new panel**

### Query:

```
average_delivery_time_sum / average_delivery_time_count
```

### Save:

Apply → Name:

```
Average Delivery Time
```

---

# 7. Save the Whole Dashboard

Top-right → **Save Dashboard**
Name:

```
Delivery Monitoring Dashboard
```

Click **Save**.

---

# Dashboard is Ready

You now have a 4-panel real-time dashboard:

* Total Deliveries
* Pending Deliveries
* On-The-Way Deliveries
* Average Delivery Time (derived metric)

All panels auto-update every scrape interval (default 15 seconds).

Done.