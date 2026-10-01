pipeline {
    agent { label 'python' }

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

        stage('Test') {
            steps {
                sh '.venv/bin/python -m pytest -v'
            }
        }
    }
}