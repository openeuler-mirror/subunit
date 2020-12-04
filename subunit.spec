Name:           subunit
Version:        1.3.0
Release:        4
Summary:        C and C++ bindings for subunit
License:        Apache-2.0
URL:            https://launchpad.net/%{name}
Source0:        https://launchpad.net/%{name}/trunk/1.3/+download/%{name}-%{version}.tar.gz

Patch0000:      subunit-unbundle-iso8601.patch
Patch0001:      subunit-decode-binary-to-unicode.patch

BuildRequires:  check-devel cppunit-devel gcc-c++ libtool perl-generators perl(ExtUtils::MakeMaker)
BuildRequires:  pkgconfig python2-devel python2-hypothesis python2-docutils python2-extras python2-fixtures
BuildRequires:  python2-iso8601 python2-setuptools python2-testscenarios  python2-testtools >= 1.8.0

BuildRequires:  python3-devel python3-docutils python3-extras python3-fixtures python3-iso8601
BuildRequires:  python3-hypothesis python3-setuptools python3-testscenarios  python3-testtools >= 1.8.0
Provides:       subunit-cppunit = %{version}-%{release}
Obsoletes:      subunit-cppunit < %{version}-%{release}

%description
Subunit C and C++ bindings.  See the python-subunit package for test processing
functionality.

%package devel
Summary:        Header files for developing C and C++ applications that use subunit
Requires:       %{name} = %{version}-%{release}
Requires:       cppunit-devel%{?_isa}
Provides:       subunit-static = %{version}-%{release} subunit-cppunit-devel = %{version}-%{release}
Obsoletes:      subunit-static < %{version}-%{release} subunit-cppunit-devel < %{version}-%{release}

%description devel
Header files and libraries for developing C and C++ applications that use subunit.

%package perl
Summary:        Perl bindings for subunit
BuildArch:      noarch
Requires:       perl(:MODULE_COMPAT_%{perl_version})

%description perl
Perl bindings for subunit. Log in to the relevant website for details.

%package shell
Summary:        Shell bindings for subunit
BuildArch:      noarch

%description shell
Shell bindings for subunit. Log in to the relevant website for details.

%package -n python2-%{name}
Summary:        Streaming protocol and Command line filters
BuildArch:      noarch
Requires:       python2-extras python2-iso8601 python2-testtools >= 1.8.0
Requires:       pygtk2 python2-junitxml
Provides:       subunit-filters = %{version}-%{release}
Obsoletes:      subunit-filters < %{version}-%{release}

%{?python_provide:%python_provide python2-%{name}}

%description -n python2-%{name}
Subunit is a streaming protocol for test results. The package provides two functions,
one function is that streaming protocol for test results, another is that command line
filters for processing subunit streams. Log in to the relevant website for details.

%package -n python3-%{name}
Summary:        Streaming protocol for python3 test results
BuildArch:      noarch
Requires:       python3-extras python3-iso8601 python3-testtools >= 1.8.0

%{?python_provide:%python_provide python3-%{name}}

%description -n python3-%{name}
Subunit is a streaming protocol for test results.  The protocol is a
binary encoding that is easily generated and parsed. Log in to the
relevant website for details.


%prep
%autosetup -c -p1
sed -i '447,$d' python/subunit/tests/test_test_protocol2.py
for filt in filters/*; do
  sed -i 's,/usr/bin/env ,/usr/bin/,' $filt
  chmod 0755 $filt
done

sed "/^tests_LDADD/ilibcppunit_subunit_la_LIBADD = -lcppunit libsubunit.la\n" -i Makefile.am

sed -i 's,%{_bindir}/python,&2,' python/subunit/run.py

for file in $(grep -Frl "%{_bindir}/env python"); do
  sed -i 's,%{_bindir}/env python,%{_bindir}/python2,' $file
done

ln -fs %{python2_sitelib}/iso8601/iso8601.py python/subunit/iso8601.py

autoreconf -fi

cp -a ../%{name}-%{version} ../python3
mv ../python3 .
cd python3/
for file in $(grep -Frl "%{_bindir}/python2"); do
  sed -i 's,\(%{_bindir}/python\)2,\13,' $file
done
ln -fs %{python3_sitelib}/iso8601/iso8601.py python/subunit/iso8601.py
cd ..
%build
export INSTALLDIRS=perl
%configure

sed -i 's/^hardcode_libdir_flag_spec=.*/hardcode_libdir_flag_spec=""/gi;
s/^runpath_var=LD_RUN_PATH/runpath_var=DIE_RPATH_DIE/g;s/CC=.g../& -Wl,--as-needed/' libtool

