#!/bin/bash -x
decisionengine_modules/build/packaging/rpm/package.sh decisionengine_modules
tar cvf $GITHUB_WORKSPACE/rpmbuild.tar /var/tmp/root/rpm/decisionengine_modules/*
exit 0
