# Docker Security with AppArmor and Python

## Objective

The goal is to secure Docker containers using AppArmor by defining restrictive profiles and applying them through Python’s Docker SDK.
The exercise shows how AppArmor limits filesystem access, binary execution, and capabilities inside a container, and how to programmatically enforce and verify these restrictions.

## Scenario

A Python Flask application is deployed inside a Docker container.
The task is to restrict what this container can access or execute.
You will create an AppArmor profile, load it, run the container under that profile, and test whether restricted operations are successfully blocked.

AppArmor acts like a rulebook. Once the profile is attached to the container, the kernel enforces the rules:
blocked directories become unreadable, banned binaries fail to run, and disabled capabilities return permission errors.

## Pre-requisites

Install `apparmor_parser` from the AppArmor utilities package.

For Ubuntu/Debian-based systems:

```
sudo apt-get update
sudo apt-get install apparmor-utils
```

This provides the parser that loads AppArmor profiles into the kernel.

## Tasks

### Task 1: Write a Basic Python Flask Application

File Name: app.py

```
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, this is a secure Flask application running inside a Docker container!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

This is the application you will later secure. It simply starts a web server and exposes one route.

### Task 2: Containerize the Flask Application Using a Dockerfile

File Name: Dockerfile

```
FROM python:3.8-slim
WORKDIR /app
COPY . /app
RUN pip install flask
EXPOSE 5000
CMD ["python", "app.py"]
```

Build the Docker image:

```
docker build -t flask-apparmor .
```

This creates the container environment in which AppArmor rules will later be tested.

### Task 3: Create and Apply AppArmor Profile

File Name: `/etc/apparmor.d/my-apparmor-profile`

```
#include <tunables/global>

/usr/bin/python3 {
    deny /etc/** r,
    deny /var/** rw,

    network inet stream,

    /app/** rwk,

    deny /bin/** rmix,
    deny /usr/bin/** rmix,

    capability net_bind_service,
    deny capability sys_admin,
}
```

Explanation of major directives:

* `deny /etc/** r`: blocks reading `/etc`, including `/etc/passwd` and `/etc/shadow`.
  Prevents the container from accessing host configuration files.

* `deny /bin/** rmix`: stops execution of host binaries like `/bin/bash`.
  Prevents container breakout attempts.

* `/app/** rwk`: allows read/write access inside its own application directory.

* `deny capability sys_admin`: one of the most powerful Linux capabilities; restricting it prevents container processes from performing privileged operations.

Load the profile:

```
sudo apparmor_parser -r /etc/apparmor.d/my-apparmor-profile
```

Run container with the profile:

```
docker run --security-opt="apparmor=my-apparmor-profile" -p 5000:5000 flask-apparmor
```

AppArmor now confines all Python processes in this container.

### Task 4: Use Docker SDK for Python to Apply AppArmor Profile

File Name: apply_apparmor.py

```
import docker

client = docker.from_env()

client.images.build(path=".", tag="flask-apparmor")

container = client.containers.run(
    "flask-apparmor",
    ports={'5000/tcp': 5000},
    security_opt=["apparmor=my-apparmor-profile"],
    detach=True
)

print(f"Container started: {container.short_id}")

container_info = client.api.inspect_container(container.id)
apparmor_profile = container_info['HostConfig']['SecurityOpt']

print(f"AppArmor profile applied: {apparmor_profile}")

container.stop()
```

This script does the same steps as the CLI: builds the image, runs the container, attaches the profile, and inspects to confirm.

Install the SDK:

```
pip install docker
python apply_apparmor.py
```

### Task 5: Test Restricted Actions

File Name: test_restricted_actions.py

```
import docker

client = docker.from_env()

container = client.containers.run(
    "flask-apparmor",
    ports={'5000/tcp': 5000},
    security_opt=["apparmor=my-apparmor-profile"],
    detach=True
)

exit_code, output = container.exec_run("cat /etc/passwd")
print(f"Attempt to read /etc/passwd: Exit Code {exit_code}, Output: {output.decode()}")

exit_code, output = container.exec_run("/bin/bash")
print(f"Attempt to execute /bin/bash: Exit Code {exit_code}, Output: {output.decode()}")

container.stop()
```

This verifies the profile actually blocks the restricted operations:

* reading `/etc/passwd` → denied
* invoking `/bin/bash` → execution blocked

## Questions and Answers

1. What is the purpose of using AppArmor with Docker containers?
   AppArmor enforces per-container mandatory access control rules that limit what a container can read, write, or execute. It prevents containers from accessing host files or performing dangerous operations even if compromised.

2. How do AppArmor profiles help secure a Docker container?
   Profiles define allowed and forbidden filesystem paths, network permissions, and capabilities. The kernel enforces these rules at runtime. If the container tries an action outside the profile, the kernel blocks it.

3. Why is it important to restrict access to sensitive directories such as `/etc/` and `/var/`?
   `/etc/` contains system-wide configurations and identity files.
   `/var/` contains logs and application state.
   Exposure of these directories allows enumeration of host details or tampering, so isolating them is mandatory for secure container deployment.

4. What other capabilities can you restrict using AppArmor profiles?
   Examples:
   `cap_sys_chroot`, `cap_sys_module`, `cap_net_raw`, `cap_dac_override`, `cap_sys_ptrace`.
   These prevent privilege escalation, raw socket creation, arbitrary file access, and debugging/inspection of host processes.

5. How can you verify if an AppArmor profile is successfully applied to a Docker container?
   Inspect the container using the Docker SDK or CLI.
   `docker inspect <id>` → check `HostConfig.SecurityOpt`.
   If the profile name appears (e.g., `apparmor=my-apparmor-profile`), the profile is active.