pipeline {

    agent any

    environment {

        EXECUTION = 'remote'
        GRID_URL = 'http://localhost:4444/wd/hub'
        BROWSER = 'chrome'
        HEADLESS = 'true'
        OPENAI_API_KEY = credentials('ak_2PP57R31q0X92wD3tA8Un2lu2rN0w')
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

        stage('Agentic MCP Performance Tests') {

            steps {

                sh 'pytest tests/test_agentic_mcp_performance.py --alluredir=reports/allure-results'
            
            }
        }

        stage('Run Tests') {

            steps {

                sh '''
                . venv/bin/activate

                pytest tests/ -n 4 --reruns 1 --reruns-delay 2 --alluredir=reports/allure-results
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