#!/bin/bash
export PYVER=${1:-"3.6"}
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
source venv/bin/activate
# MMDB
echo "MMDB Python (`which python`): `python --version`"
echo "MMDB M2Crypto: `yum list *m2crypto*`"
echo "MMDB M2Crypto python: `python3 -c "import M2Crypto; print (M2Crypto.__path__)"`"
echo "MMDB M2Crypto python3: `python3 -c "import M2Crypto; print (M2Crypto.__path__)"`"

pytest -v -l --tb=native decisionengine_modules > pytest.log 2>&1
status=$?
cat pytest.log
exit $status
