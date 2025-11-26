Here is the **exact, literal, step-by-step procedure**, including every click, every button, and exactly where to type the query for the *Average Delivery Time* panel.
Do this exactly as written and the panel will work.

---

# Create Panel 4 — **Average Delivery Time**

## **1. Open your dashboard**

In Grafana left sidebar:

**Dashboards → Manage → Click your dashboard (Delivery Monitoring Dashboard)**

Your existing panels will appear.

---

## **2. Add a new panel**

Top-right corner:

**Click “Add panel” → Click “Add new panel”**

This opens the panel editor.

You now see:

* Graph area (empty)
* Query section at the bottom

---

## **3. Select the data source**

If it does not auto-select:

In top-left of the query section:

Dropdown → choose **Prometheus**

---

## **4. Enter the exact PromQL expression**

In the query editor box that shows something like `A | Query | Metrics Browser`:

Click inside the **Query A** input field.

Type this EXACTLY:

```
average_delivery_time_sum / average_delivery_time_count
```

Press **Enter**.

---

## **5. Wait for the graph to load**

You will immediately see the plotted result.

If your Python app is running you will see a line with values between ~15–45.

---

## **6. Name and apply the panel**

Top-right:

**Click “Apply”**

A sidebar appears to enter panel title.

In the “Title” field, type:

```
Average Delivery Time
```

Click **Apply**.

---

## **7. Save the dashboard**

Top-right:

**Click “Save dashboard” → Save**

---

# Result

Your Panel 4 now correctly shows:

`average_delivery_time_sum / average_delivery_time_count`

This is the runtime average from the Prometheus Summary metric.

Done.


You’re in the Grafana “Builder” mode and you’ve put the whole expression into the Metric dropdown.
Builder is treating it as a single metric name (wrapped like `{"average_delivery_time_sum / average_delivery_time_count"}`), which doesn’t exist → “no data”.

You must switch to raw PromQL “Code” mode and type the expression there.

Do this exactly:

1. Open the panel editor for this panel

   * On the dashboard, hover the panel → click the panel title → Edit

2. In the query section (where your screenshot is):

   * On the right side of the query header line you will see:
     `Builder | Code`
   * Click `Code`

3. Now you’ll see a plain text PromQL editor instead of the Metric dropdown.

   * Delete everything that is currently in the query box.
   * Type this EXACTLY (no braces, no quotes):

   ```
   average_delivery_time_sum / average_delivery_time_count
   ```

4. Top-right of the query area:

   * Click `Run queries`

5. Confirm you see a line in the graph.

   * If you see data, the query is correct.

6. Apply the panel:

   * Top-right of the panel editor → click `Apply`
   * Set Title to: `Average Delivery Time`
   * Click `Apply` again to return to the dashboard.

If it still shows no data after that, verify the metric actually exists in Prometheus:

1. Open Prometheus UI: `http://localhost:9090/graph`

2. In the “Expression” box type:

   ```
   average_delivery_time_sum
   ```

3. Click `Execute`.

   * If you see time series, the metric is present.
   * Then try:

   ```
   average_delivery_time_sum / average_delivery_time_count
   ```

If Prometheus shows data but Grafana doesn’t, the only issue will be how the query is entered in Grafana; entering it in `Code` mode as above fixes it.
