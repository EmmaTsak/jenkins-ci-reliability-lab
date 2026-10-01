# Jenkins Pipeline Design

## Purpose

The main Jenkins pipeline validates a small Python application while also demonstrating distributed CI execution, reliability controls, operational checks, secure credential handling and clear failure classification.

The pipeline is defined in:

```text
Jenkinsfile
```

A separate pipeline for executor and capacity experiments is defined in:

```text
Jenkinsfile.capacity
```

## Trigger

The main pipeline uses Jenkins Poll SCM:

```text
H/2 * * * *
```

Jenkins periodically checks the GitHub repository for a new revision and starts the pipeline when a change is detected.

The project uses Pipeline from SCM so the Jenkins pipeline definition remains version-controlled with the application source.

## Top-Level Agent Strategy

The main pipeline uses:

```groovy
agent none
```

This prevents the entire pipeline from occupying a single Jenkins executor.

Instead, stages request the execution environment they need.

This makes the relationship between the Jenkins controller, agent labels and build execution explicit.

## Agent Verification

The first stage verifies both Jenkins agents in parallel.

The pipeline targets:

```text
agent1
agent2
```

Each branch checks:

- agent availability
- hostname
- Python availability

This demonstrates distributed Jenkins execution before the main CI workflow begins.

## Checkout

The source repository is retrieved using:

```groovy
checkout scm
```

This keeps source retrieval aligned with the Jenkins Pipeline from SCM configuration.

## Environment Setup

The main CI workflow creates a Python virtual environment:

```text
.venv
```

Dependencies are then installed from:

```text
requirements.txt
```

The project pins the versions of pytest and Ruff so CI uses predictable tool versions.

## Build Parameters

The pipeline defines a `TARGET_ENV` parameter with values such as:

```text
ci
staging
```

The selected value becomes:

```text
APP_ENV
```

inside the pipeline.

This demonstrates basic parameterised pipeline behaviour without introducing unnecessary deployment complexity.

## Environment Validation

The pipeline checks that `APP_ENV` is configured before continuing.

Failing early helps make environment problems easier to identify.

## Credential Handling

The pipeline retrieves Jenkins credentials using:

```groovy
withCredentials(...)
```

The configured credential is identified through Jenkins Credential Store rather than being placed directly in the Jenkinsfile.

The pipeline receives temporary environment variables for:

```text
JENKINS_USER
JENKINS_API_TOKEN
```

The stage verifies that both values are available without printing the actual credential values.

## Operational Checks

Operational checks are intentionally separated from application-quality checks.

They include:

- disk-capacity validation
- Jenkins controller reachability

The disk check is implemented in:

```text
scripts/check_disk.sh
```

The Jenkins connectivity check is implemented in:

```text
scripts/check_jenkins.py
```

The connectivity check is wrapped in:

```groovy
retry(2)
```

because short infrastructure or networking failures may be transient.

## Retry Strategy

Retries are limited to infrastructure checks where a temporary failure may recover safely.

Application tests are not automatically retried.

A real product regression should remain visible rather than being repeatedly rerun until the pipeline becomes green.

## Parallel Quality Checks

Linting and tests run independently in parallel:

```text
Quality Checks
├── Lint
└── Test
```

Ruff validates Python code quality.

pytest validates application behaviour.

Running the two checks in parallel demonstrates Jenkins parallel stages while keeping the pipeline easy to understand.

## Build

After quality checks succeed, the application is packaged into:

```text
dist/health-service.zip
```

The project intentionally keeps the application itself small because the main focus of the repository is CI infrastructure and reliability rather than application complexity.

## Artifact Archiving

The generated ZIP is archived by Jenkins using artifact fingerprinting.

Generated build output is excluded from Git source control.

This keeps a clear separation between:

```text
source code
```

and:

```text
build output
```

## Pipeline Timeout

The pipeline has a ten-minute timeout.

This prevents a stalled or blocked execution from consuming Jenkins resources indefinitely.

## Concurrent Build Control

The pipeline uses:

```groovy
disableConcurrentBuilds()
```

to prevent overlapping executions of the same main pipeline.

Capacity and concurrency behaviour are tested separately through the dedicated capacity pipeline.

## Build Retention

The pipeline limits retained Jenkins history.

It keeps:

```text
20 builds
```

and:

```text
10 artifact sets
```

This prevents build history and artifacts from growing indefinitely.

## Failure Classification

The pipeline uses three failure categories:

```text
PRODUCT
INFRASTRUCTURE
DEPENDENCY_OR_ENVIRONMENT
```

### PRODUCT

Used for problems such as:

- failing tests
- lint failures
- application regression

### INFRASTRUCTURE

Used for problems such as:

- Jenkins connectivity failure
- operational-check failure
- infrastructure availability problems

### DEPENDENCY_OR_ENVIRONMENT

Used for problems such as:

- virtual-environment creation failure
- dependency installation failure
- environment setup failure

The objective is to improve CI signal quality by making failures easier to interpret.

## Post-Build Behaviour

The pipeline reports whether the CI workflow:

- completed successfully
- failed
- produced a final Jenkins build result

This ensures the pipeline finishes with a clear operational signal.

## Capacity Pipeline

`Jenkinsfile.capacity` provides a separate controlled workload for studying Jenkins scheduling.

It captures:

- executing agent
- CPU-core count
- memory availability
- disk usage

It then runs simulated work long enough to occupy an executor.

This was used to observe:

- queued builds
- one executor versus multiple executors
- executor contention
- capacity across multiple Jenkins agents

## Design Principles

The pipeline was designed around a few simple questions:

```text
What failed?
Where did it fail?
Is it product code or infrastructure?
Should the failure be retried?
What evidence should Jenkins retain?
```

The goal is not to make the Jenkinsfile as complicated as possible.

The goal is to make CI behaviour understandable, reproducible and useful when something goes wrong.