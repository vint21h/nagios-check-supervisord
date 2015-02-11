%global _unpackaged_files_terminate_build 0
%global name nagios-plugins-check-supervisord
%global version 0.1.2
%global release 1

Summary: Check supervisord programs status Nagios plugin
Name: %{name}
Version: %{version}
Release: 1%{?dist}
Source0: %{name}-%{version}.tar.gz
License: GPLv3 or later
Group: Applications/System
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
BuildRequires: python-setuptools
BuildRequires: nagios-plugins
Requires: python >= 2.7
Requires: nagios-plugins
Vendor: Alexei Andrushievich <vint21h@vint21h.pp.ua>
Url: https://github.com/vint21h/nagios-check-supervisord

%description
Check supervisord programs status Nagios plugin

%prep
%setup -n %{name}-%{version} -n %{name}-%{version}

%build
python setup.py build

%install
python setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
mkdir -p $RPM_BUILD_ROOT%{_libdir}/nagios/plugins
install -p -m 755 $RPM_BUILD_ROOT%{_bindir}/check_supervisord.py $RPM_BUILD_ROOT%{_libdir}/nagios/plugins/check_supervisord.py

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
%doc README.rst COPYING
%{_libdir}/nagios/plugins/check_supervisord.py
