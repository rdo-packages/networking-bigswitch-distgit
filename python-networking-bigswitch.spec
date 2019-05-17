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
Version:        14.0.0
Release:        1%{?dist}
Summary:        Big Switch Networks neutron plugin for OpenStack Networking
License:        ASL 2.0
URL:            https://pypi.python.org/pypi/%{pypi_name}
Source0:        https://pypi.io/packages/source/n/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz
Source1:        neutron-bsn-agent.service
BuildArch:      noarch

BuildRequires:  python%{pyver}-devel
BuildRequires:  python%{pyver}-pbr
BuildRequires:  python%{pyver}-mock
BuildRequires:  python%{pyver}-oslotest
BuildRequires:  python%{pyver}-setuptools
BuildRequires:  python%{pyver}-sphinx
BuildRequires:  python%{pyver}-webob
BuildRequires:  systemd
BuildRequires:  git

%description
%{common_desc}

%package -n python%{pyver}-%{pypi_name}
Summary: Networking Bigswitch python library
%{?python_provide:%python_provide python%{pyver}-%{pypi_name}}

Requires:       openstack-neutron-common >= 1:12.0.0
Requires:       os-net-config >= 10.0.0
Requires:       python%{pyver}-alembic >= 1.0.0
Requires:       python%{pyver}-distro >= 1.3.0
Requires:       python%{pyver}-eventlet >= 0.24.1
Requires:       python%{pyver}-keystoneauth1 >= 3.11.1
Requires:       python%{pyver}-keystoneclient >= 3.18.0
Requires:       python%{pyver}-neutron-lib >= 1.20.0
Requires:       python%{pyver}-pbr >= 0.10.8
Requires:       python%{pyver}-oslo-log >= 3.40.1
Requires:       python%{pyver}-oslo-config >= 2:6.7.0
Requires:       python%{pyver}-oslo-utils >= 3.37.1
Requires:       python%{pyver}-oslo-messaging >= 9.2.0
Requires:       python%{pyver}-oslo-serialization >= 2.28.1
Requires:       python%{pyver}-oslo-i18n >= 3.22.1
Requires:       python%{pyver}-oslo-db >= 4.42.0
Requires:       python%{pyver}-oslo-service >= 1.33.0
Requires:       python%{pyver}-requests >= 2.18.4
Requires:       python%{pyver}-setuptools >= 18.5
Requires:       python%{pyver}-six >= 1.11.0
# https://github.com/openstack/networking-bigswitch/commit/206be47aa2eddeb4d908eeacec2d46cb0b16eb03
# seems to introduce this, but there's no code in this commit which
# shows anything 1.2.12-specific
# RHEL8 has 1.2.8, so we should use this for now
Requires:       python%{pyver}-sqlalchemy >= 1.2.8
Requires:       python%{pyver}-tap-as-a-service >= 3.0.0


%if 0%{?rhel} && 0%{?rhel} < 8
%{?systemd_requires}
%else
%{?systemd_ordering} # does not exist on EL7
%endif

%description -n python%{pyver}-%{pypi_name}
%{common_desc}


%package -n %{rpm_prefix}-agent
Summary:        Neutron Big Switch Networks agent

Requires:       python%{pyver}-%{pypi_name} = %{epoch}:%{version}-%{release}

%description -n %{rpm_prefix}-agent
%{common_desc}

This package contains the agent for security groups.

%package doc
Summary:        Neutron Big Switch Networks plugin documentation

%description doc
%{common_desc}

This package contains the documentation.

%prep
%autosetup -n %{pypi_name}-%{upstream_version} -S git

%build
export PBR_VERSION=%{version}
export SKIP_PIP_INSTALL=1
%{pyver_build}
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

%files -n python%{pyver}-%{pypi_name}
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
* Mon Apr 08 2019 Slawek Kaplonski <skaplons@redhat.com> 2:14.0.0-1
- Update to 14.0.0

