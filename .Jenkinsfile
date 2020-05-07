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
            sh 'https://github.com/vitodb/decisionengine_modules.git'
            # sh 'git clone https://github.com/HEPCloud/decisionengine_modules.git'
         }
      }

      stage('pylint') {
         steps {
            echo 'prepare docker image'
            # DOCKER_IMAGE="vitodb/decision-engine-modules-ci:jenkins"
            sh 'docker build -t ${DOCKER_IMAGE} -f decisionengine_modules/.github/actions/pylint-in-sl7-docker/Dockerfile.jenkins decisionengine_modules/.github/actions/pylint-in-sl7-docker/'
            echo 'Run pylint tests'
            sh '''
            pwd
            docker run --rm -v $PWD:$PWD -w ${PWD} ${DOCKER_IMAGE}
            '''
         }
      }

      stage('unit tests') {
         steps {
            echo 'prepare docker image'
            # DOCKER_IMAGE="vitodb/decision-engine-modules-ci:jenkins"
            sh 'docker build -t ${DOCKER_IMAGE} -f decisionengine_modules/.github/actions/unittest-in-sl7-docker/Dockerfile.jenkins decisionengine_modules/.github/actions/unittest-in-sl7-docker'
            echo 'Run pylint tests'
            sh '''
            pwd
            docker run --rm -v $PWD:$PWD -w ${PWD} ${DOCKER_IMAGE}
            '''
         }
      }
   }
}
