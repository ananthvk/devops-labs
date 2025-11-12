# Exercise 2: Scaling a Flask App on a Single Node using ReplicaSets

## Objective

Simulate a real-world **flash sale** load scenario by scaling a Flask web app using Kubernetes **ReplicaSets**.
You’ll:

1. Deploy a Python Flask app inside Kubernetes.
2. Use ReplicaSets to run multiple identical Pods for scalability and fault tolerance.
3. Scale, delete, and observe auto-healing behavior.

---

## 1. Conceptual Primer (Before Running Anything)

* **Pod:** The smallest deployable unit in Kubernetes (runs one or more containers).
* **ReplicaSet:** Ensures a specified number of identical Pods are always running.
  If a Pod crashes or is deleted, ReplicaSet replaces it automatically.
* **Service:** Provides a stable endpoint (ClusterIP or NodePort) to access the Pods — since Pods have dynamic IPs.

---

## 2. Write the Flask App

Create a new file `app.py`:

```python
from flask import Flask, request
import socket, time, random

app = Flask(__name__)

@app.get("/")
def homepage():
    return {
        "message": "Welcome to Big Sale!",
        "pod": socket.gethostname(),
        "ts": time.time()
    }

@app.get("/buy")
def buy():
    item = random.choice(["Smartphone", "Shoes", "Headphones", "Laptop"])
    user = request.args.get("user", f"user{random.randint(1,1000)}")
    return {
        "status": "success",
        "item": item,
        "user": user,
        "served_by_pod": socket.gethostname(),
        "time": time.strftime("%H:%M:%S")
    }

@app.get("/health")
def health():
    return {"status": "healthy", "pod": socket.gethostname()}
```

**Explanation:**
Each request returns the hostname of the pod that served it. This allows you to visually confirm load balancing between replicas later.

---

## 3. Dockerize the Application

Create a file named `Dockerfile` in the same directory:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY app.py .
RUN pip install --no-cache-dir flask gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app", "--workers", "1", "--threads", "2"]
```

**Explanation:**
We use `gunicorn` (a production-grade WSGI server) instead of Flask’s development server.
`containerPort 5000` will later map to Kubernetes service ports.

---

## 4. Build and Push Docker Image

You can build the image directly inside Minikube (so you don’t need Docker Hub push/pull):

```bash
minikube start --nodes=1
eval $(minikube docker-env)
docker build -t flashsale:1.0 .
```

If you want to use Docker Hub instead (optional):

```bash
docker tag flashsale:1.0 <your-dockerhub-username>/flashsale:1.0
docker push <your-dockerhub-username>/flashsale:1.0
```

**Explanation:**
`eval $(minikube docker-env)` redirects Docker to use Minikube’s internal Docker daemon.
This avoids network upload/download overhead.

---

## 5. Create ReplicaSet and Service Manifest

Create a file named `flashsale-replicaset.yaml`:

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: flashsale-rs
  labels:
    app: flashsale
spec:
  replicas: 3
  selector:
    matchLabels:
      app: flashsale
  template:
    metadata:
      labels:
        app: flashsale
    spec:
      containers:
      - name: flashsale-container
        image: flashsale:1.0
        ports:
        - containerPort: 5000
        readinessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 3
          periodSeconds: 5
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 10
          periodSeconds: 10
        resources:
          requests:
            cpu: "100m"
            memory: "128Mi"
          limits:
            cpu: "500m"
            memory: "256Mi"
---
apiVersion: v1
kind: Service
metadata:
  name: flashsale-svc
spec:
  selector:
    app: flashsale
  ports:
  - name: http
    port: 80
    targetPort: 5000
  type: NodePort
```

**Explanation:**

* `replicas: 3` means Kubernetes will maintain 3 identical Pods.
* `readinessProbe` ensures Pods receive traffic only when ready.
* `livenessProbe` restarts Pods that become unhealthy.
* `Service` of type `NodePort` allows browser access through Minikube’s IP.

---

## 6. Apply the Configuration

```bash
kubectl apply -f flashsale-replicaset.yaml
```

Expected output:

```bash
replicaset.apps/flashsale-rs created
service/flashsale-svc created
```

---

## 7. Verify the ReplicaSet and Pods

```bash
kubectl get rs
kubectl get pods
```

Expected output:

