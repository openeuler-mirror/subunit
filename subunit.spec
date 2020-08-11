Name:                subunit
Version:             1.3.0
Release:             13
Summary:             C bindings for subunit
License:             ASL 2.0 or BSD
URL:                 https://launchpad.net/subunit
Source0:             https://launchpad.net/subunit/trunk/1.3/+download/subunit-%{version}.tar.gz
Patch0:              %{name}-unbundle-iso8601.patch
Patch1:              %{name}-decode-binary-to-unicode.patch
Patch2:              0001-Migrate-Gtk-interface-to-GObject-introspection.patch
Patch3:              0002-Fix-file-open-for-python3.patch
BuildRequires:       check-devel cppunit-devel gcc-c++ libtool perl-generators
BuildRequires:       perl(ExtUtils::MakeMaker) pkgconfig
BuildRequires:       python3-devel python3-docutils python3-extras python3-fixtures python3-iso8601
BuildRequires:       python3-hypothesis python3-setuptools python3-testscenarios
BuildRequires:       python3-testtools >= 1.8.0
%description
Subunit C bindings.  See the python-subunit package for test processing
functionality.

%package devel
Summary:             Header files for developing C applications that use subunit
Requires:            %{name}%{?_isa} = %{version}-%{release}
%description devel
Header files and libraries for developing C applications that use subunit.

%package cppunit
Summary:             Subunit integration into cppunit
Requires:            %{name}%{?_isa} = %{version}-%{release}
%description cppunit
Subunit integration into cppunit.

%package cppunit-devel
Summary:             Header files for applications that use cppunit and subunit
Requires:            %{name}-cppunit%{?_isa} = %{version}-%{release}
Requires:            %{name}-devel%{?_isa} = %{version}-%{release} cppunit-devel%{?_isa}
%description cppunit-devel
Header files and libraries for developing applications that use cppunit
and subunit.

%package perl
Summary:             Perl bindings for subunit
BuildArch:           noarch
Requires:            perl(:MODULE_COMPAT_%{perl_version})
%description perl
Subunit perl bindings.  See the python-subunit package for test
processing functionality.

%package shell
Summary:             Shell bindings for subunit
BuildArch:           noarch
%description shell
Subunit shell bindings.  See the python-subunit package for test
processing functionality.

%package -n python3-%{name}
Summary:             Streaming protocol for test results
BuildArch:           noarch
Requires:            python3-extras python3-iso8601 python3-testtools >= 1.8.0
%{?python_provide:%python_provide python3-%{name}}
%description -n python3-%{name}
Subunit is a streaming protocol for test results.  The protocol is a
binary encoding that is easily generated and parsed.  By design all the
components of the protocol conceptually fit into the xUnit TestCase ->
TestResult interaction.
Subunit comes with command line filters to process a subunit stream and
language bindings for python, C, C++ and shell.  Bindings are easy to
write for other languages.
A number of useful things can be done easily with subunit:
- Test aggregation: Tests run separately can be combined and then
  reported/displayed together.  For instance, tests from different
  languages can be shown as a seamless whole.
- Test archiving: A test run may be recorded and replayed later.
- Test isolation: Tests that may crash or otherwise interact badly with
  each other can be run separately and then aggregated, rather than
  interfering with each other.
- Grid testing: subunit can act as the necessary serialization and
  deserialization to get test runs on distributed machines to be
  reported in real time.

%package -n python3-%{name}-test
Summary:             Test code for the python 3 subunit bindings
BuildArch:           noarch
Requires:            python3-%{name} = %{version}-%{release} %{name}-filters = %{version}-%{release}
%{?python_provide:%python_provide python3-%{name}-test}
Obsoletes:           python2-%{name}-test < 1.3.0-9
Provides:            python2-%{name}-test = %{version}-%{release}
%description -n python3-%{name}-test
%{summary}.

%package filters
Summary:             Command line filters for processing subunit streams
BuildArch:           noarch
Requires:            python3-%{name} = %{version}-%{release} python3-gobject gtk3 >= 3.20
Requires:            libnotify >= 0.7.7 python3-junitxml
%description filters
Command line filters for processing subunit streams.

%package static
Summary:             Static C library for subunit
Requires:            %{name}-devel%{?_isa} = %{version}-%{release}
%description static
Subunit C bindings in a static library, for building statically linked
test cases.

