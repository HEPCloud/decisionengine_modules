#!/bin/bash -x
PYVER=${1:-"2.7"}
GITHUB_WORKSPACE=${GITHUB_WORKSPACE:-`pwd`}
env PYVER=$PYVER decisionengine_modules/build/packaging/rpm/package.sh decisionengine_modules
status=$?
tar cvf $GITHUB_WORKSPACE/rpmbuild-$PYVER.tar /var/tmp/`whoami`/rpm/decisionengine_modules/*RPMS
exit $status
