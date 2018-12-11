# Macros for py2/py3 compatibility
%if 0%{?fedora} || 0%{?rhel} > 7
%global pyver %{python3_pkgversion}
%else
%global pyver 2
%endif
%global pyver_bin python%{pyver}
%global pyver_sitelib %python%{pyver}_sitelib
%global pyver_install %py%{pyver}_install
%global pyver_build %py%{pyver}_build
# End of macros for py2/py3 compatibility
%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
%global pypi_name networking-bigswitch
%global module_name networking_bigswitch
%global rpm_prefix openstack-neutron-bigswitch
%global docpath doc/build/html
%global lib_dir %{buildroot}%{pyver_sitelib}/%{module_name}/plugins/bigswitch

%global common_desc This package contains the Big Switch Networks Neutron plugins and agents

Name:           python-%{pypi_name}
Epoch:          2
Version:        XXX
Release:        XXX
Summary:        Big Switch Networks neutron plugin for OpenStack Networking
License:        ASL 2.0
URL:            https://pypi.python.org/pypi/%{pypi_name}
Source0:        https://pypi.io/packages/source/n/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz
Source1:        neutron-bsn-agent.service
BuildArch:      noarch

BuildRequires:  python%{pyver}-devel
BuildRequires:  python%{pyver}-pbr
BuildRequires:  python%{pyver}-setuptools
BuildRequires:  python%{pyver}-sphinx
BuildRequires:  systemd

Requires:       openstack-neutron-common >= 1:7.0.0
Requires:       python%{pyver}-pbr >= 0.10.8
Requires:       python%{pyver}-oslo-log >= 1.0.0
Requires:       python%{pyver}-oslo-config >= 2:1.9.3
Requires:       python%{pyver}-oslo-utils >= 1.4.0
Requires:       python%{pyver}-oslo-messaging >= 1.8.0
Requires:       python%{pyver}-oslo-serialization >= 1.4.0

%{?systemd_requires}

%description
%{common_desc}


%package -n %{rpm_prefix}-agent
Summary:        Neutron Big Switch Networks agent
%{?python_provide:%python_provide python%{pyver}-%{pypi_name}}

Requires:       python%{pyver}-%{pypi_name} = %{epoch}:%{version}-%{release}

%description -n %{rpm_prefix}-agent
%{common_desc}

This package contains the agent for security groups.

%package doc
Summary:        Neutron Big Switch Networks plugin documentation
%{?python_provide:%python_provide python%{pyver}-%{pypi_name}}

%description doc
%{common_desc}

This package contains the documentation.

%prep
%setup -q -n %{pypi_name}-%{upstream_version}

%build
export PBR_VERSION=%{version}
export SKIP_PIP_INSTALL=1
%{pyver_bin} setup.py build
%{pyver_bin} setup.py build_sphinx
rm %{docpath}/.buildinfo

%install
%{pyver_install}
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/neutron-bsn-agent.service
mkdir -p %{buildroot}/%{_sysconfdir}/neutron/conf.d/neutron-bsn-agent
mkdir -p %{lib_dir}/tests
for lib in %{lib_dir}/version.py %{lib_dir}/tests/test_server.py; do
    sed '1{\@^#!/usr/bin/env python@d}' $lib > $lib.new &&
    touch -r $lib $lib.new &&
    mv $lib.new $lib
done

%files
%license LICENSE
%{pyver_sitelib}/%{module_name}
%{pyver_sitelib}/*.egg-info

%config %{_sysconfdir}/neutron/policy.d/bsn_plugin_policy.json

%files -n %{rpm_prefix}-agent
%license LICENSE
%{_unitdir}/neutron-bsn-agent.service
%{_bindir}/neutron-bsn-agent
%dir %{_sysconfdir}/neutron/conf.d/neutron-bsn-agent

%files doc
%license LICENSE
%doc README.rst
%doc %{docpath}

%post
%systemd_post neutron-bsn-agent.service

%preun
%systemd_preun neutron-bsn-agent.service

%postun
%systemd_postun_with_restart neutron-bsn-agent.service

%changelog
