pipeline {
   agent {label 'docker'}

   stages {

      stage('setup') {
         steps {
            echo "cleanup workspace"
            sh 'for f in $(ls -A); do rm -rf ${f}; done'
            // DE_MOD_REPO is defined through Jenkins project
            echo "clone decisionengine_modules code from ${DE_MOD_REPO}"
            sh "git clone ${DE_MOD_REPO}"
         }
      }

      stage('pep8') {
         steps {
            script {
                // DOCKER_IMAGE is defined through Jenkins project
                pep8StageDockerImage="${DOCKER_IMAGE}_${BUILD_NUMBER}_${STAGE_NAME}"
            }
            echo "prepare docker image ${pep8StageDockerImage}"
            sh "docker build -t ${pep8StageDockerImage} -f decisionengine_modules/.github/actions/pep8-in-sl7-docker/Dockerfile.jenkins decisionengine_modules/.github/actions/pep8-in-sl7-docker/"
            echo "Run ${STAGE_NAME} tests"
            sh "docker run --rm -v ${WORKSPACE}:${WORKSPACE} -w ${WORKSPACE} ${pep8StageDockerImage}"
            echo "cleanup docker image"
            sh "docker rmi ${pep8StageDockerImage}"
         }
      }

      stage('pylint') {
         steps {
            script {
                // DOCKER_IMAGE is defined through Jenkins project
                pylintStageDockerImage="${DOCKER_IMAGE}_${BUILD_NUMBER}_${STAGE_NAME}"
            }
            echo "prepare docker image ${pylintStageDockerImage}"
            sh "docker build -t ${pylintStageDockerImage} -f decisionengine_modules/.github/actions/pylint-in-sl7-docker/Dockerfile.jenkins decisionengine_modules/.github/actions/pylint-in-sl7-docker/"
            echo "Run ${STAGE_NAME} tests"
            sh "docker run --rm -v ${WORKSPACE}:${WORKSPACE} -w ${WORKSPACE} ${pylintStageDockerImage}"
            echo "cleanup docker image"
            sh "docker rmi ${pylintStageDockerImage}"
         }
      }

      stage('unittest') {
         steps {
            script {
                // DOCKER_IMAGE is defined through Jenkins project
                unittestStageDockerImage="${DOCKER_IMAGE}_${BUILD_NUMBER}_${STAGE_NAME}"
            }
            echo "prepare docker image ${unittestStageDockerImage}"
            sh "docker build -t ${unittestStageDockerImage} -f decisionengine_modules/.github/actions/unittest-in-sl7-docker/Dockerfile.jenkins decisionengine_modules/.github/actions/unittest-in-sl7-docker"
            echo "Run ${STAGE_NAME} tests"
            sh "docker run --rm -v ${WORKSPACE}:${WORKSPACE} -w ${WORKSPACE} ${unittestStageDockerImage}"
            echo "cleanup docker image"
            sh "docker rmi ${unittestStageDockerImage}"
         }
      }

      stage('rpmbuild') {
         steps {
            script {
                // DOCKER_IMAGE is defined through Jenkins project
                rpmbuildStageDockerImage="${DOCKER_IMAGE}_${BUILD_NUMBER}_${STAGE_NAME}"
            }
            echo "prepare docker image ${rpmbuildStageDockerImage}"
            sh "docker build -t ${rpmbuildStageDockerImage} -f decisionengine_modules/.github/actions/rpmbuild-in-sl7-docker/Dockerfile.jenkins decisionengine_modules/.github/actions/rpmbuild-in-sl7-docker"
            echo "Run ${STAGE_NAME} tests"
            sh "docker run --rm -v ${WORKSPACE}:${WORKSPACE} -w ${WORKSPACE} ${rpmbuildStageDockerImage}"
            echo "cleanup docker image"
            sh "docker rmi ${rpmbuildStageDockerImage}"
         }
      }
   }
}
