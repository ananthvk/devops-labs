
# Kubernetes Hands-On Exercise Series

### Exercise 1: Hello Pod (Nginx Deployment)

**Goal:** Deploy a simple Nginx-based “storefront” web app on Kubernetes using Minikube.
You’ll run a pod, expose it as a service, and access it in your browser.

## 1. Prerequisites

### A. Install Minikube

Choose your OS and run the corresponding command:

**Linux**

```bash
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

**macOS (Homebrew)**

```bash
brew install minikube
```

**Windows (PowerShell, Administrator)**

```powershell
choco install minikube
```

**WSL (Ubuntu/Debian-based)**

```bash
sudo apt-get update -y
sudo apt-get install -y curl apt-transport-https
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
```

> Ensure **Docker** or a VM driver like **VirtualBox** is installed before starting.

---

## 2. Start Kubernetes Cluster

Start Minikube and confirm it’s running:

```bash
minikube start --nodes=1
kubectl cluster-info
```

Expected output (example):

```bash
Kubernetes control plane is running at https://127.0.0.1:50821
CoreDNS is running at https://127.0.0.1:50821/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy
```

---

## 3. Deploy the Nginx Pod

Create a pod named `hello-k8s` using the official Nginx image:

```bash
kubectl run hello-k8s --image=nginx --port=80
```

Container Port (Target Port): 
The value 80 is configured as the containerPort in the created Pod's specification. 
This tells Kubernetes that the application (nginx in this case) running inside the container is configured to accept traffic on that specific port.

Internal Visibility Only: 
By itself, this flag does not automatically expose the application to external network traffic outside of the Kubernetes cluster.
Pods in Kubernetes get their own internal IP addresses, reachable by other Pods and Services within the same cluster, but not from outside.

Enabling Service Communication:
The primary purpose of specifying the port is to allow Kubernetes Services to correctly route internal cluster traffic to the container. If you later create a Service (e.g., using kubectl expose) to provide a stable IP and external access, the Service will use this port information as its targetPort to direct requests to the correct port on the Pod.


Verify it’s running:

```bash
kubectl get pods
```

Expected output:

```bash
NAME         READY   STATUS    RESTARTS   AGE
hello-k8s    1/1     Running   0          10s
```

---

## 4. Expose the Pod as a Service

Expose your pod so it can be accessed outside the cluster:

```bash
kubectl expose pod hello-k8s --type=NodePort --port=80
```

This command exposes an existing pod so that it can receive external or internal traffic. When you expose a resource (pod in this example), it creates a Service to allow the pod to be accessed via a network endpoint. The service object provides a stable IP and DNS name to access the pod.

Explanation of type:

`ClusterIP` - Default, makes the service accessible only within the cluster (internal only networking)

`NodePort` - Exposes the service on a port on each cluster node, allowing external access via `<NodeIP>:<NodePort>`

`LoadBalancer` - Uses a cloud provider's load balancer to expose the service externally.

`ExternalName` - Maps the service to an external DNS name

Verify the service:

```bash
kubectl get service hello-k8s
```

Expected output:

```bash
NAME         TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
hello-k8s    NodePort   10.96.120.203   <none>        80:30080/TCP   10s
```

---

## 5. Access the Web App

Use Minikube to automatically open the service in your browser:

```bash
minikube service hello-k8s
```

Manual method:
```bash
kubectl get service hello-k8s # Get the assigned port
minikube ip # To get the IP of the node

# This only works within the cluster
kubectl exec -it hello-k8s -- bash
apt update && apt install curl -y   # inside container if not already available
curl http://10.96.120.203
```

Expected behavior:
Your browser opens the default Nginx welcome page — confirming your app is running inside Kubernetes.

---

## 6. Cleanup (Optional)

If you want to remove all created resources:

```bash
kubectl delete service hello-k8s
kubectl delete pod hello-k8s
minikube stop
```

---

### Final Output (Markdown)

```bash
NAME         READY   STATUS    RESTARTS   AGE
hello-k8s    1/1     Running   0          10s

NAME         TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
hello-k8s    NodePort   10.96.120.203   <none>        80:30080/TCP   10s

Opening service hello-k8s in default browser...
```

---
