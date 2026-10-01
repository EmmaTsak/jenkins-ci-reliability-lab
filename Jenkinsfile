pipeline {
    agent none

    options {
        disableConcurrentBuilds()
    }

    triggers {
        pollSCM('H/2 * * * *')
    }

    stages {
        stage('Verify Agents') {
            parallel {
                stage('Verify Agent 1') {
                    agent { label 'agent1' }

                    steps {
                        sh 'echo "Running on Agent 1:"'
                        sh 'hostname'
                        sh 'python3 --version'
                    }
                }

                stage('Verify Agent 2') {
                    agent { label 'agent2' }

                    steps {
                        sh 'echo "Running on Agent 2:"'
                        sh 'hostname'
                        sh 'python3 --version'
                    }
                }
            }
        }

        stage('CI Pipeline') {
            agent { label 'agent1' }

            stages {
                stage('Checkout') {
                    steps {
                        checkout scm
                    }
                }

                stage('Environment Setup') {
                    steps {
                        sh 'python3 -m venv .venv'
                        sh '.venv/bin/python -m pip install -r requirements.txt'
                    }
                }

                stage('Lint') {
                    steps {
                        sh '.venv/bin/python -m ruff check app tests'
                    }
                }

                stage('Test') {
                    steps {
                        sh '.venv/bin/python -m pytest -v'
                    }
                }

                stage('Build') {
                    steps {
                        sh 'mkdir -p dist'
                        sh '.venv/bin/python -m zipfile -c dist/health-service.zip app'
                    }
                }

                stage('Archive') {
                    steps {
                        archiveArtifacts artifacts: 'dist/*.zip', fingerprint: true
                    }
                }
            }
        }
    }
}