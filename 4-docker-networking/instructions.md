# Docker Networking Exercise

## Objective

Understand **Docker networking** concepts by configuring and testing communication between multiple containers —
a **Flask web app**, a **MySQL database**, and a **Redis cache** — all connected through a **user-defined bridge network.**

---

## Scenario Overview

We will create a **multi-container system** where:

1. A **Flask** app serves an API endpoint (`/about`).
2. A **MySQL** container acts as a backend database.
3. A **Redis** container acts as an in-memory cache.

All containers will communicate internally through a **custom bridge network** named `my-bridge-net`.

---

## Step-by-Step Implementation

---

### **Task 1: Create a Bridge Network**

Create a custom user-defined bridge network:

```bash
docker network create --driver bridge my-bridge-net
```

**Explanation:**

* `--driver bridge`: specifies the network driver.
* `my-bridge-net`: your custom network name.
* Bridge networks allow containers to communicate securely within an isolated subnet.

**Example Output:**

```
87c23b491f5994c74e497f4f4f4f4f4f4f4f4
```

---

### **Task 2: Verify the Network**

List all available Docker networks:

```bash
docker network ls
```

**Expected Output:**

```
NETWORK ID     NAME            DRIVER    SCOPE
87c23b491f59   my-bridge-net   bridge    local
```

**Explanation:**
This confirms that the new network has been created.
The `DRIVER` column shows it's a **bridge** network, meaning Docker has assigned it a private IP range.

---

### **Task 3: Inspect the Network**

Inspect detailed configuration for `my-bridge-net`:

```bash
docker network inspect my-bridge-net
```

**Expected Output (shortened for clarity):**

```json
[
    {
        "Name": "my-bridge-net",
        "Id": "87c23b491f5994c74e497f4f4f4f4f4f4f4f4",
        "Driver": "bridge",
        "IPAM": {
            "Config": [
                {
                    "Subnet": "172.18.0.0/16",
                    "Gateway": "172.18.0.1"
                }
            ]
        },
        "Containers": {}
    }
]
```

**Explanation:**

* Each bridge network is given its own subnet (e.g., `172.18.0.0/16`).
* Containers connected to this network will receive IP addresses within this range.
* The gateway (usually `.1`) acts as the network’s default router.

---

### **Task 4: Launch Containers**

We’ll now build a **Flask container** and connect it, along with MySQL and Redis, to the same bridge network.

---

#### **A. Flask Application**

**1. Create `app.py`:**

```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/about', methods=['GET'])
def about():
    return jsonify({
        "name": "Simple REST API",
        "version": "1.0",
        "description": "This is a simple REST API built with Flask."
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001)
```

**Explanation:**
This is a minimal Flask REST API that runs on port **5001** and returns metadata in JSON format when accessed at `/about`.

---

**2. Create `requirements.txt`:**

```
Flask==2.0.1
```

**Explanation:**
Flask is the only dependency required for this project.

---

**3. Create `Dockerfile`:**

```Dockerfile
# Use the official lightweight Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy dependencies and source code
COPY requirements.txt .
COPY app.py .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port used by Flask
EXPOSE 5001

# Define container startup command
CMD ["python", "app.py"]
```

**Explanation:**

* `FROM python:3.9-slim`: lightweight base image for smaller builds.
* `WORKDIR /app`: sets the container’s working directory.
* `RUN pip install`: installs required dependencies.
* `EXPOSE 5001`: informs Docker which port the app listens on (for documentation purposes).
* `CMD`: starts the Flask server when the container runs.

---

#### **B. Build the Flask Image**

```bash
docker build -t flask-api .
```

**Explanation:**
This command builds a Docker image named `flask-api` using the current directory (`.`) as build context.

**Expected Output (truncated):**

```
Sending build context to Docker daemon  3.584kB
Step 1/5 : FROM python:3.9-slim
...
Successfully tagged flask-api:latest
```

---

#### **C. Run All Containers**

Now run **MySQL**, **Redis**, and **Flask** containers on the same network.

```bash
docker run -d --name mysql --net=my-bridge-net mysql:latest
docker run -d --name redis --net=my-bridge-net redis:latest
docker run -d --name flask --net=my-bridge-net -p 5001:5001 flask-api
```

**Explanation:**

* `-d`: run in detached (background) mode.
* `--name`: assigns a container name for easier access.
* `--net=my-bridge-net`: connects the container to our bridge network.
* `-p 5001:5001`: maps the Flask app’s port 5001 inside the container to port 5001 on your host (so you can access it via browser or curl).

**Expected Output (container IDs):**

```
237c941f4f4f
456c941f4f4f
678c941f4f4f
```

---

### **Task 5: Test Connectivity Between Containers**

#### **A. Exec into the Flask Container**

```bash
docker exec -it flask bash
```

This opens a terminal inside the running Flask container.

