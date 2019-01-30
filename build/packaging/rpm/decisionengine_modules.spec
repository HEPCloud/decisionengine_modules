#%define version __DECISIONENGINE_RPM_VERSION__
#%define release __DECISIONENGINE_RPM_RELEASE__
%define version 0.3.8
%define release 1

%define de_user decisionengine
%define de_group decisionengine

%define de_confdir %{_sysconfdir}/decisionengine
%define de_channel_confdir %{_sysconfdir}/decisionengine/config.d
%define de_logdir %{_localstatedir}/log/decisionengine
%define de_lockdir %{_localstatedir}/lock/decisionengine
%define systemddir %{_prefix}/lib/systemd/system

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

Source0:        decisionengine_modules.tar.gz

BuildArch:      x86_64
#BuildRequires:  cmake numpy numpy-f2py python-pandas
#BuildRequires:  boost-python boost-regex boost-system
#Requires:       numpy >= 1.7.1
#Requires:       numpy-f2py >= 1.7.1
#Requires:       python-pandas >= 0.17.1
#Requires:       boost-python >= 1.53.0
#Requires:       boost-regex >= 1.53.0
#Requires:       boost-system >= 1.53.0


%description
The Decision Engine is a critical component of the HEPCloud Facility. It
provides the functionality of resource scheduling for disparate resource
providers, including those which may have a cost or a restricted allocation
of cycles.

#%package testcase
#Summary:        The HEPCloud Decision Engine Test Case
#Group:          System Environment/Daemons
#Requires:       decisionengine

#%description testcase
#The testcase used to try out the Decision Engine.


%package standard-library
Summary:        The HEPCloud Decision Engine Modules in Standard Library
Group:          System Environment/Daemons
Requires:       decisionengine

%description standard-library
Modules in the Decision Engine Standard Library.


%prep
%setup -q -n decisionengine_modules


%build


%install
rm -rf $RPM_BUILD_ROOT

# Create the system directories
#install -d $RPM_BUILD_ROOT%{_sbindir}
#install -d $RPM_BUILD_ROOT%{_bindir}
#install -d $RPM_BUILD_ROOT%{_initddir}
#install -d $RPM_BUILD_ROOT%{de_confdir}
install -d $RPM_BUILD_ROOT%{de_channel_confdir}
#install -d $RPM_BUILD_ROOT%{de_logdir}
#install -d $RPM_BUILD_ROOT%{de_lockdir}
#install -d $RPM_BUILD_ROOT%{systemddir}
install -d $RPM_BUILD_ROOT%{python_sitelib}

# Copy files in place
cp -r ../decisionengine_modules $RPM_BUILD_ROOT%{python_sitelib}

#mkdir -p $RPM_BUILD_ROOT%{de_confdir}/config.d
# BUILDING testcase RPM: Uncomment following 1 line
#install -m 0644 framework/tests/etc/decisionengine/config.d/channelA.conf $RPM_BUILD_ROOT%{de_channel_confdir}

# Remove unwanted files
rm -Rf $RPM_BUILD_ROOT%{python_sitelib}/decisionengine_modules/build
rm -Rf $RPM_BUILD_ROOT%{python_sitelib}/decisionengine_modules/tests
rm -Rf $RPM_BUILD_ROOT%{python_sitelib}/decisionengine_modules/AWS/tests
# BUILDING testcase RPM: Comment following line
rm -Rf $RPM_BUILD_ROOT%{python_sitelib}/decisionengine_modules/testcases

# BUILDING testcase RPM: Uncomment following 3 lines
#%files testcase
#%{python_sitelib}/decisionengine/testcases
#%config(noreplace) %{de_channel_confdir}/channelA.conf


%files standard-library
%{python_sitelib}/decisionengine_modules/__init__.py
%{python_sitelib}/decisionengine_modules/__init__.pyo
%{python_sitelib}/decisionengine_modules/__init__.pyc
%{python_sitelib}/decisionengine_modules/graphite_client.py
%{python_sitelib}/decisionengine_modules/graphite_client.pyo
%{python_sitelib}/decisionengine_modules/graphite_client.pyc
%{python_sitelib}/decisionengine_modules/load_config.py
%{python_sitelib}/decisionengine_modules/load_config.pyo
%{python_sitelib}/decisionengine_modules/load_config.pyc
%{python_sitelib}/decisionengine_modules/LICENSE.txt
%{python_sitelib}/decisionengine_modules/util
%{python_sitelib}/decisionengine_modules/AWS
%{python_sitelib}/decisionengine_modules/glideinwms
%{python_sitelib}/decisionengine_modules/htcondor
%{python_sitelib}/decisionengine_modules/NERSC
%{python_sitelib}/decisionengine_modules/GCE
%{python_sitelib}/decisionengine_modules/graphite

%pre


%post

%preun

%changelog

* Wed Jan 30 2019 Parag Mhashilkar <parag@fnal.gov> - 0.3.8-1
- New transforms: AWSBurnRate and GCEBurnRate
- Breadth first filling of resources using FOM
- Resource request publishers takes into account Logic Engine facts

* Tue Jan 15 2019 Parag Mhashilkar <parag@fnal.gov> - 0.3.7-2
- Remove dependency on python-pandas and numpy rpms as we get latest from pip

* Mon Jan 14 2019 Parag Mhashilkar <parag@fnal.gov> - 0.3.7-1
- GCE/Nersc/Grid FOMs take into account idle, max idle, running jobs
- Updated AWS billing
- Bug fixes

* Wed Dec 19 2018 Parag Mhashilkar <parag@fnal.gov> - 0.3.6-1
- Replace deprecated API oauth2client with google-auth
- Bug fixes
- Improved code quality

* Wed Oct 31 2018 Parag Mhashilkar <parag@fnal.gov> - 0.3.5-0.1
- Added GCE publishers
- Changes to Job clustering config
- Bug fixes

* Mon Oct 22 2018 Parag Mhashilkar <parag@fnal.gov> - 0.3.4-0.1
- Added few GCE modules
- Bug fixes to AWS modules

* Fri Sep 14 2018 Parag Mhashilkar <parag@fnal.gov> - 0.3.3-0.1
- Added tool to create and update glidein infrastructure

* Tue Aug 28 2018 Parag Mhashilkar <parag@fnal.gov> - 0.3.2-0.1
- Added Nersc and Job clustering modules

* Tue Jun 26 2018 Parag Mhashilkar <parag@fnal.gov> - 0.3.1-0.3
- Splitting framework and modules codebase and Directory restructuring

* Tue Dec 12 2017 Parag Mhashilkar <parag@fnal.gov> - 0.3.1-0.1
- Minor bug fixes

* Mon Nov 13 2017 Parag Mhashilkar <parag@fnal.gov> - 0.3-0.1
- Decision Engine v0.3
- Includes fixes made during the demo

* Thu Nov 02 2017 Parag Mhashilkar <parag@fnal.gov> - 0.2-0.1
- Decision Engine v0.2 for the demo
- RPM work in progress

* Fri Sep 15 2017 Parag Mhashilkar <parag@fnal.gov> - 0.1-0.2
- Decision Engine v0.1 work in progress
- Added packaging for modules

* Mon May 01 2017 Parag Mhashilkar <parag@fnal.gov> - 0.1-0.1
- Decision Engine v0.1
- RPM work in progress

