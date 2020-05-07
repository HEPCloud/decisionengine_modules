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
            sh '''
            git clone https://github.com/vitodb/decisionengine_modules.git
            cd decisionengine_modules
            git checkout vito_ci
            cd ..
            '''
            // sh 'git clone https://github.com/HEPCloud/decisionengine_modules.git'
         }
      }

      stage('pep8') {
         steps {
            echo 'prepare docker image'
            // DOCKER_IMAGE="vitodb/decision-engine-modules-ci:jenkins"
            sh 'docker build -t ${DOCKER_IMAGE} -f decisionengine_modules/.github/actions/pep8-in-sl7-docker/Dockerfile.jenkins decisionengine_modules/.github/actions/pep8-in-sl7-docker/'
            echo 'Run pep8 tests'
            sh '''
            pwd
            docker run --rm -v $PWD:$PWD -w ${PWD} ${DOCKER_IMAGE}
            '''
         }
      }

      stage('pylint') {
         steps {
            echo 'prepare docker image'
            // DOCKER_IMAGE="vitodb/decision-engine-modules-ci:jenkins"
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
            // DOCKER_IMAGE="vitodb/decision-engine-modules-ci:jenkins"
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
