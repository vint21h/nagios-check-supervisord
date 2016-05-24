# nagios-check-supervisord
# nagios-plugin-check-supervisord.spec

%global _unpackaged_files_terminate_build 0
%global original_name nagios-check-supervisord
%global debug_package %{nil}

Summary: Check supervisord programs status Nagios plugin
Name: nagios-plugins-check-supervisord
Version: 0.2.5
Release: 1%{?dist}
Source0: %{original_name}-%{version}.tar.gz
License: GPLv3 or later
Group: Applications/System
BuildRequires: python-setuptools
Requires: python >= 2.6
Requires: nagios-plugins
Packager: Alexei Andrushievich <vint21h@vint21h.pp.ua>
Url: https://github.com/vint21h/nagios-check-supervisord

%description
Check supervisord programs status Nagios plugin.

%prep
%setup -n %{original_name}-%{version}

%install
mkdir -p %{buildroot}%{_libdir}/nagios/plugins
install -p -m 755 check_supervisord.py %{buildroot}%{_libdir}/nagios/plugins/check_supervisord

%files
%defattr(-,root,root)
%doc README.rst COPYING AUTHORS
%{_libdir}/nagios/plugins/check_supervisord

%changelog
* Wed May 25 2016 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 0.2.6-1
- Update to new version

* Sat Sep 5 2015 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 0.2.5-1
- Update to new version

* Mon Jun 1 2015 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 0.2.0-1
- Update to new version

* Fri Feb 13 2015 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 0.1.9-1
- Version up

* Fri Feb 13 2015 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 0.1.8-1
- Update spec changelog

* Wed Feb 11 2015 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 0.1.4-1
- Init
