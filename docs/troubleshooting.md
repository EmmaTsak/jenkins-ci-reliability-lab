# docs/troubleshooting.md

## Jenkins Troubleshooting Guide

### Build is waiting in the queue

Symptoms:

```text
Still waiting to schedule task
```

Possible causes:

- required agent offline
- no free executor
- incorrect label
- resource contention

Checks:

```bash
docker ps
docker logs linux-agent-1
docker logs linux-agent-2
```

Then inspect Jenkins Nodes and Build Queue.

### Agent is offline

Check:

```bash
docker ps -a
docker logs <agent-container>
```

A real failure observed in this lab was an inbound agent repeatedly restarting because its connection secret was missing.

Recovery:

1. confirm the Jenkins node exists
2. verify the correct node name
3. configure a valid inbound secret
4. restart or recreate the container
5. confirm the node becomes online

### Pipeline test failure

Example:

```text
FAILED tests/test_health.py
FAILURE_CLASS=PRODUCT
```

This indicates application or test behavior rather than Jenkins infrastructure.

Check:

```bash
python -m pytest -v
```

locally before changing Jenkins infrastructure.

### Dependency or environment failure

Example category:

```text
FAILURE_CLASS=DEPENDENCY_OR_ENVIRONMENT
```

Investigate:

```bash
python3 --version
pip --version
cat requirements.txt
```

Check whether virtual-environment creation and package installation succeeded.

### Infrastructure health failure

Example:

```text
FAILURE_CLASS=INFRASTRUCTURE
```

Check:

- Jenkins controller availability
- Docker network
- agent connectivity
- disk capacity

Useful commands:

```bash
docker ps
docker network inspect jenkins-lab
docker logs jenkins-controller
```

### Container localhost confusion

A key incident in this project occurred when:

```text
http://localhost:8080
```

was used inside a Jenkins agent container.

Inside that container, `localhost` referred to the agent itself.

The controller was reachable through Docker DNS:

```text
http://jenkins-controller:8080
```

### Shell script failure

Observed error:

```text
unexpected operator
```

Cause:

Incorrect comparison operator syntax.

Correct:

```sh
[ "$USAGE" -ge "$THRESHOLD" ]
```

### Python syntax failure

Observed:

```text
SyntaxError: expected 'except' or 'finally' block
```

Use:

```bash
python3 -m py_compile scripts/check_jenkins.py
```

to detect Python syntax errors before committing.

### Jenkinsfile syntax failure

A malformed Jenkinsfile can fail before an agent or application test runs.

That is different from a product failure.

Check:

- braces
- stage nesting
- Declarative Pipeline structure
- `post`, `parallel`, and `environment` placement

### Build artifact accidentally committed

Generated build artifacts should not live in Git.

Fix:

```bash
git rm --cached -r dist
```

and add:

```text
dist/
```

to `.gitignore`.

Artifacts should be generated and archived by Jenkins instead.

### Flaky test

A flaky test produces different results for the same commit.

Example:

```text
same commit → PASS
same commit → FAIL
```

Do not hide flaky product tests with retries.

Fix the underlying nondeterminism.

---

# docs/incident-runbook.md

## Jenkins Incident Runbook

## 1. Confirm the Incident

Determine:

- what failed
- when it failed
- which build was affected
- whether all builds or one job are affected

Check Jenkins build status and console output.

## 2. Classify the Failure

Use one of the lab categories:

```text
PRODUCT
INFRASTRUCTURE
DEPENDENCY_OR_ENVIRONMENT
```

### Product

Examples:

- failing tests
- lint violations
- application regression

### Infrastructure

Examples:

- offline agent
- controller unavailable
- network failure
- disk capacity failure

### Dependency or Environment

Examples:

- package install failure
- missing Python
- virtual environment creation failure

## 3. Check Jenkins Controller

```bash
docker ps
docker logs jenkins-controller
```

Confirm the controller is running.

Check:

```text
http://localhost:8080
```

from the host environment.

## 4. Check Agents

```bash
docker ps
docker logs linux-agent-1
docker logs linux-agent-2
```

Confirm Jenkins shows both nodes online.

## 5. Inspect Queue

If builds are waiting:

- verify required labels
- verify agent availability
- verify free executors
- inspect running jobs

## 6. Check Resources

```bash
docker stats --no-stream
df -h
free -h
```

Look for:

- high CPU usage
- memory pressure
- disk exhaustion
- excessive concurrency

## 7. Check Networking

```bash
docker network inspect jenkins-lab
```

Verify the controller and agents are attached.

Remember:

```text
localhost inside one container != another container
```

Use Docker service/container names for internal communication.

## 8. Check Recent Changes

Review:

```bash
git log --oneline -10
git diff HEAD~1
```

Determine whether a recent source or Jenkinsfile change introduced the incident.

## 9. Recover Safely

Examples:

Restart agent:

```bash
docker restart linux-agent-1
```

Restart controller:

```bash
docker restart jenkins-controller
```

Avoid deleting:

```text
jenkins_home
```

unless data removal is explicitly intended.

## 10. Validate Recovery

After recovery:

- agent is online
- queue decreases
- build executes
- tests pass
- artifact is produced
- monitoring shows healthy state

## 11. Security Incident

If a credential is exposed:

1. assume it is compromised
2. rotate it
3. remove old access
4. check Git history if it was committed
5. confirm no logs or files still contain it

Do not simply delete a secret from the current file and continue using the same value.

## 12. Record Lessons

After an incident, document:

- symptom
- root cause
- recovery
- prevention

This converts troubleshooting experience into operational knowledge.