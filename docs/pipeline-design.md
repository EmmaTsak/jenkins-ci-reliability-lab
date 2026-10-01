# docs/pipeline-design.md

## Jenkins Pipeline Design

## Purpose

The pipeline validates the Python application while also exercising Jenkins infrastructure and reliability concepts.

## Trigger

The pipeline uses SCM polling:

```text
H/2 * * * *
```

A change in GitHub triggers the Jenkins job after Jenkins detects the new revision.

## Top-Level Design

The pipeline uses:

```groovy
agent none
```

This prevents the entire pipeline from occupying one executor unnecessarily.

Specific stages request the agents they need.

## Agent Verification

The two agent checks run in parallel.

Purpose:

- prove distributed execution
- confirm Python availability
- confirm both agents are operational

## Checkout

The repository is retrieved from GitHub using Pipeline from SCM.

## Environment Setup

The pipeline creates a Python virtual environment and installs pinned dependencies.

This improves reproducibility.

## Environment Validation

Required environment variables are checked before quality or build stages begin.

Failing early gives developers clearer feedback.

## Credential Check

Jenkins credentials are retrieved from the Jenkins Credential Store.

Sensitive values are injected temporarily and are not stored directly in the Jenkinsfile.

## Operational Checks

Operational checks include:

- disk threshold
- Jenkins controller reachability

Infrastructure checks are separated from product tests so failure signals remain meaningful.

## Quality Checks

Linting and tests run in parallel because they are independent.

```text
Quality Checks
├── Lint
└── Test
```

Both are product-quality gates.

## Build

The application source is packaged into:

```text
dist/health-service.zip
```

## Archive

Jenkins archives the generated ZIP with fingerprinting enabled.

The generated `dist/` directory is ignored by Git.

## Reliability Features

The pipeline includes:

- timeout
- disabled concurrent pipeline runs
- build retention
- artifact retention
- infrastructure retry
- explicit failure categories
- post-build reporting

## Retry Strategy

Retries are limited to transient infrastructure operations.

Application tests are not automatically retried to force a green result.

## Parameters

The pipeline supports selecting a target environment such as:

```text
ci
staging
```

This allows the same pipeline definition to support multiple execution contexts.

## Failure Classification

Examples:

```text
FAILURE_CLASS=PRODUCT
FAILURE_CLASS=INFRASTRUCTURE
FAILURE_CLASS=DEPENDENCY_OR_ENVIRONMENT
```

The goal is to improve CI signal quality by making failures easier to interpret.

## Capacity Design

Agents normally use one executor each.

This makes queue behavior easier to understand and prevents excessive resource contention in the lab.

## Design Principle

The pipeline is intentionally more than a sequence of shell commands.

It is designed to answer:

```text
What failed?
Where did it fail?
Is it product or infrastructure?
Can it recover safely?
What evidence is retained?
```

---

# docs/lessons-learned.md

## Lessons Learned

### Jenkins Controller vs Agent

The controller schedules and coordinates work.

Agents execute builds.

Separating these roles improves isolation and allows build capacity to scale independently.

### Executors Are Not Hardware

An executor is a Jenkins scheduling slot.

Adding executors does not create additional:

- CPU
- RAM
- disk
- network capacity

Too many executors can make builds slower through contention.

### Queues Are Useful Signals

A growing build queue may indicate:

- insufficient executor capacity
- offline agents
- overly restrictive labels
- slow builds

The correct response is not always to add executors.

### Docker Networking Matters

`localhost` is relative to the environment executing the command.

Inside `linux-agent-1`:

```text
localhost
```

means Agent 1.

To reach the controller over the Docker network, the pipeline can use:

```text
jenkins-controller
```

### Persistence Must Be Explicit

Containers are disposable.

Important Jenkins state must live outside the controller container.

The `jenkins_home` volume allowed the controller to be deleted and recreated without losing configuration.

### CI Signal Quality Matters

A red build should answer whether the problem is:

- product code
- infrastructure
- dependency/environment

If every failure looks identical, CI becomes harder to trust and slower to troubleshoot.

### Retries Have Limits

Retries are useful for transient infrastructure failures.

Retries should not hide deterministic application defects or flaky tests.

### Flaky Tests Reduce Trust

A test that changes result without a source-code change creates poor CI signal.

The right fix is to remove the nondeterminism, not repeatedly rerun the test until it succeeds.

### Monitoring Improves Operations

The monitoring dashboard made Jenkins state visible through:

- agent health
- queue size
- recent builds
- failed builds
- build duration
- disk usage

Operational visibility makes troubleshooting faster.

### Build Artifacts Are Not Source Code

Generated ZIP files belong in Jenkins artifacts rather than the Git repository.

Source control should contain inputs needed to reproduce the build, not generated outputs.

### Secrets Must Be Treated as Credentials

Inbound agent secrets and API tokens should never be pasted into source control or documentation.

When a secret is exposed, it should be rotated.

### Least Privilege Reduces Risk

Components and credentials should receive only the access required for their task.

Build agents do not automatically need administrator-level access.

### Reliability Is More Than Uptime

Reliable CI also requires:

- predictable environments
- clear failures
- bounded execution time
- recoverability
- monitoring
- manageable resource usage
- reproducible builds

### Troubleshooting Is a Process

The most useful troubleshooting sequence became:

```text
observe symptom
→ inspect logs
→ classify failure
→ identify failure domain
→ test hypothesis
→ fix
→ rerun
→ confirm recovery
```

### Final Takeaway

A useful CI platform is not simply one that runs tests.

It must provide developers with fast, understandable, reproducible, and trustworthy feedback while remaining operable when infrastructure fails.