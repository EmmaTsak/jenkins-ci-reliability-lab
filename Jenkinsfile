pipeline {
    agent { label 'python' }

    stages {
        stage('Verify Agent') {
            steps {
                sh 'python3 --version'
                sh 'hostname'
                sh 'whoami'
            }
        }
    }
}