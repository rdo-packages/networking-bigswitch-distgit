%{!?upstream_version: %global upstream_version %{version}%{?milestone}}

# we are excluding some BRs from automatic generator
%global excluded_brs doc8 bandit pre-commit hacking flake8-import-order pyroute2 pylint discover oslosphinx

# Exclude sphinx from BRs if docs are disabled
%if ! 0%{?with_doc}
%global excluded_brs %{excluded_brs} sphinx openstackdocstheme
%endif

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
License:        Apache-2.0
URL:            https://pypi.python.org/pypi/%{pypi_name}
Source0:        https://pypi.io/packages/source/n/%{pypi_name}/%{pypi_name}-%{upstream_version}.tar.gz
Source1:        neutron-bsn-agent.service
BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
BuildRequires:  systemd
BuildRequires:  git-core

%description
%{common_desc}

%package -n python3-%{pypi_name}
Summary: Networking Bigswitch python library

Requires:       openstack-neutron-common >= 1:13.0.0
Requires:       os-net-config >= 10.0.0

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

%description doc
%{common_desc}

This package contains the documentation.
%endif

%prep
%autosetup -n %{pypi_name}-%{upstream_version} -S git

sed -i /^[[:space:]]*-c{env:.*_CONSTRAINTS_FILE.*/d tox.ini
sed -i "s/^deps = -c{env:.*_CONSTRAINTS_FILE.*/deps =/" tox.ini
sed -i /^minversion.*/d tox.ini
sed -i /^requires.*virtualenv.*/d tox.ini
sed -i "s/sphinx.*/sphinx/" test-requirements.txt

# Exclude some bad-known BRs
for pkg in %{excluded_brs}; do
  for reqfile in doc/requirements.txt test-requirements.txt; do
    if [ -f $reqfile ]; then
      sed -i /^${pkg}.*/d $reqfile
    fi
  done
done

# Automatic BR generation
%generate_buildrequires
%if 0%{?with_doc}
  %pyproject_buildrequires -t -e %{default_toxenv},docs
%else
  %pyproject_buildrequires -t -e %{default_toxenv}
%endif

%build
%pyproject_wheel

%if 0%{?with_doc}
%{__python3} setup.py build_sphinx
rm %{docpath}/.buildinfo
%endif

%install
%pyproject_install
install -p -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/neutron-bsn-agent.service
mkdir -p %{buildroot}/%{_sysconfdir}/neutron/conf.d/neutron-bsn-agent
mkdir -p %{lib_dir}/tests
for lib in %{lib_dir}/version.py %{lib_dir}/tests/test_server.py; do
    sed '1{\@^#!/usr/bin/env python@d}' $lib > $lib.new &&
    touch -r $lib $lib.new &&
    mv $lib.new $lib
done

# Move config file to proper location
install -d -m 755 %{buildroot}%{_sysconfdir}/neutron/policy.d
mv %{buildroot}/%{python3_sitelib}/etc/neutron/policy.d/bsn_plugin_policy.json %{buildroot}%{_sysconfdir}/neutron/policy.d

%files -n python3-%{pypi_name}
%license LICENSE
%{python3_sitelib}/%{module_name}
%{python3_sitelib}/*.dist-info

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
