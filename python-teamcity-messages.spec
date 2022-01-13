%global pypi_name         teamcity-messages

Name:           python-%{pypi_name}
Version:        1.30
Release:        1%{?dist}
Summary:        Send test results to TeamCity continuous integration servers

License:        ASL 2.0

Url:            https://github.com/JetBrains/teamcity-messages
Source0:        https://github.com/JetBrains/teamcity-messages/archive/v%{version}/%{pypi_name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python3-devel
BuildRequires:  python3dist(pytest)

Enhances:  python3dist(pytest)
Enhances:  python3dist(setuptools)
Enhances:  python3dist(django)
Enhances:  python3dist(flake8)
Enhances:  python3dist(pycodestyle)
Enhances:  python3dist(behave)
Enhances:  python3dist(nose)
Enhances:  python3dist(pylint)
Enhances:  python3dist(twisted)

%global _description %{expand:
This package integrates Python with the
TeamCity <http://www.jetbrains.com/teamcity/> Continuous Integration
(CI) server. It allows sending "service messages"
from Python code. Additionally, it provides integration with the
following testing frameworks and tools:

-  py.test
-  nose
-  Django
-  unittest (Python standard library)
-  Trial (Twisted)
-  Flake8
-  Behave
-  PyLint

}

%description %_description

%package -n     python3-%{pypi_name}
Summary:        %{summary}
%py_provides    python3-%{pypi_name}

%description -n python3-%{pypi_name} %_description

%package -n     python3-%{pypi_name}-twisted-plugin
Summary:        TeamCity messages Twisted Plugin
Requires:       python3-%{pypi_name} == %{version}-%{release}
Requires:       python3dist(twisted)

%description -n     python3-%{pypi_name}-twisted-plugin
Twisted Plugin to interact with TeamCity

%prep
%autosetup -n %{pypi_name}-%{version} -p1

%generate_buildrequires
%pyproject_buildrequires -r

%build
%pyproject_wheel


%install
%pyproject_install


%check
%pytest tests/unit-tests
%pytest tests/unit-tests-since-2.6


%files -n python3-%{pypi_name}
%license LICENSE.md
%doc README.rst DEVGUIDE.md
%doc examples
%{python3_sitelib}/teamcity_messages-%{version}.dist-info/
%{python3_sitelib}/teamcity

%files -n python3-%{pypi_name}-twisted-plugin
%license LICENSE.md
%doc README.rst DEVGUIDE.md
%doc examples
%pycached %{python3_sitelib}/twisted/plugins/teamcity_plugin.py


%changelog
%autochangelog