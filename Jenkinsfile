pipeline {
    agent { label 'python' }

    triggers {
        pollSCM('H/2 * * * *')
    }
    
    stages {
        stage('Verify Agent') {
            steps {
                sh 'hostname'
                sh 'whoami'
                sh 'python3 --version'
                sh 'git --version'
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

        stage('Archive Artifact') {
            steps {
                archiveArtifacts artifacts: 'dist/*.zip', fingerprint: true
            }
        }
    }
}