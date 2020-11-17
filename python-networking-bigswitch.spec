%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
%global pypi_name networking-bigswitch
%global module_name networking_bigswitch
%global rpm_prefix openstack-neutron-bigswitch
%global docpath doc/build/html
%global lib_dir %{buildroot}%{python3_sitelib}/%{module_name}/plugins/bigswitch
%global with_doc 1

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

BuildRequires:  python3-devel
BuildRequires:  python3-pbr
BuildRequires:  python3-mock
BuildRequires:  python3-oslotest
BuildRequires:  python3-setuptools
BuildRequires:  python3-webob
BuildRequires:  systemd
BuildRequires:  git-core

%description
%{common_desc}

%package -n python3-%{pypi_name}
Summary: Networking Bigswitch python library
%{?python_provide:%python_provide python3-%{pypi_name}}

Requires:       openstack-neutron-common >= 1:13.0.0
Requires:       os-net-config >= 10.0.0
Requires:       python3-alembic >= 1.0.0
Requires:       python3-distro >= 1.3.0
Requires:       python3-eventlet >= 0.24.1
Requires:       python3-keystoneauth1 >= 3.11.1
Requires:       python3-keystoneclient >= 3.18.0
Requires:       python3-neutron-lib >= 1.22.0
Requires:       python3-pbr >= 0.10.8
Requires:       python3-oslo-log >= 3.40.1
Requires:       python3-oslo-config >= 2:6.7.0
Requires:       python3-oslo-utils >= 3.37.1
Requires:       python3-oslo-messaging >= 9.2.0
Requires:       python3-oslo-serialization >= 2.28.1
Requires:       python3-oslo-i18n >= 3.22.1
Requires:       python3-oslo-db >= 4.42.0
Requires:       python3-oslo-service >= 1.33.0
Requires:       python3-requests >= 2.18.4
Requires:       python3-setuptools >= 18.5
# https://github.com/openstack/networking-bigswitch/commit/206be47aa2eddeb4d908eeacec2d46cb0b16eb03
# seems to introduce this, but there's no code in this commit which
# shows anything 1.2.12-specific
# RHEL8 has 1.2.8, so we should use this for now
Requires:       python3-sqlalchemy >= 1.2.12


%if 0%{?rhel} && 0%{?rhel} < 8
%{?systemd_requires}
%else
%{?systemd_ordering} # does not exist on EL7
%endif

%description -n python3-%{pypi_name}
%{common_desc}


%package -n %{rpm_prefix}-agent
Summary:        Neutron Big Switch Networks agent

Requires:       python3-%{pypi_name} = %{epoch}:%{version}-%{release}

%description -n %{rpm_prefix}-agent
%{common_desc}

This package contains the agent for security groups.

%if 0%{?with_doc}
%package doc
Summary:        Neutron Big Switch Networks plugin documentation

BuildRequires:  python3-sphinx

%description doc
%{common_desc}

This package contains the documentation.
%endif

%prep
%autosetup -n %{pypi_name}-%{upstream_version} -S git

%build
export PBR_VERSION=%{version}
export SKIP_PIP_INSTALL=1
%{py3_build}

%if 0%{?with_doc}
%{__python3} setup.py build_sphinx
rm %{docpath}/.buildinfo
%endif

%install
%{py3_install}
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/neutron-bsn-agent.service
mkdir -p %{buildroot}/%{_sysconfdir}/neutron/conf.d/neutron-bsn-agent
mkdir -p %{lib_dir}/tests
for lib in %{lib_dir}/version.py %{lib_dir}/tests/test_server.py; do
    sed '1{\@^#!/usr/bin/env python@d}' $lib > $lib.new &&
    touch -r $lib $lib.new &&
    mv $lib.new $lib
done

%files -n python3-%{pypi_name}
%license LICENSE
%{python3_sitelib}/%{module_name}
%{python3_sitelib}/*.egg-info

%config %{_sysconfdir}/neutron/policy.d/bsn_plugin_policy.json

%files -n %{rpm_prefix}-agent
%license LICENSE
%{_unitdir}/neutron-bsn-agent.service
%{_bindir}/neutron-bsn-agent
%dir %{_sysconfdir}/neutron/conf.d/neutron-bsn-agent

%if 0%{?with_doc}
%files doc
%license LICENSE
%doc README.rst
%doc %{docpath}
%endif

%post
%systemd_post neutron-bsn-agent.service

%preun
%systemd_preun neutron-bsn-agent.service

%postun
%systemd_postun_with_restart neutron-bsn-agent.service

%changelog
