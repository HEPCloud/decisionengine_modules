#!/bin/bash
PYVER=${1:-"3.6"}
GITHUB_WORKSPACE=${GITHUB_WORKSPACE:-`pwd`}
env PYVER=$PYVER decisionengine_modules/build/packaging/rpm/package.sh decisionengine_modules
status=$?
if [[ ! -e /var/tmp/`whoami`/rpm/decisionengine_modules/RPMS ]];then
  echo "Error: RPMS did not build"
  exit 1
else
  tar cvf $GITHUB_WORKSPACE/rpmbuild.tar /var/tmp/`whoami`/rpm/decisionengine_modules/RPMS
exit 0
fi
