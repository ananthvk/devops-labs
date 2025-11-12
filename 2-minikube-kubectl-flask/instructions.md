Exercise 3 — Deploy a Flask app on Minikube using kubectl and YAML

Prerequisites (assumed installed): minikube, kubectl, docker (host). If using Linux and Docker driver, have permissions to run docker commands or use sudo.

1. Start Minikube (single-node)

```bash
minikube start
```

Why: boots a single-node Kubernetes cluster locally. Minikube provides a VM/container runtime and a Kubernetes control plane so you can test deployments locally.

Expected (example) lines:

```text
😄  minikube vX.Y.Z on Ubuntu ...
✨  Automatically selected the docker driver
🏄  Done! kubectl is now configured to use "minikube" cluster and "default" namespace by default
```

2. Create the Flask application file (app.py)
   Write this file exactly:

```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return "Hello from Flask on Kubernetes!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=15000)
```

Why: the app listens on 0.0.0.0:15000 so the container accepts connections from any network interface. Port 15000 will be the container's listening port (targetPort).

3. Create Dockerfile
   File: Dockerfile

```dockerfile
FROM python:3.8-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir flask
EXPOSE 15000
CMD ["python", "app.py"]
```

Why: EXPOSE documents the container port. Using a lightweight base keeps the image small. We use the simple python run for learning; in production use a WSGI server.

4. Configure Docker to use Minikube's Docker daemon (recommended — avoids pushing to Docker Hub)

```bash
minikube start            # ensure minikube running
eval $(minikube docker-env)
docker build -t flask-app:latest .
```

Why: `eval $(minikube docker-env)` points your docker CLI to Minikube's internal Docker daemon. Building there makes the image immediately available to Kubernetes in the Minikube cluster without pushing to a public registry.

Expected build output (condensed):

```text
Sending build context to Docker daemon  3.84kB
Step 1/5 : FROM python:3.8-slim
...
Successfully built <IMAGE_ID>
Successfully tagged flask-app:latest
```

5. Deployment + Service manifest (flask-deployment.yaml)
   Create this file exactly:

```yaml
# -----------------------------------------
# Deployment: Defines how to run and manage the Flask app pods
# -----------------------------------------
apiVersion: apps/v1                     # API version used for the Deployment resource (stable version for workloads)
kind: Deployment                        # Kind specifies this resource is a Deployment
metadata:
  name: flask-app                       # Name of the Deployment; must be unique in the namespace
spec:
  replicas: 1                           # Desired number of running pods; ensures at least 1 is always active
  selector:                             # Defines how Kubernetes identifies which pods belong to this Deployment
    matchLabels:                        # Label selector to match pods with the same key-value pair
      app: flask-app                    # Label used to connect Deployment with its pods
  template:                             # Pod template that describes how the Pods should be created
    metadata:
      labels:
        app: flask-app                  # Label assigned to each Pod; must match the selector above
    spec:
      containers:                       # List of containers inside each Pod
      - name: flask-app                 # Container name (used for referencing or debugging)
        image: flask-app:latest         # Docker image to use for the container; locally built in Minikube
        imagePullPolicy: IfNotPresent   # Use local image if available; pull from registry only if missing
        ports:
        - containerPort: 15000          # Exposed port inside the container where Flask listens (matches app.py)

# -----------------------------------------
# Service: Provides stable networking and external access to the pods
# -----------------------------------------
---
apiVersion: v1                          # API version for core Kubernetes objects (Service is part of core/v1)
kind: Service                           # Kind specifies this resource is a Service
metadata:
  name: flask-app-service               # Unique name for the Service within the namespace
spec:
  selector:                             # Determines which pods this Service routes traffic to
    app: flask-app                      # Must match the label defined in the Pod template (links Service -> Pods)
  ports:                                # List of ports to expose for the Service
  - name: http                          # Optional name for the port (used for clarity or referencing)
    port: 15000                         # Port exposed by the Service inside the cluster
    targetPort: 15000                   # Port on the Pod/container that receives the traffic (Flask listening port)
  type: NodePort                        # Exposes the Service externally via a Node port (typically 30000–32767)

# -----------------------------------------
# Explanation Summary:
# 1. The Deployment ensures one Pod (replica) runs the flask-app container.
# 2. The Pod listens on port 15000 internally (containerPort).
# 3. The Service (flask-app-service) exposes the application on the same port (15000),
#    forwarding traffic from the Node’s external port (random high NodePort) to the container port.
# 4. Use "minikube service flask-app-service --url" to get the accessible external URL.
# -----------------------------------------
```

Why:

* `imagePullPolicy: IfNotPresent` is safer than `Never`. If you built inside Minikube, Kubernetes will use the local image; IfNotPresent avoids unnecessary registry pulls while allowing normal behavior when images are remote. Use `Never` only when you explicitly require Kubernetes to never attempt any pull.
* Deployment (not bare Pod) provides rolling updates and easier scaling.
* Service type NodePort exposes the app externally on a node port so you can reach it from the host via Minikube tooling.

6. Apply the manifest

