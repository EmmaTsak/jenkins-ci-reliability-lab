# Architecture

## Phase 3 Architecture

Current environment:

Windows
└── WSL2
    └── Ubuntu
        └── Docker
            ├── Jenkins Controller
            └── jenkins_home volume

## Jenkins Controller

The Jenkins controller currently runs inside a Docker container.

Container name:

jenkins-controller

Ports:

- 8080 — Jenkins web interface
- 50000 — Jenkins inbound agent communication

Persistent storage:

- Docker volume: jenkins_home
- Mounted at: /var/jenkins_home

## Persistence Test

The Jenkins container was:

1. stopped and restarted
2. deleted
3. recreated using the same Docker volume

The Jenkins configuration remained available after the container was recreated.

This demonstrates that the Jenkins controller container is disposable while Jenkins state is stored persistently outside the container.