---

#### **B. Ping the MySQL Container**

```bash
ping mysql
```

**Expected Output:**

```
PING mysql (172.18.0.2) 56(84) bytes of data.
64 bytes from mysql (172.18.0.2): icmp_seq=1 ttl=64 time=0.078 ms
```

**Explanation:**
Docker’s embedded DNS automatically resolves container names to their IPs when on the same network.

---

#### **C. Ping the Redis Container**

```bash
ping redis
```

**Expected Output:**

```
PING redis (172.18.0.3) 56(84) bytes of data.
64 bytes from redis (172.18.0.3): icmp_seq=1 ttl=64 time=0.078 ms
```

**Explanation:**
Since both containers share the same bridge network, the Flask container can directly reach Redis and MySQL via container names.
You could also connect to MySQL or Redis using their service names in an actual Flask app configuration.

---

### **Task 6: Access Flask API**

Exit from the Flask container shell (`exit`) and test from your host machine:

```bash
curl http://localhost:5001/about
```

**Expected Output:**

```json
{
  "name": "Simple REST API",
  "version": "1.0",
  "description": "This is a simple REST API built with Flask."
}
```

---

### **Task 7: Cleanup**

After completing the exercise, remove everything to free resources.

#### Stop and Remove Containers

```bash
docker stop mysql redis flask
docker rm mysql redis flask
```

#### Remove the Network

```bash
docker network rm my-bridge-net
```

**Expected Output:**

```
my-bridge-net
```

#### (Optional) Remove the Flask Image

```bash
docker rmi flask-api
```

**Explanation:**
This ensures no unused images or networks remain, keeping your system clean.

---

## **Q&A Section**

**Q1. What is the purpose of the `--net` flag in `docker run`?**
**A1:** The `--net` flag specifies which network the container should connect to.
In this exercise, it connects containers to the custom bridge network `my-bridge-net`, allowing them to communicate by name.

---

**Q2. How do containers communicate with each other on the same network?**
**A2:** Containers on the same bridge network communicate using their **container names** as DNS hostnames.
For example, `ping mysql` works because Docker’s internal DNS resolves `mysql` to its internal IP (e.g., `172.18.0.2`).

---

**Q3. What is the difference between a bridge network and a host network?**
**A3:**

* **Bridge Network:** Containers have their own internal IPs and communicate through Docker’s virtual bridge. It isolates containers from the host.
* **Host Network:** Containers share the host’s network stack, meaning ports and interfaces are the same as the host machine’s.

**Analogy:**

* Bridge → Containers are in their own private room, talking through an internal router.
* Host → Containers are in the same room as the host, directly sharing the space.

---

**Q4. How can you expose a container's port to the host machine?**
**A4:** By using the `-p` flag in `docker run`.
For example:

```bash
docker run -p 5001:5001 flask-api
```

This maps **host port 5001** → **container port 5001**, allowing access via `http://localhost:5001`.

---

**Q5. Why use a user-defined bridge instead of the default one?**
**A5:**

* User-defined bridges provide **built-in DNS resolution** by container name.
* They offer better **isolation and control** over IP ranges and subnets.
* Default `bridge` requires manual linking or IP-based communication.

---

**Q6. How can you see which containers are attached to a specific network?**
**A6:**
Use:

```bash
docker network inspect my-bridge-net
```

The `"Containers"` section lists all containers connected, along with their IPs.

---

**Q7. What happens if you don’t specify `--net` when running containers?**
**A7:**
By default, Docker attaches containers to the **default bridge network**, where containers **cannot resolve each other by name** (only by IP).
Communication is limited unless you use `--link` (deprecated) or a user-defined network.

---

**Q8. Can two containers on different networks talk to each other?**
**A8:**
Not directly. Containers must share a common network to communicate.
Alternatively, you can use a proxy container or connect one container to multiple networks with `docker network connect`.

---

## **Summary of Commands**

```bash
# Step 1: Create network
docker network create --driver bridge my-bridge-net

# Step 2: Build image
docker build -t flask-api .

# Step 3: Run containers
docker run -d --name mysql --net=my-bridge-net mysql:latest
docker run -d --name redis --net=my-bridge-net redis:latest
docker run -d --name flask --net=my-bridge-net -p 5001:5001 flask-api

# Step 4: Test connectivity
docker exec -it flask bash
ping mysql
ping redis
exit
curl http://localhost:5001/about

# Step 5: Cleanup
docker stop mysql redis flask
docker rm mysql redis flask
docker network rm my-bridge-net
docker rmi flask-api
```

---

### ✅ **End Result**

* Three containers (`flask`, `mysql`, `redis`) communicating over a custom bridge network.
* Flask API accessible externally via `localhost:5001`.
* Network isolation and connectivity verified.
* Full environment cleaned up afterward to avoid leftover resources.

---