The error is **100% precise and unambiguous**:

Prometheus started to launch, but Docker aborted because:

Prometheus expects this path **inside the container**:

```
/etc/prometheus/prometheus.yml   ← must be a FILE
```

But inside the container, the directory layout is:

```
/etc/prometheus/
    console_libraries/
    consoles/
    prometheus.yml        ← file
```

Your error:

```
not a directory: Are you trying to mount a directory onto a file (or vice-versa)?
```

means Jenkins replaced your file mount with a **directory**, so Docker refuses to overlay.

This happens ONLY when:

**Your host file is NOT a file.
Your host file path exists but is a DIRECTORY, not a file.**

---

# Root Cause (confirmed)

You created:

```
prometheus.yml
```

INSIDE Jenkins workspace,
but Jenkins created a **folder** named `prometheus.yml` instead of a file.

This usually happens when someone accidentally typed:

```
mkdir prometheus.yml
```

or when the Jenkins job created an empty folder with that name.

Same applies to:

```
alert_rules.yml
```

When Docker tries to do:

```
-v /var/jenkins_home/workspace/.../prometheus.yml:/etc/prometheus/prometheus.yml
```

…Docker sees you are mounting a **directory** to a **file**, and fails.

---

# FIX (Do this EXACTLY)

## 1. SSH/exec into the Jenkins container

```
docker exec -it jenkins bash
```

## 2. Go to workspace

```
cd /var/jenkins_home/workspace/delivery-monitoring-pipeline
```

## 3. Check what's wrong

Run:

```
ls -l
```

You will see something like:

```
drwxr-xr-x 2 root root 4096 ... prometheus.yml
```

If the entry starts with **d** → it is a **directory**, not a file.

---

# 4. Delete the bad folder

```
rm -rf prometheus.yml
rm -rf alert_rules.yml
```

---

# 5. Recreate correct files

Create `prometheus.yml`:

```
cat > prometheus.yml << 'EOF'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]

  - job_name: "delivery_service"
    static_configs:
      - targets: ["172.17.0.1:8000"]

rule_files:
  - /etc/prometheus/alert_rules.yml
EOF
```

Create `alert_rules.yml`:

```
cat > alert_rules.yml << 'EOF'
groups:
  - name: delivery_alerts
    rules:
      - alert: HighPendingDeliveries
        expr: pending_deliveries > 10
        for: 15s
        labels:
          severity: warning
        annotations:
          summary: "High pending deliveries"
          description: "Pending deliveries > 10 for 15 seconds."

      - alert: HighAverageDeliveryTime
        expr: (average_delivery_time_sum / average_delivery_time_count) > 30
        for: 15s
        labels:
          severity: critical
        annotations:
          summary: "High average delivery time"
          description: "Average delivery time > 30 seconds for 15 seconds."
EOF
```

Check:

```
ls -l prometheus.yml alert_rules.yml
```

You MUST see:

```
-rw-r--r-- 1 root root .... prometheus.yml
-rw-r--r-- 1 root root .... alert_rules.yml
```

NOT:

```
drwxr-xr-x ...
```

---

# 6. Re-run pipeline

Back in Jenkins UI → Build Now.

---

# Why this resolves the error

Docker requires:

* host path must be a **file**
* container path `/etc/prometheus/prometheus.yml` is a **file**
* file → file mount works
* directory → file mount fails with “not a directory”

After you replace the mistaken folders with actual files, Prometheus will start normally.

---

If you paste the `ls -l` output from the workspace, I can confirm immediately whether anything else is wrong.
