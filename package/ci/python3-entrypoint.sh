#!/bin/bash -xe
CMD=${1:- -m pytest}
LOGFILE=${2:- pytest.log}

id
getent passwd $(whoami)
python3 -m site
echo ''

# checkout DE Framework
rm -rf decisionengine
git clone https://github.com/HEPCloud/decisionengine.git

# checkout GlideinWMS for python3
rm -rf glideinwms
git clone -b branch_v3_9 https://github.com/glideinWMS/glideinwms.git

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
