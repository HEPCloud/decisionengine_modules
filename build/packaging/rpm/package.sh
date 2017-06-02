#!/bin/bash

id=`whoami`

echo $#

if [ $# -eq 0 ] ; then
    source_dir=/cloud/login/parag/wspace/de/decisionengine
else
    source_dir=$1
fi

echo "Using source dir: $source_dir"

export RPM_TOPDIR=/var/tmp/$id/rpm/decisionengine
mkdir -p $RPM_TOPDIR

rpm_macros=~/.rpmmacros

cat > $rpm_macros << RPM_MACROS
%_topdir    %(echo \$RPM_TOPDIR)
%_builddir  %{_topdir}/BUILD
%_sourcedir %{_topdir}/SOURCES
%_rpmdir    %{_topdir}/RPMS
%_specdir   %{_topdir}/SPECS
%_srcrpmdir %{_topdir}/SRPMS
%_tmppath   %{_topdir}/TMP
RPM_MACROS

release_dir=/var/tmp/$id/release/v0.1
release_tar=$release_dir/decisionengine.tar.gz

spec_template=$source_dir/build/packaging/rpm/decisionengine.spec
spec_file=$RPM_TOPDIR/SPECS/decisionengine.spec

rpm_dirs="BUILD RPMS SOURCES SPECS SRPMS"

for dir in $rpm_dirs
do
    d=$RPM_TOPDIR/$dir
    echo "Creating dir: $d"
    mkdir -p $d
done

rm -rf $release_dir
mkdir -p $release_dir

cp -r $source_dir  $release_dir
cd $release_dir
tar --exclude=.git --exclude=.gitignore --exclude=doc --exclude=cxx/build \
    --exclude=readme \
    -czf $release_tar decisionengine

cp $release_tar $RPM_TOPDIR/SOURCES
cp $spec_template $RPM_TOPDIR/SPECS

rpmbuild -bs $spec_file 
rpmbuild -bb $spec_file

#mock -r epel-el7-x86_64 --macro-file=$rpm_macros -i python
#mock --no-clean -r epel-el7-x86_64 --macro-file=%s --resultdir=%s/RPMS rebuild %s

#mock --macro-file=$rpm_macros -i python
#mock --no-clean --macro-file=$rpm_macros --resultdir=$RPM_TOPDIR/RPMS rebuild $spec_file
