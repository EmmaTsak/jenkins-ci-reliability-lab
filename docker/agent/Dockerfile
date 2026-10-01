FROM jenkins/inbound-agent:latest-jdk21

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-venv \
        python3-pip \
        git && \
    rm -rf /var/lib/apt/lists/*

USER jenkins

WORKDIR /home/jenkins/agent