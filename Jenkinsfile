#!groovy

@Library('flycatch-jenkins-shared-library') _

pipeline {
    agent any
    options {
        disableConcurrentBuilds(abortPrevious: true)
    }

    environment {
            APP_NAME = "travelworld-backend"
            BUILD_ID = "${APP_NAME}.${BUILD_NUMBER}"
            PYTHON_TAG = "3.10.12-alpine" // replace with the latest Node version tag
        }

    stages {
        stage("Analysis") {
            agent {
                docker {
                    image "python:${PYTHON_TAG}"
                    args '-u root:root'
                    reuseNode true
                }
            }

            stages {
                    stage("Dependencies Setup") {
                        steps {
                            catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                                sh script: 'pip install --upgrade pip', label: 'pip upgrade'
                                sh script: 'pip install -r requirements.txt', label: 'requirements installation'
                            }
                        }
                    }

                    stage("Lint") {
                        steps {
                            catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                                sh script: 'pip install pylint', label: 'pylint installation'
                                sh script: 'pylint --max-line-length=100  --ignore=Dockerfile,nginx,migrations,Jenkinsfile,README.md,docker-compose.yml,pylint.log,report  --output-format=parseable ./* > pylint.log', label: 'lint check'
                            }
                        }
                    }

                    stage('Cpd') {
                        steps {
                            catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                                sh script: 'apk add npm && npm install -g jscpd', label: 'jscpd installation'
                                sh script: 'jscpd --ignore "**/*.yml,Jenkinsfile,README.md,nginx/**/*,**/templates/**,**/migrations/**,**/static/assets/**" -r xml --exitCode 1', label: 'code duplication check'
                            }
                        }
                    }

                    stage("change ownsership of lint and cpd log files") {
                    steps {
                        catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                            sh 'chown -R 1000:1000 ./*'
                        }
                    }
                }

            }

            post {
                always {
                    withChecks('pyLint') {
                        recordIssues(
                            publishAllIssues: true,
                            enabledForFailure: true, aggregatingResults: true,
                            tools: [pyLint(pattern: 'pylint.log', reportEncoding: 'UTF-8')],
                            qualityGates: [[threshold: 1, type: 'TOTAL', unstable: true]]
                        )
                    }

                    withChecks('cpd') {
                        recordIssues(
                            publishAllIssues: true,
                            enabledForFailure: true, aggregatingResults: true,
                            tools: [cpd(pattern: 'report/jscpd-report.xml', reportEncoding: 'UTF-8')],
                            qualityGates: [[threshold: 1, type: 'TOTAL', unstable: true]]
                        )
                    }
                }
            }
        }

        stage("Dockerize") {
            steps {
                sh 'sed -i "/^FROM/a LABEL BUILD_ID=${BUILD_ID}" Dockerfile' // add a label to all stages of the docker file.
                sh 'docker build --no-cache --force-rm -t ${BUILD_ID} .'
            }
        }

    }

    post {
        failure {
            sendNotifications(currentBuild.result)
        }
        cleanup {
            sh 'docker rmi $(docker images -q -f "label=BUILD_ID=${BUILD_ID}")'
            cleanWs deleteDirs: true
        }
    }
}
