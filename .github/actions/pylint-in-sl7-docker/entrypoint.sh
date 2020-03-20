#!/bin/bash
PYVER=${1:-"2.7"}
GITHUB_WORKSPACE=${GITHUB_WORKSPACE:-`pwd`}
env PYVER=$PYVER decisionengine_modules/build/scripts/run_pylint.sh
tar cvfj $GITHUB_WORKSPACE/logs-$PYVER.tar.bz2 pylint.*.log
cat pylint.*.log
exit `cat pylint*.log | wc -l`
