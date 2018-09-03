%{!?upstream_version: %global upstream_version %{version}%{?milestone}}
%global pypi_name networking-bigswitch
%global module_name networking_bigswitch
%global rpm_prefix openstack-neutron-bigswitch
%global docpath doc/build/html
%global lib_dir %{buildroot}%{python2_sitelib}/%{module_name}/plugins/bigswitch

%global common_desc This package contains the Big Switch Networks Neutron plugins and agents

Name:           python-%{pypi_name}
Epoch:          2
Version:        13.0.0
Release:        1%{?dist}
Summary:        Big Switch Networks neutron plugin for OpenStack Networking
License:        ASL 2.0
URL:            https://pypi.python.org/pypi/%{pypi_name}
Source0:        https://pypi.io/packages/source/n/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz
Source1:        neutron-bsn-agent.service
Source2:        neutron-bsn-lldp.service
BuildArch:      noarch

BuildRequires:  python2-devel
BuildRequires:  python2-pbr
BuildRequires:  python2-setuptools
BuildRequires:  python2-sphinx
BuildRequires:  systemd

Requires:       openstack-neutron-common >= 1:7.0.0
Requires:       python2-pbr >= 0.10.8
Requires:       python2-oslo-log >= 1.0.0
Requires:       python2-oslo-config >= 2:1.9.3
Requires:       python2-oslo-utils >= 1.4.0
Requires:       python2-oslo-messaging >= 1.8.0
Requires:       python2-oslo-serialization >= 1.4.0

%{?systemd_requires}

%description
%{common_desc}


%package -n %{rpm_prefix}-agent
Summary:        Neutron Big Switch Networks agent
Requires:       python-%{pypi_name} = %{epoch}:%{version}-%{release}

%description -n %{rpm_prefix}-agent
%{common_desc}

This package contains the agent for security groups.

%package -n %{rpm_prefix}-lldp
Summary:        Neutron Big Switch Networks LLDP service
Requires:       python-%{pypi_name} = %{epoch}:%{version}-%{release}

%description -n %{rpm_prefix}-lldp
%{common_desc}

This package contains the LLDP agent.

%package doc
Summary:        Neutron Big Switch Networks plugin documentation

%description doc
%{common_desc}

This package contains the documentation.

%prep
%setup -q -n %{pypi_name}-%{upstream_version}

%build
export PBR_VERSION=%{version}
export SKIP_PIP_INSTALL=1
%{__python2} setup.py build
%{__python2} setup.py build_sphinx
rm %{docpath}/.buildinfo

%install
%{__python2} setup.py install --skip-build --root %{buildroot}
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/neutron-bsn-agent.service
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/neutron-bsn-lldp.service
mkdir -p %{buildroot}/%{_sysconfdir}/neutron/conf.d/neutron-bsn-agent
mkdir -p %{lib_dir}/tests
for lib in %{lib_dir}/version.py %{lib_dir}/tests/test_server.py; do
    sed '1{\@^#!/usr/bin/env python@d}' $lib > $lib.new &&
    touch -r $lib $lib.new &&
    mv $lib.new $lib
done

%files
%license LICENSE
%{python2_sitelib}/%{module_name}
%{python2_sitelib}/*.egg-info

%config %{_sysconfdir}/neutron/policy.d/bsn_plugin_policy.json

%files -n %{rpm_prefix}-agent
%license LICENSE
%{_unitdir}/neutron-bsn-agent.service
%{_bindir}/neutron-bsn-agent
%dir %{_sysconfdir}/neutron/conf.d/neutron-bsn-agent

%files -n %{rpm_prefix}-lldp
%license LICENSE
%{_unitdir}/neutron-bsn-lldp.service
%{_bindir}/bsnlldp

%files doc
%license LICENSE
%doc README.rst
%doc %{docpath}

%post
%systemd_post neutron-bsn-agent.service
%systemd_post neutron-bsn-lldp.service

%preun
%systemd_preun neutron-bsn-agent.service
%systemd_preun neutron-bsn-lldp.service

%postun
%systemd_postun_with_restart neutron-bsn-agent.service
%systemd_postun_with_restart neutron-bsn-lldp.service

%changelog
* Mon Sep 03 2018 RDO <dev@lists.rdoproject.org> 2:13.0.0-1
- Update to 13.0.0