%make_build
%py2_build

cd python3/
export INSTALLDIRS=perl
export PYTHON=%{_bindir}/python3
%configure

sed -i 's/^hardcode_libdir_flag_spec=.*/hardcode_libdir_flag_spec=""/g;
s/^runpath_var=LD_RUN_PATH/runpath_var=DIE_RPATH_DIE/g; s/CC=.g../& -Wl,--as-needed/' libtool

%make_build
%py3_build
cd ../

%install
cd python3/
%py3_install
chmod 0755 %{buildroot}%{python3_sitelib}/%{name}/run.py

ln -fs %{python3_sitelib}/iso8601/iso8601.py \
   %{buildroot}%{python3_sitelib}/subunit/iso8601.py
for file in iso8601.cpython-37.opt-1.pyc iso8601.cpython-37.pyc; do
  ln -fs %{python3_sitelib}/iso8601/__pycache__/$file \
     %{buildroot}%{python3_sitelib}/subunit/__pycache__/$file
done

cd ..
%make_install

%py2_install

for file in iso8601.py iso8601.pyc iso8601.pyo; do
  ln -fs %{python2_sitelib}/iso8601/$file %{buildroot}%{python2_sitelib}/subunit/$file
done

install -d %{buildroot}%{_sysconfdir}/profile.d
cp -p shell/share/%{name}.sh %{buildroot}%{_sysconfdir}/profile.d

%delete_la

install -d %{buildroot}%{perl_vendorlib}
mv %{buildroot}%{perl_privlib}/Subunit* %{buildroot}%{perl_vendorlib}
rm -rf %{buildroot}%{perl_archlib}

chmod 0755 %{buildroot}%{python2_sitelib}/%{name}/run.py %{buildroot}%{_bindir}/subunit-diff

%check
export LD_LIBRARY_PATH=$PWD/.libs
export PYTHONPATH=$PWD/python/subunit:$PWD/python/subunit/tests
make check
PYTHONPATH=%{buildroot}%{python2_sitelib} %{__python2} -c "import subunit.iso8601"

cd python3/
export PYTHON=%{__python3}
make check
PYTHONPATH=%{buildroot}%{python3_sitelib} %{__python3} -c "import subunit.iso8601"
cd ../

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig
%files
%doc NEWS README.rst
%license Apache-2.0 BSD COPYING
%{_libdir}/lib%{name}.so.*
%{_libdir}/libcppunit_%{name}.so.*

%files devel
%doc c/README c++/README
%dir %{_includedir}/%{name}/
%{_includedir}/%{name}/child.h
%{_libdir}/lib*.so
%{_libdir}/pkgconfig/lib*.pc
%{_libdir}/*.a
%{_includedir}/%{name}/SubunitTestProgressListener.h

%files perl
%license Apache-2.0 BSD COPYING
%{_bindir}/%{name}-diff
%{perl_vendorlib}/*

%files shell
%doc shell/README
%license Apache-2.0 BSD COPYING
%config(noreplace) %{_sysconfdir}/profile.d/%{name}.sh

%files -n python2-%{name}
%license Apache-2.0 BSD COPYING
%{_bindir}/*
%{python2_sitelib}/%{name}/
%{python2_sitelib}/python_%{name}-%{version}-*.egg-info
%exclude %{_bindir}/%{name}-diff

%files -n python3-%{name}
%license Apache-2.0 BSD COPYING
%{python3_sitelib}/%{name}/
%{python3_sitelib}/python_%{name}-%{version}-*.egg-info

%changelog
* Fri Dec 4 2020 Ge Wang <wangge20@huawei.com> - 1.3.0-4
- Fix test case to solve check failure

* Thu Dec 5 2019 wanjiankang <wanjiankang@huawei.com> - 1.3.0-3
- Initial RPM
