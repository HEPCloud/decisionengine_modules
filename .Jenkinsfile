pipeline {
   agent {label 'docker'}

   stages {

      stage('cleanup') {
         steps {
            sh '''
            pwd
            for f in $(ls -A); do rm -rf ${f}; done
            '''
         }
      }

      stage('clone') {
         steps {
            sh 'git clone https://github.com/HEPCloud/decisionengine_modules.git'
         }
      }

      stage('pep8') {
         steps {
            script {
                // DOCKER_IMAGE is defined through Jenkins project
                pep8StageDockerImage="${DOCKER_IMAGE}_${BUILD_NUMBER}_${STAGE_NAME}"
            }
            echo "prepare docker image ${pep8StageDockerImage}"
            // DOCKER_IMAGE is defined through Jenkins project
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
            // DOCKER_IMAGE is defined through Jenkins project
            sh "docker build -t ${pylintStageDockerImage} -f decisionengine_modules/.github/actions/pylint-in-sl7-docker/Dockerfile.jenkins decisionengine_modules/.github/actions/pylint-in-sl7-docker/"
            echo "Run ${STAGE_NAME} tests"
            sh "docker run --rm -v ${WORKSPACE}:${WORKSPACE} -w ${WORKSPACE} ${pylintStageDockerImage}"
            echo "cleanup docker image"
            sh "docker rmi ${pylintStageDockerImage}"
         }
      }

      stage('unit_tests') {
         steps {
            script {
                // DOCKER_IMAGE is defined through Jenkins project
                unit_testsStageDockerImage="${DOCKER_IMAGE}_${BUILD_NUMBER}_${STAGE_NAME}"
            }
            echo "prepare docker image ${unit_testsStageDockerImage}"
            // DOCKER_IMAGE is defined through Jenkins project
            sh "docker build -t ${unit_testsStageDockerImage} -f decisionengine_modules/.github/actions/unittest-in-sl7-docker/Dockerfile.jenkins decisionengine_modules/.github/actions/unittest-in-sl7-docker"
            echo "Run ${STAGE_NAME} tests"
            sh "docker run --rm -v ${WORKSPACE}:${WORKSPACE} -w ${WORKSPACE} ${unit_testsStageDockerImage}"
            echo "cleanup docker image"
            sh "docker rmi ${unit_testsStageDockerImage}"
         }
      }

      stage('rpmbuild') {
         steps {
            script {
                // DOCKER_IMAGE is defined through Jenkins project
                rpmbuildStageDockerImage="${DOCKER_IMAGE}_${BUILD_NUMBER}_${STAGE_NAME}"
            }
            echo "prepare docker image ${rpmbuildStageDockerImage}"
            // DOCKER_IMAGE is defined through Jenkins project
            sh "docker build -t ${rpmbuildStageDockerImage} -f decisionengine_modules/.github/actions/rpmbuild-in-sl7-docker/Dockerfile.jenkins decisionengine_modules/.github/actions/rpmbuild-in-sl7-docker"
            echo "Run ${STAGE_NAME} tests"
            sh "docker run --rm -v ${WORKSPACE}:${WORKSPACE} -w ${WORKSPACE} ${rpmbuildStageDockerImage}"
            echo "cleanup docker image"
            sh "docker rmi ${rpmbuildStageDockerImage}"
         }
      }
   }
}
