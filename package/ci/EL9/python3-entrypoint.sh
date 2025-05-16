#!/bin/bash -xe

# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

CMD=${1:- -m pytest}
LOGFILE=${2:- pytest.log}
# set default DE_BRANCH to master or eventually set it as entrypoint script argument
DE_BRANCH=${3:-master}

# check DE modules branch
# the entrypoint script is supposed to run inside DE modules folder
# GITHUB_PR_NUMBER is set in Jenkins for PR
# CI on GitHub for PR uses a HEAD detached branch
# if we have a different case, we are testing an actual branch
[[ -z ${GITHUB_PR_NUMBER} && $(git rev-parse --abbrev-ref HEAD) != "HEAD" ]] && DE_BRANCH=$(git rev-parse --abbrev-ref HEAD) || :
echo "DE_BRANCH: ${DE_BRANCH}"

id
getent passwd $(whoami)
python3 -m site
echo ''

# checkout DE Framework
rm -rf decisionengine
git clone -b ${DE_BRANCH} https://github.com/HEPCloud/decisionengine.git

# checkout GlideinWMS for python3
rm -rf glideinwms
git clone -b master https://github.com/glideinWMS/glideinwms.git

# Install dependencies for GlideinWMS
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade wheel
python3 -m pip install -r glideinwms/requirements.txt

# Install dependencies for DE Framework
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade wheel
python3 -m pip install --upgrade pytest
python3 -m pip install --user Cython
python3 -m pip install --user numpy
(cd decisionengine/ ; python3 setup.py bdist_wheel)
python3 -m pip install --user decisionengine/dist/decisionengine*.whl

# Install DE Modules dependencies
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade pytest
python3 -m pip install -e . --user
python3 -m pip install -e .[develop] --user

echo''
python3 -m pip list

# make sure the pipe doesn't eat failures
set -o pipefail

# run the python "module/command"
export PYTHONPATH=${PWD}/src:${PYTHONPATH}
python3 ${CMD} 2>&1 | tee ${LOGFILE}
