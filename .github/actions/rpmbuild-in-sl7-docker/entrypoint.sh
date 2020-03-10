#!/bin/bash -x
PYVER=${1:-"2.7"}
export PYVER
echo PYVER
decisionengine_modules/build/packaging/rpm/package.sh decisionengine_modules
status=$?
tar cvf $GITHUB_WORKSPACE/rpmbuild-$PYVER.tar /var/tmp/`whoami`/rpm/decisionengine_modules/*RPMS
pwd
ls -l
exit $status