```bash
kubectl apply -f flask-deployment.yaml
```

Expected output:

```text
deployment.apps/flask-app created
service/flask-app-service created
```

7. Validate deployment and pods

```bash
kubectl get deployments
kubectl get pods -l app=flask-app
```

Expected outputs:

```text
# kubectl get deployments
NAME        READY   UP-TO-DATE   AVAILABLE   AGE
flask-app   1/1     1            1           10s

# kubectl get pods -l app=flask-app
NAME                         READY   STATUS    RESTARTS   AGE
flask-app-<hash>             1/1     Running   0          10s
```

Why: ensures the Deployment created a ReplicaSet and Pod; READY 1/1 shows container started.

8. Inspect logs (verify app is serving)

```bash
POD=$(kubectl get pods -l app=flask-app -o jsonpath='{.items[0].metadata.name}')
kubectl logs "$POD"
```

Expected log snippet:

```text
 * Serving Flask app "app"
 * Running on http://127.0.0.1:15000
 * Running on http://10.244.x.y:15000
```

Why: confirms container process started and Flask is listening on expected port inside the Pod.

9. Why curl localhost:15000 fails on host and how to access
   Attempting:

```bash
curl http://127.0.0.1:15000
```

Likely output:

```text
curl: (7) Failed to connect to 127.0.0.1 port 15000: Connection refused
```

Why it fails: Minikube runs the container inside a VM/container network namespace; container ports are not automatically bound to host localhost. You must use Service+NodePort or port-forward to reach the Pod from host.

Two correct access methods:

A) Use Minikube service (recommended for interactive)

```bash
minikube service flask-app-service --url
```

Output example:

```text
http://127.0.0.1:36215
```

Then:

```bash
curl http://127.0.0.1:36215
# returns:
Hello from Flask on Kubernetes!
```

Why: `minikube service --url` finds the NodePort assigned to the service and starts a proxy/local tunnel if needed, exposing a reachable URL on localhost.

B) Port-forward directly to Pod (alternative)

```bash
kubectl port-forward svc/flask-app-service 15000:15000
# in a separate terminal:
curl http://127.0.0.1:15000
# returns:
Hello from Flask on Kubernetes!
```

Why: `kubectl port-forward` creates a local tunnel from host:15000 to service:15000 (or pod). Good for debugging without NodePort.

10. How port, targetPort, containerPort relate

* containerPort: documentation inside Pod spec; indicates which port the container listens on (15000).
* targetPort (Service): the port on the Pod to forward traffic to (15000). Can be numeric or name.
* port (Service): the port the Service exposes inside the cluster (15000). For NodePort the cluster maps an external high-numbered port (e.g., 36215) to this service port.
  Why: this mapping lets services route traffic to dynamically assigned Pod IPs and ports.

11. Scale the Deployment

```bash
kubectl scale deployment flask-app --replicas=3
kubectl get pods -l app=flask-app
```

Expected:

```text
deployment.apps/flask-app scaled
# pods:
NAME                         READY   STATUS    RESTARTS   AGE
flask-app-aaa                1/1     Running   0          10s
flask-app-bbb                1/1     Running   0          9s
flask-app-ccc                1/1     Running   0          8s
```

Why: scaling creates additional Pods so Kubernetes can serve more concurrent requests. The Service load-balances across Pods.

12. Confirm load distribution (simple check)
    Obtain the NodePort URL:

```bash
URL=$(minikube service flask-app-service --url)
for i in $(seq 1 6); do curl -s $URL; echo; done
```

Each response should be identical string; for more advanced confirmation you could modify the app to return the Pod hostname (useful to see different pods serve different requests).

13. Cleanup

```bash
kubectl delete -f flask-deployment.yaml
minikube stop
minikube delete
```

Why: removes cluster resources and stops Minikube.

Troubleshooting notes

* If image not found: ensure you built inside Minikube or pushed to a registry and updated `image` in YAML to `<user>/flask-app:tag` and set `imagePullPolicy: IfNotPresent` or `Always` depending on need.
* To use Docker Hub: `docker build -t <user>/flask-app:1.0 . && docker push <user>/flask-app:1.0` then update YAML image to `<user>/flask-app:1.0`.
* If `minikube service ... --url` returns localhost but curl fails: ensure the terminal running `minikube`/docker driver remains open when required, or use `minikube tunnel` for LoadBalancer services.

Minimal expected terminal transcript (condensed)

```bash
minikube start
eval $(minikube docker-env)
docker build -t flask-app:latest .
kubectl apply -f flask-deployment.yaml
deployment.apps/flask-app created
service/flask-app-service created
kubectl get pods
NAME                         READY   STATUS    RESTARTS   AGE
flask-app-<hash>             1/1     Running   0          20s
minikube service flask-app-service --url
http://127.0.0.1:36215
curl http://127.0.0.1:36215
Hello from Flask on Kubernetes!
kubectl scale deployment flask-app --replicas=3
deployment.apps/flask-app scaled
kubectl get pods
# shows 3 running pods
kubectl delete -f flask-deployment.yaml
```