#!/bin/bash
PYVER=${1:-"3.6"}
GITHUB_WORKSPACE=${GITHUB_WORKSPACE:-`pwd`}
env PYVER=$PYVER decisionengine_modules/build/scripts/run_pep8.sh
tar cvfj $GITHUB_WORKSPACE/logs.tar.bz2 pep8.*.log
cat pep8.*.log
exit `cat pep8*.log | wc -l`
