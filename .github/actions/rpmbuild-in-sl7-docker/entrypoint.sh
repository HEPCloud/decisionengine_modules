#!/bin/bash -x
decisionengine_modules/build/packaging/rpm/package.sh $PWD
tar cvf $GITHUB_WORKSPACE/rpmbuild.tar /var/tmp/root/rpm/decisionengine/*
exit 0
