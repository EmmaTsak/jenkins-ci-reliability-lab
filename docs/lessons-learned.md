# Lessons Learned

## Jenkins Controller vs Agent

The Jenkins controller coordinates the CI system.

It is responsible for tasks such as:

- job configuration
- scheduling
- queue management
- credential management
- agent coordination
- build history

Agents provide the environments where pipeline work executes.

Keeping those responsibilities separate made Jenkins architecture easier to understand and demonstrated how build execution can be distributed across multiple nodes.

## Executors Are Scheduling Slots

One of the most important lessons from the capacity experiments was that a Jenkins executor is not additional hardware.

Increasing executor count does not create more:

- CPU
- RAM
- disk capacity
- network capacity

Executors only allow more Jenkins tasks to be scheduled concurrently on the same node.

Too many executors can therefore increase resource contention rather than improve performance.

## Multiple Agents Can Add Capacity

Adding another Jenkins agent is different from simply adding executors to an existing node.

A separate agent can provide additional execution capacity when that agent has its own available computing resources.

The two-agent setup also demonstrated distributed Jenkins execution and label-based workload placement.

## Queues Are Operational Signals

A queued build does not automatically mean Jenkins is broken.

A queue can indicate:

- busy executors
- insufficient capacity
- an offline agent
- restrictive labels
- long-running workloads

Queue behaviour should be investigated before changing executor counts.

## Docker Networking Matters

A major practical lesson was understanding what `localhost` means inside containers.

Inside a Jenkins agent container:

```text
localhost
```

refers to the agent itself.

It does not refer to the Jenkins controller.

The controller is reachable across the Docker network using:

```text
jenkins-controller
```

This made Docker DNS and container networking an important part of troubleshooting the CI environment.

## Persistent Infrastructure Must Be Explicit

Containers are disposable.

Jenkins state should therefore not depend on the lifetime of the controller container.

The project stores Jenkins state in:

```text
jenkins_home
```

The controller container was recreated while reusing the same Docker volume, and Jenkins configuration remained available.

This demonstrated the difference between disposable infrastructure and persistent state.

## CI Signal Quality Matters

A red build is more useful when it explains what kind of problem occurred.

The project distinguishes:

```text
PRODUCT
INFRASTRUCTURE
DEPENDENCY_OR_ENVIRONMENT
```

This makes it easier to decide where troubleshooting should begin.

A failing application test should not trigger the same response as an offline Jenkins agent.

## Retries Should Be Selective

Retries can be useful for transient infrastructure problems.

For example, a temporary Jenkins connectivity failure may succeed when retried shortly afterwards.

However, retrying deterministic product tests until they eventually pass hides useful failure information.

Retries should therefore be applied only where temporary recovery is reasonable.

## Flaky Tests Reduce Trust

A flaky test can produce different results for the same source revision:

```text
PASS
FAIL
PASS
```

That reduces confidence in CI.

Repeatedly rerunning a flaky test until it passes produces a misleading signal.

The correct response is to identify and remove the source of nondeterminism.

## Build Artifacts Are Not Source Code

Generated output should not normally live in the Git repository.

The project generates:

```text
health-service.zip
```

during the Jenkins build and stores it as a Jenkins artifact.

Git contains the inputs required to reproduce the artifact rather than the generated artifact itself.

## Artifact Retention Matters

CI systems can accumulate significant storage over time.

Keeping every build and every artifact indefinitely is unnecessary for this lab.

Build and artifact retention policies provide a simple example of controlling Jenkins storage growth.

## Monitoring Improves Troubleshooting

The monitoring dashboard made useful Jenkins state visible without requiring a full monitoring platform.

It reports information such as:

- Jenkins availability
- online agents
- offline agents
- queue size
- recent builds
- failed builds
- average build duration
- disk usage

Having operational state available before making changes improves troubleshooting decisions.

## Credentials Should Stay Outside Source Control

Jenkins credentials should not be stored directly in:

- source files
- Jenkinsfiles
- documentation
- screenshots

The project uses Jenkins Credential Store and temporary credential injection.

API tokens and inbound agent secrets are treated as runtime credentials rather than repository configuration.

## Exposed Secrets Must Be Rotated

Deleting an exposed credential from a file is not enough.

If a secret is exposed, it should be considered compromised.

The correct response is to:

1. rotate the credential
2. invalidate the previous value
3. check whether it entered Git history
4. inspect relevant logs or screenshots
5. verify the new credential works

## Least Privilege Matters

Credentials and components should only receive the access required for their purpose.

A build agent does not automatically require administrator-level access to Jenkins.

Thinking about privilege boundaries is important even in a local learning environment.

## Failure Classification Improves Incident Response

Troubleshooting became easier when failures were classified before attempting recovery.

For example:

```text
test failure
→ PRODUCT
```

while:

```text
offline agent
→ INFRASTRUCTURE
```

and:

```text
dependency installation failure
→ DEPENDENCY_OR_ENVIRONMENT
```

This reduces the chance of changing infrastructure when the problem actually belongs to application code.

## Operational Checks Belong in CI

CI reliability depends on more than tests.

Disk capacity and Jenkins connectivity can affect whether the pipeline is able to run successfully.

Adding lightweight operational checks demonstrated how infrastructure state can be validated as part of CI.

## Timeouts Prevent Unbounded Builds

A pipeline should not be allowed to remain stuck indefinitely.

The project uses a pipeline timeout to place a clear upper bound on execution time.

This protects Jenkins execution capacity from blocked builds.

## Troubleshooting Should Follow a Process

The most useful troubleshooting pattern during the project became:

```text
observe symptom
        ↓
inspect logs and state
        ↓
classify the failure
        ↓
identify the failure domain
        ↓
test a hypothesis
        ↓
apply the smallest appropriate fix
        ↓
rerun
        ↓
confirm recovery
```

This approach was more reliable than changing multiple settings at once.

## Reliability Is More Than Uptime

A useful CI system is not reliable simply because Jenkins is running.

Reliable CI also requires:

- understandable failure signals
- reproducible environments
- controlled execution time
- manageable resource usage
- persistent state
- monitoring
- secure credentials
- useful artifacts
- recoverability

## Final Takeaway

The biggest lesson from the project was that operating CI is different from simply writing a Jenkinsfile.

A useful CI system needs to provide developers with feedback that is:

- repeatable
- understandable
- actionable
- secure
- operationally manageable

The reliability experiments made Jenkins behaviour much clearer than simply building a pipeline that always succeeds.