#!/bin/bash
PYVER=${1:-"3.6"}
GITHUB_WORKSPACE=${GITHUB_WORKSPACE:-`pwd`}
env PYVER=$PYVER decisionengine_modules/build/scripts/run_pylint.sh
tar cvfj $GITHUB_WORKSPACE/logs.tar.bz2 pylint.*.log
cat pylint.*.log
exit `cat pylint*.log | wc -l`
