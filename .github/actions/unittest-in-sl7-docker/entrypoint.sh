#!/bin/bash

# SPDX-FileCopyrightText: 2017 Fermi Research Alliance, LLC
# SPDX-License-Identifier: Apache-2.0

export PYVER=${1:-"3.6"}
source decisionengine_modules/build/scripts/utils.sh
setup_python_venv
setup_dependencies
source venv/bin/activate
export PYTHONPATH=$PWD:$PYTHONPATH
pytest -v -l --tb=native decisionengine_modules > pytest.log 2>&1
status=$?
cat pytest.log
exit $status
