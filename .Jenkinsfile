pipeline {
    agent { label 'docker' }
    stages{
        stage('DE modules tests') {
            parallel {
                stage('pep8') {
                    agent {
                        node {
                            label 'docker'
                            customWorkspace "${WORKSPACE}/${STAGE_NAME}"
                        }
                    }
                    steps {
                        script {
                            // DOCKER_IMAGE is defined through Jenkins project
                            pep8StageDockerImage="${DOCKER_IMAGE}_${BUILD_NUMBER}_${STAGE_NAME}"
                            // Set custom Build Name
                            if (params.GITHUB_PR_NUMBER) {
                                if (params.GITHUB_PR_STATE == 'CLOSED') {
                                    currentBuild.displayName="${BUILD_NUMBER}#PR#${GITHUB_PR_NUMBER}#CLOSED"
                                } else {
                                    currentBuild.displayName="${BUILD_NUMBER}#PR#${GITHUB_PR_NUMBER}"
                                }
                            } else {
                                currentBuild.displayName="${BUILD_NUMBER}#${BRANCH}"
                            }
                        }
                        echo "cleanup workspace"
                        sh 'for f in $(ls -A); do rm -rf ${f}; done'
                        // DE_MOD_REPO is defined through Jenkins project
                        echo "clone decisionengine_modules code from ${DE_MOD_REPO}"
                        sh '''
                            git clone ${DE_MOD_REPO}
                            cd decisionengine_modules
                            echo "checkout ${BRANCH} branch"
                            git checkout ${BRANCH}
                            echo GITHUB_PR_NUMBER: ${GITHUB_PR_NUMBER} - GITHUB_PR_STATE: ${GITHUB_PR_STATE}
                            if [[ -n ${GITHUB_PR_NUMBER} && ${GITHUB_PR_STATE} == OPEN ]]; then
                                git fetch origin pull/${GITHUB_PR_NUMBER}/merge:merge${GITHUB_PR_NUMBER}
                                git checkout merge${GITHUB_PR_NUMBER}
                            fi
                            cd ..
                        '''
                        echo "prepare docker image ${pep8StageDockerImage}"
                        sh "docker build --pull --tag ${pep8StageDockerImage} --build-arg BASEIMAGE=hepcloud/decision-engine-ci:${BRANCH} --build-arg USER=\$(id -u) --build-arg GROUP=\$(id -g) -f decisionengine_modules/.github/actions/pep8-in-sl7-docker/Dockerfile.jenkins decisionengine_modules/.github/actions/pep8-in-sl7-docker/"
                        echo "Run ${STAGE_NAME} tests"
                        sh "docker run --rm -v ${WORKSPACE}:${WORKSPACE} -w ${WORKSPACE} ${pep8StageDockerImage}"
                        sh 'for artifact_file in pep8.*.log pylint.*.log results.*.log mail.results; do mv -v ${artifact_file} ${STAGE_NAME}.${artifact_file}; done'
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: "${STAGE_NAME}.pep8.*.log,${STAGE_NAME}.pylint.*.log,${STAGE_NAME}.results.*.log,${STAGE_NAME}.mail.results"
                            echo "cleanup docker image ${pep8StageDockerImage}"
                            sh "docker rmi ${pep8StageDockerImage}"
                        }
                    }
                }
                stage('pylint') {
                    agent {
                        node {
                            label 'docker'
                            customWorkspace "${WORKSPACE}/${STAGE_NAME}"
                        }
                    }
                    steps {
                        script {
                            // DOCKER_IMAGE is defined through Jenkins project
                            pylintStageDockerImage="${DOCKER_IMAGE}_${BUILD_NUMBER}_${STAGE_NAME}"
                        }
                        echo "cleanup workspace"
                        sh 'for f in $(ls -A); do rm -rf ${f}; done'
                        // DE_MOD_REPO is defined through Jenkins project
                        echo "clone decisionengine_modules code from ${DE_MOD_REPO}"
                        sh '''
                            git clone ${DE_MOD_REPO}
                            cd decisionengine_modules
                            echo "checkout ${BRANCH} branch"
                            git checkout ${BRANCH}
                            echo GITHUB_PR_NUMBER: ${GITHUB_PR_NUMBER} - GITHUB_PR_STATE: ${GITHUB_PR_STATE}
                            if [[ -n ${GITHUB_PR_NUMBER} && ${GITHUB_PR_STATE} == OPEN ]]; then
                                git fetch origin pull/${GITHUB_PR_NUMBER}/merge:merge${GITHUB_PR_NUMBER}
                                git checkout merge${GITHUB_PR_NUMBER}
                            fi
                            cd ..
                        '''
                        echo "prepare docker image ${pylintStageDockerImage}"
                        sh "docker build --pull --tag ${pylintStageDockerImage} --build-arg BASEIMAGE=hepcloud/decision-engine-ci:${BRANCH} --build-arg USER=\$(id -u) --build-arg GROUP=\$(id -g) -f decisionengine_modules/.github/actions/pylint-in-sl7-docker/Dockerfile.jenkins decisionengine_modules/.github/actions/pylint-in-sl7-docker/"
                        echo "Run ${STAGE_NAME} tests"
                        sh "docker run --rm -v ${WORKSPACE}:${WORKSPACE} -w ${WORKSPACE} ${pylintStageDockerImage}"
                        sh 'for artifact_file in pep8.*.log pylint.*.log results.*.log mail.results; do mv -v ${artifact_file} ${STAGE_NAME}.${artifact_file}; done'
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: "${STAGE_NAME}.pep8.*.log,${STAGE_NAME}.pylint.*.log,${STAGE_NAME}.results.*.log,${STAGE_NAME}.mail.results"
                            echo "cleanup docker image ${pylintStageDockerImage}"
                            sh "docker rmi ${pylintStageDockerImage}"
                        }
                    }
                }
                stage('unit_tests') {
                    agent {
                        node {
                            label 'docker'
                            customWorkspace "${WORKSPACE}/${STAGE_NAME}"
                        }
                    }
                    steps {
                        script {
                            // DOCKER_IMAGE is defined through Jenkins project
                            unit_testsStageDockerImage="${DOCKER_IMAGE}_${BUILD_NUMBER}_${STAGE_NAME}"
                        }
                        echo "cleanup workspace"
                        sh 'for f in $(ls -A); do rm -rf ${f}; done'
                        // DE_MOD_REPO is defined through Jenkins project
                        echo "clone decisionengine_modules code from ${DE_MOD_REPO}"
                        sh '''
                            git clone ${DE_MOD_REPO}
                            cd decisionengine_modules
                            echo "checkout ${BRANCH} branch"
                            git checkout ${BRANCH}
                            echo GITHUB_PR_NUMBER: ${GITHUB_PR_NUMBER} - GITHUB_PR_STATE: ${GITHUB_PR_STATE}
                            if [[ -n ${GITHUB_PR_NUMBER} && ${GITHUB_PR_STATE} == OPEN ]]; then
                                git fetch origin pull/${GITHUB_PR_NUMBER}/merge:merge${GITHUB_PR_NUMBER}
                                git checkout merge${GITHUB_PR_NUMBER}
                            fi
                            cd ..
                        '''
                        echo "prepare docker image ${unit_testsStageDockerImage}"
                        sh "docker build --pull --tag ${unit_testsStageDockerImage} --build-arg BASEIMAGE=hepcloud/decision-engine-ci:${BRANCH} --build-arg USER=\$(id -u) --build-arg GROUP=\$(id -g) -f decisionengine_modules/.github/actions/unittest-in-sl7-docker/Dockerfile.jenkins decisionengine_modules/.github/actions/unittest-in-sl7-docker"
                        echo "Run ${STAGE_NAME} tests"
                        sh "docker run --rm -v ${WORKSPACE}:${WORKSPACE} -w ${WORKSPACE} ${unit_testsStageDockerImage}"
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: "pytest.log"
                            echo "cleanup docker image ${unit_testsStageDockerImage}"
                            sh "docker rmi ${unit_testsStageDockerImage}"
                            }
                    }
                }
                stage('rpmbuild') {
                    agent {
                        node {
                            label 'docker'
                            customWorkspace "${WORKSPACE}/${STAGE_NAME}"
                        }
                    }
                    steps {
                        script {
                            // DOCKER_IMAGE is defined through Jenkins project
                            rpmbuildStageDockerImage="${DOCKER_IMAGE}_${BUILD_NUMBER}_${STAGE_NAME}"
                        }
                        echo "cleanup workspace"
                        sh 'for f in $(ls -A); do rm -rf ${f}; done'
                        // DE_MOD_REPO is defined through Jenkins project
                        echo "clone decisionengine_modules code from ${DE_MOD_REPO}"
                        sh '''
                            git clone ${DE_MOD_REPO}
                            cd decisionengine_modules
                            echo "checkout ${BRANCH} branch"
                            git checkout ${BRANCH}
                            echo GITHUB_PR_NUMBER: ${GITHUB_PR_NUMBER} - GITHUB_PR_STATE: ${GITHUB_PR_STATE}
                            if [[ -n ${GITHUB_PR_NUMBER} && ${GITHUB_PR_STATE} == OPEN ]]; then
                                git fetch origin pull/${GITHUB_PR_NUMBER}/merge:merge${GITHUB_PR_NUMBER}
                                git checkout merge${GITHUB_PR_NUMBER}
                            fi
                            cd ..
                        '''
                        echo "prepare docker image ${rpmbuildStageDockerImage}"
                        sh "docker build --pull --tag ${rpmbuildStageDockerImage} --build-arg BASEIMAGE=hepcloud/decision-engine-ci:${BRANCH} --build-arg USER=\$(id -u) --build-arg GROUP=\$(id -g) -f decisionengine_modules/.github/actions/rpmbuild-in-sl7-docker/Dockerfile.jenkins decisionengine_modules/.github/actions/rpmbuild-in-sl7-docker"
                        echo "Run ${STAGE_NAME} tests"
                        sh "docker run --rm -v ${WORKSPACE}:${WORKSPACE} -w ${WORKSPACE} ${rpmbuildStageDockerImage}"
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: "rpmbuild.tar"
                            echo "cleanup docker image ${rpmbuildStageDockerImage}"
                            sh "docker rmi ${rpmbuildStageDockerImage}"
                        }
                    }
                }
            }
        }
    }
}
