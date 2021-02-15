# nagios-check-supervisord
# nagios-plugin-check-supervisord.spec

%global _unpackaged_files_terminate_build 0
%global original_name nagios-check-supervisord
%global debug_package %{nil}

Summary: Check supervisord programs status Nagios plugin
Name: nagios-plugins-check-supervisord
Version: 2.0.0
Release: 1%{?dist}
Source0: %{original_name}-%{version}.tar.gz
License: GPLv3 or later
Group: Applications/System
BuildRequires: python-setuptools
Requires: python >= 2.7
Requires: nagios-plugins
Requires: supervisor
Packager: Alexei Andrushievich <vint21h@vint21h.pp.ua>
Url: https://github.com/vint21h/nagios-check-supervisord/

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
* Mon Feb 15 2020 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 2.0.0-1
- Updated to new version

* Sun Feb 14 2020 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 1.1.1-1
- Updated to new version

* Thu Feb 11 2020 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 1.1.0-1
- Updated to new version

* Sat Oct 24 2020 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 1.0.1-1
- Updated to new version

* Tue Oct 20 2020 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 1.0.0-1
- Updated to new version

* Wed Apr 18 2018 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 0.6.1-1
- Updated to new version

* Wed Apr 18 2018 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 0.6.0-1
- Updated to new version

* Wed Apr 18 2018 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 0.5.2-1
- Updated to new version

* Mon Dec 18 2017 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 0.5.1-1
- Updated to new version

* Mon Dec 18 2017 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 0.5.0-1
- Updated to new version

* Mon Oct 10 2017 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 0.4.0-1
- Updated to new version

* Thu Sep 29 2016 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 0.3.1-1
- Updated to new version

* Fri Jul 29 2016 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 0.3.0-1
- Updated to new version

* Wed May 25 2016 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 0.2.7-1
- Updated to new version

* Wed May 25 2016 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 0.2.6-1
- Updated to new version

* Sat Sep 5 2015 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 0.2.5-1
- Updated to new version

* Mon Jun 1 2015 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 0.2.0-1
- Updated to new version

* Fri Feb 13 2015 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 0.1.9-1
- Version up

* Fri Feb 13 2015 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 0.1.8-1
- Update spec changelog

* Wed Feb 11 2015 Alexei Andrushievich <vint21h@vint21h.pp.ua> - 0.1.4-1
- Init