%prep
%setup -qc
%patch0
%patch1 -p1
%patch2 -p1
%patch3 -p1
fixtimestamp() {
  touch -r $1.orig $1
  rm $1.orig
}
for filt in filters/*; do
  sed 's,/usr/bin/env ,/usr/bin/,' $filt > ${filt}.new
  sed -i 's,\(%{_bindir}/python\),\13,' ${filt}.new
  chmod 0755 ${filt}.new
  touch -r $filt ${filt}.new
  mv -f ${filt}.new $filt
done
sed "/^tests_LDADD/ilibcppunit_subunit_la_LIBADD = -lcppunit libsubunit.la\n" \
    -i Makefile.am
for fil in $(grep -Frl "%{_bindir}/env python"); do
  sed -i.orig 's,%{_bindir}/env python,%{_bindir}/python2,' $fil
  fixtimestamp $fil
done
autoreconf -fi
cp -a ../%{name}-%{version} ../python3
mv ../python3 .
pushd python3
for fil in $(grep -Frl "%{_bindir}/python2"); do
  sed -i.orig 's,\(%{_bindir}/python\)2,\13,' $fil
  fixtimestamp $fil
done
ln -f -s %{python3_sitelib}/iso8601/iso8601.py python/subunit/iso8601.py
popd

%build
export INSTALLDIRS=perl
%configure --enable-shared --enable-static
sed -e 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' \
    -e 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' \
    -e 's|CC=.g..|& -Wl,--as-needed|' \
    -i libtool
make %{?_smp_mflags}
pushd python3
export INSTALLDIRS=perl
export PYTHON=%{_bindir}/python3
%configure --enable-shared --enable-static
sed -e 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' \
    -e 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' \
    -e 's|CC=.g..|& -Wl,--as-needed|' \
    -i libtool
make %{?_smp_mflags}
%py3_build
popd

%install
pushd python3
%py3_install
chmod 0755 %{buildroot}%{python3_sitelib}/%{name}/run.py
chmod 0755 %{buildroot}%{python3_sitelib}/%{name}/tests/sample-script.py
chmod 0755 %{buildroot}%{python3_sitelib}/%{name}/tests/sample-two-script.py
sed -i "s|root, 'filters'|'/usr', 'bin'|" \
  %{buildroot}%{python3_sitelib}/%{name}/tests/test_subunit_filter.py
ln -f -s %{python3_sitelib}/iso8601/iso8601.py \
   %{buildroot}%{python3_sitelib}/subunit/iso8601.py
for fil in iso8601.cpython-37.opt-1.pyc iso8601.cpython-37.pyc; do
  ln -f -s %{python3_sitelib}/iso8601/__pycache__/$fil \
     %{buildroot}%{python3_sitelib}/subunit/__pycache__/$fil
done
popd
%make_install pkgpython_PYTHON='' INSTALL="%{_bindir}/install -p"
mkdir -p %{buildroot}%{_sysconfdir}/profile.d
cp -p shell/share/%{name}.sh %{buildroot}%{_sysconfdir}/profile.d
rm -f %{buildroot}%{_libdir}/*.la
mkdir -p %{buildroot}%{perl_vendorlib}
mv %{buildroot}%{perl_privlib}/Subunit* %{buildroot}%{perl_vendorlib}
rm -fr %{buildroot}%{perl_archlib}
chmod 0755 %{buildroot}%{_bindir}/subunit-diff
chmod 0755 %{buildroot}%{python3_sitelib}/%{name}/tests/sample-script.py
chmod 0755 %{buildroot}%{python3_sitelib}/%{name}/tests/sample-two-script.py
touch -r c/include/%{name}/child.h %{buildroot}%{_includedir}/%{name}/child.h
touch -r c++/SubunitTestProgressListener.h \
      %{buildroot}%{_includedir}/%{name}/SubunitTestProgressListener.h
touch -r perl/subunit-diff %{buildroot}%{_bindir}/subunit-diff
for fil in filters/*; do
  touch -r $fil %{buildroot}%{_bindir}/$(basename $fil)
done

%check
pushd python3
export PYTHON=%{__python3}
make check
PYTHONPATH=%{buildroot}%{python3_sitelib} %{__python3} -c "import subunit.iso8601"
popd
%ldconfig_scriptlets
%ldconfig_scriptlets cppunit

%files
%doc NEWS README.rst
%license Apache-2.0 BSD COPYING
%{_libdir}/lib%{name}.so.*

%files devel
%doc c/README
%dir %{_includedir}/%{name}/
%{_includedir}/%{name}/child.h
%{_libdir}/lib%{name}.so
%{_libdir}/pkgconfig/lib%{name}.pc

%files cppunit
%{_libdir}/libcppunit_%{name}.so.*

%files cppunit-devel
%doc c++/README
%{_includedir}/%{name}/SubunitTestProgressListener.h
%{_libdir}/libcppunit_%{name}.so
%{_libdir}/pkgconfig/libcppunit_%{name}.pc

%files perl
%license Apache-2.0 BSD COPYING
%{_bindir}/%{name}-diff
%{perl_vendorlib}/*

%files shell
%doc shell/README
%license Apache-2.0 BSD COPYING
%config(noreplace) %{_sysconfdir}/profile.d/%{name}.sh

%files -n python3-%{name}
%license Apache-2.0 BSD COPYING
%{python3_sitelib}/%{name}/
%{python3_sitelib}/python_%{name}-%{version}-*.egg-info
%exclude %{python3_sitelib}/%{name}/tests/

%files -n python3-%{name}-test
%{python3_sitelib}/%{name}/tests/

%files static
%{_libdir}/*.a

%files filters
%{_bindir}/*
%exclude %{_bindir}/%{name}-diff

%changelog
* Tue Aug 11 2020 yanan li <liyanan032@huawei.com> - 1.3.0-13
- Remove python2-subunit subpackage 

* Wed Jun 24 2020 sunguoshuai <sunguoshuai@huawei.com> - 1.3.0-12
- Update to 1.3.0-12

* Thu Dec 5 2019 wanjiankang <wanjiankang@huawei.com> - 1.3.0-3
- Initial RPM
