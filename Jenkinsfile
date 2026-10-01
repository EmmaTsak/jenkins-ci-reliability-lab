pipeline {
    agent any

    stages {
        stage('Verify Environment') {
            steps {
                sh 'python3 --version'
                sh 'pwd'
                sh 'hostname'
            }
        }
    }
}

