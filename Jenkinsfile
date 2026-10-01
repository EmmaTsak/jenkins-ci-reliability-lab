pipeline {
    agent none

    options {
        disableConcurrentBuilds()
        timeout(time: 10, unit: 'MINUTES')
        buildDiscarder(logRotator(
            numToKeepStr: '20',
            artifactNumToKeepStr: '10'
        ))
    }

    environment {
        APP_ENV = 'ci'
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

                stage('Validate Environment') {
                    steps {
                        sh '''
                            if [ -z "$APP_ENV" ]; then
                                echo "ERROR: APP_ENV is not configured"
                                exit 1
                            fi
                        '''
                    }
                }

                stage('Operational Checks') {
                    steps {
                        sh './scripts/check_disk.sh'

                        retry(2) {
                            sh '.venv/bin/python scripts/check_jenkins.py'
                        }
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

            post {
                success {
                    echo 'CI pipeline completed successfully.'
                }

                failure {
                    echo 'CI pipeline failed. Review the failed stage and console output.'
                }

                always {
                    echo "Build result: ${currentBuild.currentResult}"
                }
            }
        }
    }
}