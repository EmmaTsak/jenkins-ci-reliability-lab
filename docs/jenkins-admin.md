# Jenkins Administration Guide

## Purpose

This document describes the administration tasks used to operate the Jenkins CI Reliability Lab.

## Controller

The Jenkins controller runs in Docker:

```text
jenkins-controller
```

The controller provides:

- Jenkins UI
- job configuration
- build scheduling
- build queue management
- agent coordination
- credential management
- build history
- artifact metadata

The controller should coordinate builds rather than perform normal build workloads.

## Persistent Storage

Jenkins state is stored in the Docker volume:

```text
jenkins_home
```

mounted at:

```text
/var/jenkins_home
```

The controller can therefore be recreated while retaining Jenkins configuration.

## Starting and Stopping Jenkins

Check containers:

```bash
docker ps
```

Start the controller:

```bash
docker start jenkins-controller
```

Stop the controller:

```bash
docker stop jenkins-controller
```

Inspect controller logs:

```bash
docker logs jenkins-controller
```

## Jenkins Agents

The environment contains:

```text
linux-agent-1
linux-agent-2
```

Each agent normally uses one executor.

Labels:

```text
linux-agent-1:
linux python agent1

linux-agent-2:
linux python agent2
```

Agents communicate with the controller over the Docker network:

```text
jenkins-lab
```

Check agent containers:

```bash
docker ps
```

View agent logs:

```bash
docker logs linux-agent-1
docker logs linux-agent-2
```

Restart an agent:

```bash
docker restart linux-agent-1
```

## Executors

Executors are Jenkins scheduling slots.

One executor means one build task can execute on that node at a time.

Increasing executor count does not increase CPU, RAM, or disk resources.

Executor changes should therefore be based on actual resource capacity rather than queue size alone.

## Build Queue

A build may remain queued when:

- all matching executors are busy
- the required agent is offline
- the requested label does not match any online agent
- Jenkins is waiting for capacity

When investigating a queue, check:

1. required agent label
2. node status
3. executor availability
4. current running builds
5. CPU and memory capacity

## Credentials

Sensitive values should be stored in the Jenkins Credential Store.

Examples include:

- API tokens
- passwords
- deployment credentials

Secrets must not be:

- committed to Git
- placed directly in Jenkinsfiles
- printed into build logs
- included in screenshots or documentation

Pipeline steps should retrieve credentials only for the scope in which they are required.

## Agent Secrets

Inbound Jenkins agents use connection secrets.

If an agent secret is exposed:

1. stop the old agent
2. remove or recreate the Jenkins node
3. generate a new inbound secret
4. recreate the agent container with the new secret
5. verify connectivity
6. never reuse the old secret

## Build History

The main pipeline limits retained build history and artifacts.

This prevents Jenkins storage from growing indefinitely.

## Basic Health Checks

Useful commands include:

```bash
docker ps
docker logs jenkins-controller
docker logs linux-agent-1
docker logs linux-agent-2
docker stats --no-stream
docker network inspect jenkins-lab
```

Jenkins health can also be inspected through the monitoring script:

```bash
python3 monitoring/dashboard.py
```

## Safe Administrative Practice

Before changing Jenkins infrastructure:

- understand which builds are currently running
- avoid deleting persistent volumes
- never expose credentials
- change one agent at a time where possible
- confirm recovery before changing the second agent
- verify builds after configuration changes