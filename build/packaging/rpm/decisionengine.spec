#%define version __DECISIONENGINE_RPM_VERSION__
#%define release __DECISIONENGINE_RPM_RELEASE__
%define version 0.1
%define release 0.1

%define decisionengine_user decisionengine
%define decisionengine_group decisionengine


%define logicengine_build_dir %{_builddir}/decisionengine/framework/logicengine/cxx/build
%define systemddir %{_prefix}/lib/systemd/system
%define decisionengine_logdir %{_localstatedir}/log/decisionengine
%define decisionengine_lockdir %{_localstatedir}/lock/decisionengine

# From http://fedoraproject.org/wiki/Packaging:Python
# Define python_sitelib
%if ! (0%{?fedora} > 12 || 0%{?rhel} > 5)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

%define de_python_sitelib $RPM_BUILD_ROOT%{python_sitelib}

Name:           decisionengine
Version:        %{version}
Release:        %{release}
Summary:        The HEPCloud Decision Engine Framework

Group:          System Environment/Daemons
License:        Fermitools Software Legal Information (Modified BSD License)
URL:            http://hepcloud.fnal.gov

Source0:        decisionengine.tar.gz
#Source1:        ../../../framework/logicengine/cxx/build

BuildArch:      x86_64
BuildRequires:  cmake numpy numpy-f2py python-pandas
BuildRequires:  boost-python boost-regex boost-system
Requires:       numpy >= 1.7.1
Requires:       numpy-f2py >= 1.7.1
Requires:       python-pandas >= 0.17.1
Requires:       boost-python >= 1.53.0
Requires:       boost-regex >= 1.53.0
Requires:       boost-system >= 1.53.0
Requires(post): /sbin/service
Requires(post): /usr/sbin/useradd


%description
The Decision Engine is a critical component of the HEPCloud Facility. It
provides the functionality of resource scheduling for disparate resource
providers, including those which may have a cost or a restricted allocation
of cycles.


%prep
%setup -q -n decisionengine


%build
pwd
mkdir %{logicengine_build_dir}
cd %{logicengine_build_dir}
cmake ..
make
cp ErrorHandler/RE.so ../..
cp ErrorHandler/libLogicEngine.so ../..


%install
#make install DESTDIR=%{buildroot}

rm -rf $RPM_BUILD_ROOT

# Create the system directories
install -d $RPM_BUILD_ROOT%{_sbindir}
install -d $RPM_BUILD_ROOT%{_bindir}
install -d $RPM_BUILD_ROOT%{_sysconfdir}
install -d $RPM_BUILD_ROOT%{_initrddir}
install -d $RPM_BUILD_ROOT%{_localstatedir}/log/decisionengine
install -d $RPM_BUILD_ROOT%{_localstatedir}/lock/decisionengine
install -d $RPM_BUILD_ROOT%{systemddir}
install -d $RPM_BUILD_ROOT%{python_sitelib}

# Copy files in place
cp -r ../decisionengine $RPM_BUILD_ROOT%{python_sitelib}

install -m 0644 build/packaging/rpm/decisionengine.service $RPM_BUILD_ROOT%{systemddir}/decision-engine.service
install -m 0644 build/packaging/rpm/decisionengine_initd_template $RPM_BUILD_ROOT%{_initrddir}/decision-engine

# Remove unwanted files
#rm -Rf $RPM_BUILD_ROOT%{python_sitelib}/decisionengine/doc
rm -Rf $RPM_BUILD_ROOT%{python_sitelib}/decisionengine/build
rm -Rf $RPM_BUILD_ROOT%{python_sitelib}/decisionengine/modules
rm -Rf $RPM_BUILD_ROOT%{python_sitelib}/decisionengine/framework/logicengine/cxx
rm -Rf $RPM_BUILD_ROOT%{python_sitelib}/decisionengine/framework/logicengine/tests


%files
%{python_sitelib}/decisionengine
%{systemddir}/decision-engine.service
%{_initrddir}/decision-engine
%{_localstatedir}/log/decisionengine
%{_localstatedir}/lock/decisionengine


#%clean
#rm -rf $RPM_BUILD_ROOT


%pre
# Add the "decisionengine" user and group if they do not exist
getent group %{decisionengine_group} >/dev/null || 
    groupadd -r  %{decisionengine_group}
getent passwd  %{decisionengine_user} >/dev/null || \
    useradd -r -g  %{decisionengine_user} -d /var/lib/decisionengine \
    -c "Decision Engine user" -s /sbin/nologin  %{decisionengine_user}
# If the decisionengine user already exists make sure it is part of
# the decisionengine group
usermod --append --groups  %{decisionengine_group}  %{decisionengine_user} >/dev/null


%post
# $1 = 1 - Installation
# $1 = 2 - Upgrade
/sbin/chkconfig --add decision-engine

# Chane the ownership of log and lock dir if theay already exist
if [ -d %{decisionengine_logdir} ]; then
    chown -R %{decisionengine_user}.%{decisionengine_group} %{decisionengine_logdir}
fi
if [ -d %{decisionengine_logdir} ]; then
    chown -R %{decisionengine_user}.%{decisionengine_group} %{decisionengine_logdir}
fi


%preun
# $1 = 0 - Action is uninstall
# $1 = 1 - Action is upgrade

if [ "$1" = "0" ] ; then
    /sbin/chkconfig --del decision-engine
fi



%changelog
* Mon May 01 2017 Parag Mhashilkar <parag@fnal.gov> - 0.1-0.1
- Decision Engine v0.1
- RPM work in progress

