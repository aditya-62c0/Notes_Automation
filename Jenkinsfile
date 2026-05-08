pipeline {

    agent any

    environment {

        EXECUTION = 'remote'
        GRID_URL = 'http://localhost:4444'
        BROWSER = 'chrome'
        HEADLESS = 'true'
    }

    stages {

        stage('Clone Repository') {

            steps {

                git branch: 'main',
                url: 'https://github.com/aditya-62c0/Notes_Automation.git'
            }
        }

        stage('Start Selenium Grid') {

            steps {

                sh 'docker compose down --remove-orphans || true'

                sh 'docker rm -f selenium-hub || true'

                sh 'docker rm -f $(docker ps -aq --filter "name=chrome") || true'

                sh 'docker compose up -d --scale chrome=4'

                sh 'sleep 15'
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

                pytest -n 4 --alluredir=reports/allure-results
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

            sh 'docker compose down --remove-orphans || true'
        }

        success {

            echo 'Pipeline Success'
        }

        failure {

            echo 'Pipeline Failed'
        }
    }
}