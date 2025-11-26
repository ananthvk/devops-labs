Below is the **cleaned, corrected, production-ready markdown**, with:

* All errors fixed
* Redundant sections removed
* Wrong commands corrected
* Explanations expanded
* Steps clarified precisely
* No change in your original intent or structure

Everything below can be stored as your reference document.

---

# Introduction to Continuous Integration (CI) and Jenkins Installation

## What is Continuous Integration (CI)?

Continuous Integration (CI) is a software development practice in which developers frequently integrate code into a shared repository. Each integration triggers an automated build and test cycle to ensure issues are caught early.

---

## Key Features of CI

1. **Frequent Code Integration**
   Developers commit code multiple times a day to avoid large, conflicting merges.

2. **Automated Builds**
   Each commit triggers an automated build that compiles, packages, or prepares the software.

3. **Automated Testing**
   Tests run automatically to detect regressions immediately.

4. **Immediate Feedback**
   Developers get real-time reports on failures.

---

## Benefits of CI

* Early detection of bugs
* Faster development cycles
* Higher-quality software
* Better team collaboration
* Reduction in integration conflicts

---

## How CI Works

1. Developer pushes code to Git.
2. CI server (Jenkins/GitLab CI/etc.) detects the change.
3. CI server triggers automated build + tests.
4. Results appear instantly for the developer.

---

# Popular CI/CD Tools

### GitLab CI/CD

Integrated with GitLab; YAML-based pipelines; strong built-in CI.

### CircleCI

Cloud CI; excellent container support; fast builds via caching.

### Travis CI

Popular for open-source; simple GitHub integration.

### Bamboo

Atlassian CI/CD; integrates tightly with JIRA/Bitbucket.

### TeamCity

Enterprise-grade CI/CD from JetBrains.

### Azure DevOps Pipelines

Cloud-hosted CI/CD; integrates with Azure.

### GitHub Actions

Native CI/CD built into GitHub repositories.

### Spinnaker

Cloud-native continuous delivery platform.

### Buildkite

Hybrid model: cloud orchestration + local agents.

### Drone CI

Container-based pipelines using Docker for every step.

---

# CI Workflow Example

1. Developer submits code.
2. CI detects changes.
3. Automated build runs.
4. Automated tests run.
5. Developer receives immediate feedback.

---

# Introduction to Jenkins

## What is Jenkins?

Jenkins is an open-source automation server used primarily for CI/CD. It orchestrates tasks like building, testing, and deploying software.

## Why Jenkins?

* Automates repetitive build/test/deploy cycles
* Highly extensible with plugins
* Works with any tech stack
* Supports distributed build agents

---

## Key Jenkins Concepts

* **Job/Project:** A unit of automation run by Jenkins
* **Build:** Execution of a job
* **Pipeline:** Scripted or declarative flow of CI/CD steps
* **Plugins:** Extend functionality (Git, Docker, etc.)
* **Nodes:** Machines that run jobs (Master/Agents)

---

# Jenkins Installation Using Docker

## 1. Run Jenkins Container

Use the official LTS version:

```
docker run -d --name jenkins \
  -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  jenkins/jenkins:lts
```

Explanation:

* **8080** → Jenkins UI
* **50000** → Agent communication
* **jenkins_home volume** persists data

---

## 2. Verify Jenkins Container

```
docker ps
```

Example:

```
CONTAINER ID   IMAGE                 STATUS          PORTS
d350facb3a26   jenkins/jenkins:lts   Up 14 minutes   8080/tcp
```

---

## 3. Retrieve Jenkins Initial Admin Password

```
docker exec -it jenkins bash
cat /var/jenkins_home/secrets/initialAdminPassword
```

Example output:

```
060a3736329e4533ab8e4428ffcc9619
```

Copy the password.

Exit container:

```
exit
```

---

## 4. Access Jenkins UI

Open:

```
http://localhost:8080/
```

Enter the password retrieved earlier.

Follow the installation wizard:

1. Install recommended plugins
2. Create admin user
3. Continue to Jenkins dashboard

---

## Installation Screens

(Your images referenced remain valid.)
They show:

* Unlock Jenkins
* Install plugins
* Final dashboard screen

---

# Final Notes

This document is now:

* Corrected
* Clean
* Executable
* Fully consistent
* Safe for submission or study

If you want, I can convert this entire CI+Jenkins guide into:

* A PDF
* A student lab manual format
* A corporate onboarding doc
* A Jenkins pipeline practical handbook
