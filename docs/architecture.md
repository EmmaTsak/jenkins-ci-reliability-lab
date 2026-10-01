# Jenkins CI Reliability Lab — Architecture

## Overview

The lab runs on a Windows host with Jenkins infrastructure operated from WSL2 Ubuntu through Docker.

The environment contains:

- one Jenkins controller
- persistent Jenkins controller storage
- two inbound Jenkins agents
- a dedicated Docker network
- GitHub as the SCM source
- a Python application used as the CI workload
- operational Python and shell checks
- a Jenkins REST API monitoring dashboard

## Runtime Architecture

```mermaid
flowchart TD
    WIN[Windows Host] --> WSL[WSL2 Ubuntu]
    WSL --> DOCKER[Docker Runtime]

    DOCKER --> CTRL[Jenkins Controller]
    DOCKER --> A1[linux-agent-1]
    DOCKER --> A2[linux-agent-2]

    VOL[(jenkins_home)] --> CTRL

    CTRL <-->|jenkins-lab network| A1
    CTRL <-->|jenkins-lab network| A2