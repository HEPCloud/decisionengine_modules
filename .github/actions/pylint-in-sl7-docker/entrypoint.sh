#!/bin/bash -x
PYVER=${1:-"2.7"}
export PYVER
echo PYVER=$PYVER
decisionengine_modules/build/scripts/run_pylint.sh
tar cvfj $GITHUB_WORKSPACE/logs-$PYVER.tar.bz2 pep8.*.log pylint.*.log
cat pep8.*.log
cat pylint.*.log
pwd
ls -l
exit `cat *.log | wc -l`