```bash
NAME           DESIRED   CURRENT   READY   AGE
flashsale-rs   3         3         3       40s

NAME                  READY   STATUS    RESTARTS   AGE
flashsale-rs-8gbfp    1/1     Running   0          35s
flashsale-rs-f4gsl    1/1     Running   0          35s
flashsale-rs-nb5kl    1/1     Running   0          35s
```

---

## 8. Access the Application

Find the NodePort:

```bash
kubectl get service flashsale-svc
```

Example output:

```
NAME             TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
flashsale-svc    NodePort   10.96.83.125    <none>        80:30080/TCP   2m
```

Get Minikube IP:

```bash
minikube ip
```

Then access in browser:

```
http://<minikube-ip>:<nodeport>
```

Example: `http://192.168.49.2:30080`

Each refresh will show a different `"pod": "<hostname>"` — proving load balancing across replicas.

---

## 9. Scale the ReplicaSet

```bash
kubectl scale rs flashsale-rs --replicas=5
kubectl get rs
kubectl get pods
```

Expected output:

```bash
NAME           DESIRED   CURRENT   READY   AGE
flashsale-rs   5         5         5       7m38s

NAME                  READY   STATUS    RESTARTS   AGE
flashsale-rs-4nr6q    1/1     Running   0          7m55s
flashsale-rs-84v7x    1/1     Running   0          7m55s
flashsale-rs-nsmlx    1/1     Running   0          32s
flashsale-rs-rbwr4    1/1     Running   0          7m55s
flashsale-rs-wfbb4    1/1     Running   0          32s
```

**Explanation:**
`scale` command adjusts desired replicas. Kubernetes automatically spawns new Pods to match the updated number.

---

## 10. Delete a Pod to Test Self-Healing

```bash
kubectl delete pod flashsale-rs-84v7x
kubectl get pods
```

Expected:

```bash
pod "flashsale-rs-84v7x" deleted

NAME                 READY   STATUS    RESTARTS   AGE
flashsale-rs-4nr6q   1/1     Running   0          9m19s
flashsale-rs-hqtm7   1/1     Running   0          51s
flashsale-rs-nsmlx   1/1     Running   0          116s
flashsale-rs-rbwr4   1/1     Running   0          9m19s
flashsale-rs-wfbb4   1/1     Running   0          116s
```

**Explanation:**
ReplicaSet immediately creates a replacement Pod to maintain `replicas=5`.
This is how Kubernetes ensures fault tolerance.

---

## 11. View Pod Distribution

```bash
kubectl get pods -o wide
```

Output:

```bash
NAME                 READY   STATUS    RESTARTS   AGE     IP            NODE       NOMINATED NODE   READINESS GATES
flashsale-rs-4nr6q   1/1     Running   0          10m     10.244.0.9    minikube   <none>           <none>
flashsale-rs-hqtm7   1/1     Running   0          109s    10.244.0.12   minikube   <none>           <none>
...
```

All Pods are on the **same node (minikube)** since this is a single-node cluster.

---

## 12. Cleanup

```bash
kubectl delete -f flashsale-replicaset.yaml
minikube stop
```

---

## Key Takeaways

| Concept          | Explanation                                                   |
| ---------------- | ------------------------------------------------------------- |
| **Pod**          | Smallest deployable unit that runs a container                |
| **ReplicaSet**   | Maintains a specified number of identical Pods                |
| **Scaling**      | Increasing replicas increases concurrent request capacity     |
| **Self-Healing** | Deleted or failed Pods are recreated automatically            |
| **Service**      | Provides stable access to Pods via internal/external IPs      |
| **Probes**       | Readiness and liveness checks ensure reliability and recovery |

---

### Final Expected Terminal Output (condensed)

```bash
replicaset.apps/flashsale-rs created
service/flashsale-svc created

NAME           DESIRED   CURRENT   READY   AGE
flashsale-rs   5         5         5       7m38s

NAME                 READY   STATUS    RESTARTS   AGE
flashsale-rs-4nr6q   1/1     Running   0          10m
flashsale-rs-hqtm7   1/1     Running   0          109s
flashsale-rs-nsmlx   1/1     Running   0          2m54s
flashsale-rs-rbwr4   1/1     Running   0          10m
flashsale-rs-wfbb4   1/1     Running   0          2m54s
```

---
