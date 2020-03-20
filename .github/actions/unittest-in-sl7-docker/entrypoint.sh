#!/bin/bash
export PYVER=${1:-"2.7"}
source decisionengine_modules/build/scripts/utils.sh
setup_python_venv
setup_dependencies
le_builddir=dependencies/decisionengine/framework/logicengine/cxx/build
[ -e $le_buildir ] && rm -rf $le_builddir
mkdir $le_builddir
cd $le_builddir
cmake3 -Wno-dev  -DPYVER=$PYVER ..
make
make liblinks
cd -
export PYTHONPATH=$PWD:$PYTHONPATH
source venv-${PYVER}/bin/activate
pip install tabulate psycopg2
pytest -v -l --tb=native decisionengine_modules > pytest-$PYVER.log 2>&1
status=$?
cat pytest-$PYVER.log
exit $status
