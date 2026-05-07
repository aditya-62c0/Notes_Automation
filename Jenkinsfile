pipeline {

    agent any

    environment {
        EXECUTION = 'remote'
        GRID_URL = 'http://localhost:4444'
        BROWSER = 'chrome'
        HEADLESS = 'true'
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main',
                url: 'https://github.com/aditya-62c0/Notes_Automation.git'
            }
        }

        stage('Start Selenium Grid') {
            steps {
                sh 'docker compose down || true'
                sh 'docker compose up -d --scale chrome=4'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                python3 -m venv venv
                . venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                . venv/bin/activate
                pytest -n 8 --alluredir=reports/allure-results
                '''
            }
        }

        stage('Generate Allure Report') {
            steps {
                allure([
                    includeProperties: false,
                    jdk: '',
                    results: [[path: 'reports/allure-results']]
                ])
            }
        }
    }

    post {

        always {

            archiveArtifacts artifacts: 'reports/**/*'

            publishHTML([
                allowMissing: true,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'reports/html',
                reportFiles: 'report.html',
                reportName: 'HTML Report'
            ])

            sh 'docker compose down'
        }

        success {
            echo 'Tests Passed'
        }

        failure {
            echo 'Tests Failed'
        }
    }
}