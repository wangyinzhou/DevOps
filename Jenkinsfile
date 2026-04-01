pipeline {
  agent any

  environment {
    COMPOSE_PROJECT_NAME = 'cpe-devops-ci'
    BASE_URL = 'http://mock-cpe:5000'
    SELENIUM_REMOTE_URL = 'http://selenium:4444/wd/hub'
    HEADLESS = 'true'
  }

  options {
    timestamps()
    ansiColor('xterm')
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Build Test Image') {
      steps {
        sh 'docker compose build test-runner'
      }
    }

    stage('Start Services') {
      steps {
        sh 'docker compose up -d mock-cpe selenium'
      }
    }

    stage('Run Unit Tests') {
      steps {
        sh 'docker compose run --rm test-runner pytest tests/unit --cov=cpe_devops --cov-report=xml --cov-report=term-missing'
      }
      post {
        always {
          junit allowEmptyResults: true, testResults: 'artifacts/junit/*.xml'
        }
      }
    }

    stage('Run UI Tests') {
      steps {
        sh 'docker compose run --rm test-runner pytest tests/ui -m "smoke or ui" --reruns 1 --alluredir=allure-results'
      }
    }

    stage('Publish Reports') {
      steps {
        archiveArtifacts allowEmptyArchive: true, artifacts: 'artifacts/**/*,allure-results/**/*'
        allure includeProperties: false, jdk: '', reportBuildPolicy: 'ALWAYS', results: [[path: 'allure-results']]
      }
    }
  }

  post {
    always {
      sh 'docker compose down -v || true'
    }
    failure {
      mail to: 'qa@example.com',
           subject: "[FAILED] ${env.JOB_NAME} #${env.BUILD_NUMBER}",
           body: "Build failed. Please check Jenkins and Allure report for details."
    }
  }
}
