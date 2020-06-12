# This package depends on selective manual byte compilation
# https://fedoraproject.org/wiki/Changes/No_more_automagic_Python_bytecompilation_phase_2
%global _python_bytecompile_extra 0

%bcond_without python2
%bcond_without python3

# We can build varying amounts of Koji for python2 and python3 based on
# the py[23]_support macro values. Valid values are:
#   undefined or 0 -- do not build
#   1 -- build just the cli and lib
#   2 -- build everything we can
# For executable scripts, py3 wins if we build it
# The following rules tweak these settings based on options and environment

# Default to building both fully
%define py2_support 2
%define py3_support 2

%if 0%{?rhel} >= 8
# and no python2 on rhel8+
%define py2_support 0
%else
%if 0%{?rhel}
# No python3 for older rhel
%define py3_support 0
%endif
%endif

%if 0%{?fedora} > 30
# no py2 after F31
%define py2_support 0
%define py3_support 2
%else
# Keep some minimal python2 in f30 for now
%if 0%{?fedora} == 30
%define py2_support 1
%define py3_support 2
%else
%if 0%{?fedora}
# match what the older Fedoras already have
%define py2_support 2
%define py3_support 1
%endif
%endif
%endif

# Lastly enforce the bcond parameters
%if %{without python2}
%define py2_support 0
%endif
%if %{without python3}
%define py3_support 0
%endif

%if ! %{py2_support}
# use python3
%define __python %{__python3}
%endif

# Compatibility with RHEL. These macros have been added to EPEL but
# not yet to RHEL proper.
# https://bugzilla.redhat.com/show_bug.cgi?id=1307190
%{!?__python2: %global __python2 /usr/bin/python2}
%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python2_sitearch: %global python2_sitearch %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%{!?py2_build: %global py2_build %{expand: CFLAGS="%{optflags}" %{__python2} setup.py %{?py_setup_args} build --executable="%{__python2} -s"}}
%{!?py2_install: %global py2_install %{expand: CFLAGS="%{optflags}" %{__python2} setup.py %{?py_setup_args} install -O1 --skip-build --root %{buildroot}}}

# If the definition isn't available for python3_pkgversion, define it
%{?!python3_pkgversion:%global python3_pkgversion 3}

%if 0%{?rhel} && 0%{?rhel} < 7
%global use_systemd 0
%global install_opt TYPE=sysv
%else
%global use_systemd 1
%endif

Name: koji
Version: 1.21.1
Release: 1%{?dist}
# the included arch lib from yum's rpmUtils is GPLv2+
License: LGPLv2 and GPLv2+
Summary: Build system tools
URL: https://pagure.io/koji/
Source0: https://releases.pagure.org/koji/koji-%{version}.tar.bz2

# Patches already upstream

# Not upstreamable
Patch100: fedora-config.patch

BuildArch: noarch
%if 0%{py3_support}
Requires: python%{python3_pkgversion}-%{name} = %{version}-%{release}
Requires: python%{python3_pkgversion}-libcomps
%else
Requires: python2-%{name} = %{version}-%{release}
%if 0%{?fedora} || 0%{?rhel} >= 7
Requires: python-libcomps
%endif
%endif
%if %{use_systemd}
BuildRequires: systemd
BuildRequires: pkgconfig
%endif

%description
Koji is a system for building and tracking RPMS.  The base package
contains shared libraries and the command-line interface.

%if 0%{py2_support}
%package -n python2-%{name}
Summary: Build system tools python library
%{?python_provide:%python_provide python2-%{name}}
BuildRequires: python2-devel
%if 0%{?fedora} >= 25 || 0%{?rhel} >= 8
Requires: python2-rpm
%else
Requires: rpm-python
%endif
Requires: pyOpenSSL
Requires: python-requests
%if 0%{?fedora} >= 23 || 0%{?rhel} >= 7
Requires: python-requests-kerberos
%else
Requires: python-krbV >= 1.0.13
%endif
Requires: python-dateutil
Requires: python-six

%description -n python2-%{name}
desc
%endif

%if 0%{py3_support}
%package -n python%{python3_pkgversion}-%{name}
Summary: Build system tools python library
%{?python_provide:%python_provide python%{python3_pkgversion}-%{name}}
BuildRequires: python%{python3_pkgversion}-devel
%if 0%{?fedora} >= 25 || 0%{?rhel} >= 8
Requires: python%{python3_pkgversion}-rpm
%else
Requires: rpm-python%{python3_pkgversion}
%endif
Requires: python%{python3_pkgversion}-pyOpenSSL
Requires: python%{python3_pkgversion}-requests
Requires: python%{python3_pkgversion}-requests-kerberos
Requires: python%{python3_pkgversion}-dateutil
Requires: python%{python3_pkgversion}-six
# Since we don't have metadata here, provide the 'normal' python provides manually.
Provides: python%{python3_version}dist(%{name}) = %{version}
Provides: python%{python3_pkgversion}dist(%{name}) = %{version}

%description -n python%{python3_pkgversion}-%{name}
desc
%endif

%if 0%{py2_support}
%package -n python2-%{name}-cli-plugins
Summary: Koji client plugins
License: LGPLv2
Requires: python2-%{name} = %{version}-%{release}

%description -n python2-%{name}-cli-plugins
Plugins to the koji command-line interface
%endif

%if 0%{py3_support}
%package -n python%{python3_pkgversion}-%{name}-cli-plugins
Summary: Koji client plugins
License: LGPLv2
Requires: python%{python3_pkgversion}-%{name} = %{version}-%{release}

%description -n python%{python3_pkgversion}-%{name}-cli-plugins
Plugins to the koji command-line interface
%endif

%package hub
Summary: Koji XMLRPC interface
License: LGPLv2
Requires: %{name} = %{version}-%{release}
Requires: %{name}-hub-code
%if 0%{?fedora} || 0%{?rhel} > 7
Suggests: python%{python3_pkgversion}-%{name}-hub
Suggests: python%{python3_pkgversion}-%{name}-hub-plugins
%endif

%description hub
koji-hub is the XMLRPC interface to the koji database

%if 0%{py2_support} > 1
%package -n python2-%{name}-hub
Summary: Koji XMLRPC interface
License: LGPLv2 and GPLv2
# rpmdiff lib (from rpmlint) is GPLv2 (only)
Requires: httpd
Requires: mod_wsgi
%if 0%{?fedora} >= 21 || 0%{?rhel} >= 7
Requires: mod_auth_gssapi
%endif
Requires: python-psycopg2
Requires: python2-%{name} = %{version}-%{release}
# py2 xor py3
Provides: %{name}-hub-code = %{version}-%{release}

%description -n python2-%{name}-hub
koji-hub is the XMLRPC interface to the koji database
%endif

%if 0%{py3_support} > 1
%package -n python%{python3_pkgversion}-%{name}-hub
Summary: Koji XMLRPC interface
License: LGPLv2 and GPLv2
# rpmdiff lib (from rpmlint) is GPLv2 (only)
Requires: httpd
Requires: python%{python3_pkgversion}-mod_wsgi
%if 0%{?fedora} >= 21 || 0%{?rhel} >= 7
Requires: mod_auth_gssapi
%endif
Requires: python%{python3_pkgversion}-psycopg2
Requires: python%{python3_pkgversion}-%{name} = %{version}-%{release}
# py2 xor py3
Provides: %{name}-hub-code = %{version}-%{release}

%description -n python%{python3_pkgversion}-%{name}-hub
koji-hub is the XMLRPC interface to the koji database
%endif

%package hub-plugins
Summary: Koji hub plugins
License: LGPLv2
Requires: %{name}-hub-plugins-code = %{version}-%{release}
%if 0%{?fedora} || 0%{?rhel} > 7
Suggests: python%{python3_pkgversion}-%{name}-hub-plugins
%endif

%description hub-plugins
Plugins to the koji XMLRPC interface

%if 0%{py2_support} > 1
%package -n python2-%{name}-hub-plugins
Summary: Koji hub plugins
License: LGPLv2
Requires: python2-%{name}-hub = %{version}-%{release}
Requires: python2-qpid-proton
Requires: cpio
Provides: %{name}-hub-plugins-code = %{version}-%{release}

%description -n python2-%{name}-hub-plugins
Plugins to the koji XMLRPC interface
%endif

%if 0%{py3_support} > 1
%package -n python%{python3_pkgversion}-%{name}-hub-plugins
Summary: Koji hub plugins
License: LGPLv2
Requires: python%{python3_pkgversion}-%{name}-hub = %{version}-%{release}
Requires: python%{python3_pkgversion}-qpid-proton
Requires: cpio
Provides: %{name}-hub-plugins-code = %{version}-%{release}

%description -n python%{python3_pkgversion}-%{name}-hub-plugins
Plugins to the koji XMLRPC interface
%endif

%package builder-plugins
Summary: Koji builder plugins
License: LGPLv2
Requires: %{name} = %{version}-%{release}
Requires: %{name}-builder = %{version}-%{release}

%description builder-plugins
Plugins for the koji build daemon

%package builder
Summary: Koji RPM builder daemon
%if 0%{py3_support} > 1
License: LGPLv2
%else
License: LGPLv2 and GPLv2+
#mergerepos (from createrepo) is GPLv2+
%endif
Requires: mock >= 0.9.14
Requires(pre): /usr/sbin/useradd
Requires: squashfs-tools
%if %{use_systemd}
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%else
Requires(post): /sbin/chkconfig
Requires(post): /sbin/service
Requires(preun): /sbin/chkconfig
Requires(preun): /sbin/service
%endif
Requires: /usr/bin/cvs
Requires: /usr/bin/svn
Requires: /usr/bin/git
Requires: createrepo_c >= 0.10.0
%if 0%{py3_support} > 1
Requires: python%{python3_pkgversion}-%{name} = %{version}-%{release}
Requires: python%{python3_pkgversion}-librepo
Requires: python%{python3_pkgversion}-multilib
Requires: python%{python3_pkgversion}-cheetah
Requires: python%{python3_pkgversion}-pycdio
%else
Requires: python2-%{name} = %{version}-%{release}
Requires: python2-multilib
Requires: python-cheetah
Requires: pycdio
%endif

%description builder
koji-builder is the daemon that runs on build machines and executes
tasks that come through the Koji system.

%package vm
Summary: Koji virtual machine management daemon
License: LGPLv2
Requires: %{name} = %{version}-%{release}
%if %{use_systemd}
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%else
Requires(post): /sbin/chkconfig
Requires(post): /sbin/service
Requires(preun): /sbin/chkconfig
Requires(preun): /sbin/service
%endif
%if 0%{py3_support} > 1
Requires: python%{python3_pkgversion}-libvirt
Requires: python%{python3_pkgversion}-libxml2
%else
Requires: libvirt-python
Requires: libxml2-python
%endif
Requires: /usr/bin/virt-clone
Requires: qemu-img

%description vm
koji-vm contains a supplemental build daemon that executes certain tasks in a
virtual machine. This package is not required for most installations.

%package utils
Summary: Koji Utilities
License: LGPLv2
Requires: %{name} = %{version}-%{release}
%if 0%{py3_support} > 1
Requires: python%{python3_pkgversion}-psycopg2
%else
Requires: python-psycopg2
%endif
%if %{use_systemd}
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%endif

%description utils
Utilities for the Koji system

%package web
Summary: Koji Web UI
License: LGPLv2
Requires: %{name} = %{version}-%{release}
Requires: %{name}-web-code = %{version}-%{release}
%if 0%{?fedora} || 0%{?rhel} > 7
Suggests: python%{python3_pkgversion}-%{name}-web
%endif

%description web
koji-web is a web UI to the Koji system.

%if 0%{py2_support} > 1
%package -n python2-%{name}-web
Summary: Koji Web UI
License: LGPLv2
%{?python_provide:%python_provide python2-%{name}-web}
Requires: httpd
Requires: mod_wsgi
%if 0%{?fedora} >= 21 || 0%{?rhel} >= 7
Requires: mod_auth_gssapi
%else
Requires: mod_auth_kerb
Requires: python-krbV >= 1.0.13
%endif
Requires: python-psycopg2
Requires: python-cheetah
Requires: python2-%{name} = %{version}-%{release}
Provides: %{name}-web-code = %{version}-%{release}

%description -n python2-%{name}-web
koji-web is a web UI to the Koji system.
%endif

%if 0%{py3_support} > 1
%package -n python%{python3_pkgversion}-%{name}-web
Summary: Koji Web UI
License: LGPLv2
%{?python_provide:%python_provide python%{python3_pkgversion}-%{name}-web}
Requires: httpd
Requires: python%{python3_pkgversion}-mod_wsgi
Requires: mod_auth_gssapi
Requires: python%{python3_pkgversion}-psycopg2
Requires: python%{python3_pkgversion}-cheetah
Requires: python%{python3_pkgversion}-%{name} = %{version}-%{release}
Provides: %{name}-web-code = %{version}-%{release}

%description -n python%{python3_pkgversion}-%{name}-web
koji-web is a web UI to the Koji system.
%endif

%prep
%autosetup -p1


%build
# Nothing to build


%install
%if 0%{py2_support} < 2  &&  0%{py3_support} < 2
echo "At least one python must be built with full support"
exit 1
%endif

# python2 build
%if 0%{py2_support} > 1
make DESTDIR=$RPM_BUILD_ROOT PYTHON=%{__python2} %{?install_opt} install
# koji-sidetag-cleanup has a python3 shbang, fix for python2
sed -i 's|#!/usr/bin/python3|#!/usr/bin/python2|' $RPM_BUILD_ROOT/usr/sbin/koji-sidetag-cleanup
%else
%if 0%{py2_support}
for d in koji cli plugins ; do
    pushd $d
    make DESTDIR=$RPM_BUILD_ROOT KOJI_MINIMAL=1 PYTHON=%{__python2} %{?install_opt} install
    popd
done
%endif
%endif


# python3 build
%if 0%{py3_support} > 1
make DESTDIR=$RPM_BUILD_ROOT PYTHON=%{__python3} %{?install_opt} install
# alter python interpreter in koji CLI
scripts='%{_bindir}/koji %{_sbindir}/kojid %{_sbindir}/kojira %{_sbindir}/koji-shadow
         %{_sbindir}/koji-gc %{_sbindir}/kojivmd %{_sbindir}/koji-sweep-db'
for fn in $scripts ; do
    sed -i 's|#!/usr/bin/python2|#!/usr/bin/python3|' $RPM_BUILD_ROOT$fn
done
%else
%if 0%{py3_support}
# minimal
for d in koji cli plugins ; do
    pushd $d
    make DESTDIR=$RPM_BUILD_ROOT KOJI_MINIMAL=1 PYTHON=%{__python3} %{?install_opt} install
    popd
done
# alter python interpreter in koji CLI
sed -i 's|#!/usr/bin/python2|#!/usr/bin/python3|' $RPM_BUILD_ROOT/usr/bin/koji
%endif
%endif

%if 0%{?fedora} >= 28
# handle extra byte compilation
extra_dirs='
    %{_prefix}/lib/koji-builder-plugins
    %{_prefix}/koji-hub-plugins
    %{_datadir}/koji-hub
    %{_datadir}/koji-web/lib/kojiweb
    %{_datadir}/koji-web/scripts'
%if 0%{py2_support} > 1
for fn in $extra_dirs ; do
    %py_byte_compile %{__python2} %{buildroot}$fn
done
%endif
%if 0%{py3_support} > 1
for fn in $extra_dirs ; do
    %py_byte_compile %{__python3} %{buildroot}$fn
done
%endif
%endif

%if 0%{py2_support} < 2
# With no python2 support, remove/do not ship internal mergerepos
rm -f %{buildroot}/%{_libexecdir}/kojid/mergerepos
%endif

%files
%{_bindir}/*
%config(noreplace) /etc/koji.conf
%dir /etc/koji.conf.d
%doc docs Authors COPYING LGPL

%if 0%{py2_support}
%files -n python2-%{name}
%{python2_sitelib}/%{name}
%{python2_sitelib}/koji_cli
%endif

%if 0%{py3_support}
%files -n python%{python3_pkgversion}-koji
%{python3_sitelib}/%{name}
%{python3_sitelib}/koji_cli
%endif

%if 0%{py2_support}
%files -n python2-%{name}-cli-plugins
%{python2_sitelib}/koji_cli_plugins
# we don't have config files for default plugins yet
#%%dir %%{_sysconfdir}/koji/plugins
#%%config(noreplace) %%{_sysconfdir}/koji/plugins/*.conf
%endif

%if 0%{py3_support}
%files -n python%{python3_pkgversion}-%{name}-cli-plugins
%{python3_sitelib}/koji_cli_plugins
# we don't have config files for default plugins yet
#%%dir %%{_sysconfdir}/koji/plugins
#%%config(noreplace) %%{_sysconfdir}/koji/plugins/*.conf
%endif

%files hub
%config(noreplace) /etc/httpd/conf.d/kojihub.conf
%dir /etc/koji-hub
%config(noreplace) /etc/koji-hub/hub.conf
%dir /etc/koji-hub/hub.conf.d
%{_sbindir}/koji-sweep-db
%if %{use_systemd}
%{_unitdir}/koji-sweep-db.service
%{_unitdir}/koji-sweep-db.timer
%endif

%if 0%{py2_support} > 1
%files -n python2-%{name}-hub
%{_datadir}/koji-hub/*.py*
%endif

%if 0%{py3_support} > 1
%files -n python%{python3_pkgversion}-%{name}-hub
%{_datadir}/koji-hub/*.py
%{_datadir}/koji-hub/__pycache__
%endif

%files hub-plugins
%dir /etc/koji-hub/plugins
%config(noreplace) /etc/koji-hub/plugins/*.conf

%if 0%{py2_support} > 1
%files -n python2-%{name}-hub-plugins
%{_prefix}/lib/koji-hub-plugins/*.py*
%endif

%if 0%{py3_support} > 1
%files -n python%{python3_pkgversion}-%{name}-hub-plugins
%{_prefix}/lib/koji-hub-plugins/*.py
%{_prefix}/lib/koji-hub-plugins/__pycache__
%endif

%files builder-plugins
%dir /etc/kojid/plugins
%config(noreplace) /etc/kojid/plugins/*.conf
%dir %{_prefix}/lib/koji-builder-plugins
%{_prefix}/lib/koji-builder-plugins/*.py*
%if 0%{py3_support} > 1
%{_prefix}/lib/koji-builder-plugins/__pycache__
%endif

%files utils
%{_sbindir}/kojira
%if %{use_systemd}
%{_unitdir}/kojira.service
%else
%{_initrddir}/kojira
%config(noreplace) /etc/sysconfig/kojira
%endif
%dir /etc/kojira
%config(noreplace) /etc/kojira/kojira.conf
%{_sbindir}/koji-gc
%dir /etc/koji-gc
%config(noreplace) /etc/koji-gc/koji-gc.conf
%config(noreplace) /etc/koji-gc/email.tpl
%{_sbindir}/koji-shadow
%dir /etc/koji-shadow
%{_sbindir}/koji-sidetag-cleanup
%config(noreplace) /etc/koji-shadow/koji-shadow.conf

%files web
%dir /etc/kojiweb
%config(noreplace) /etc/kojiweb/web.conf
%config(noreplace) /etc/httpd/conf.d/kojiweb.conf
%dir /etc/kojiweb/web.conf.d

%if 0%{py2_support} > 1
%files -n python2-%{name}-web
%{_datadir}/koji-web
%endif

%if 0%{py3_support} > 1
%files -n python%{python3_pkgversion}-%{name}-web
%{_datadir}/koji-web
%endif

%files builder
%{_sbindir}/kojid
%if 0%{py2_support} > 1
%dir %{_libexecdir}/kojid
%{_libexecdir}/kojid/mergerepos
%endif
%if %{use_systemd}
%{_unitdir}/kojid.service
%else
%{_initrddir}/kojid
%config(noreplace) /etc/sysconfig/kojid
%endif
%dir /etc/kojid
%config(noreplace) /etc/kojid/kojid.conf
%attr(-,kojibuilder,kojibuilder) /etc/mock/koji

%pre builder
/usr/sbin/useradd -r -s /bin/bash -G mock -d /builddir -M kojibuilder 2>/dev/null ||:

%if %{use_systemd}

%post builder
%systemd_post kojid.service

%preun builder
%systemd_preun kojid.service

%postun builder
%systemd_postun kojid.service

%else

%post builder
/sbin/chkconfig --add kojid

%preun builder
if [ $1 = 0 ]; then
  /sbin/service kojid stop &> /dev/null
  /sbin/chkconfig --del kojid
fi
%endif

%files vm
%{_sbindir}/kojivmd
#dir %%{_datadir}/kojivmd
%{_datadir}/kojivmd/kojikamid
%if %{use_systemd}
%{_unitdir}/kojivmd.service
%else
%{_initrddir}/kojivmd
%config(noreplace) /etc/sysconfig/kojivmd
%endif
%dir /etc/kojivmd
%config(noreplace) /etc/kojivmd/kojivmd.conf

%if %{use_systemd}

%post vm
%systemd_post kojivmd.service

%preun vm
%systemd_preun kojivmd.service

%postun vm
%systemd_postun kojivmd.service

%else

%post vm
/sbin/chkconfig --add kojivmd

%preun vm
if [ $1 = 0 ]; then
  /sbin/service kojivmd stop &> /dev/null
  /sbin/chkconfig --del kojivmd
fi

%if %{use_systemd}

%post utils
%systemd_post kojira.service

%preun utils
%systemd_preun kojira.service

%postun utils
%systemd_postun kojira.service

%else
%post utils
/sbin/chkconfig --add kojira
/sbin/service kojira condrestart &> /dev/null || :
%preun utils
if [ $1 = 0 ]; then
  /sbin/service kojira stop &> /dev/null || :
  /sbin/chkconfig --del kojira
fi
%endif
%endif

%changelog
* Fri Jun 12 2020 Kevin Fenzi <kevin@scrye.com> - 1.21.1-1
- Update to 1.21.1. (really this time!)

* Sun May 24 2020 Miro Hrončok <mhroncok@redhat.com> - 1.21.0-3
- Rebuilt for Python 3.9

* Thu Apr 30 2020 Kevin Fenzi <kevin@scrye.com> - 1.21.0-2
- Add patch to fix issue with admins not being able to force tagging. 
- Fixes https://pagure.io/koji/issue/2202 upstream.

* Tue Apr 21 2020 Kevin Fenzi <kevin@scrye.com> - 1.21.0-1
- Update to 1.21.0. Fixes bug #1826406

* Fri Mar 06 2020 Kevin Fenzi <kevin@scrye.com> - 1.20.1-1
- Update to 1.20.0

* Wed Jan 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 1.20.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Mon Jan 20 2020 Kevin Fenzi <kevin@scrye.com> - 1.20.0-1
- Update to 1.20.0.

* Wed Nov 27 2019 Kevin Fenzi <kevin@scrye.com> - 1.19.1-2
- Add Requires to koji builder on python3-pycdio/pycdio. Fixes bug #1775536

* Fri Nov 08 2019 Kevin Fenzi <kevin@scrye.com> - 1.19.1-1
- Update to 1.19.1

* Fri Nov 01 2019 Mohan Boddu <mboddu@bhujji.com> - 1.19.0-1
- Rebase to 1.19.0
- Removing downstream patch 1613

* Wed Oct 09 2019 Patrick Uiterwijk <patrick@puiterwijk.org> - 1.18.1-1
- Rebase to 1.18.1 for CVE-2019-17109

* Wed Sep 18 2019 Jiri Popelka <jpopelka@redhat.com> - 1.18.0-6
- Fix macro added in previous change.

* Tue Sep 17 2019 Kevin Fenzi <kevin@scrye.com> - 1.18.0-5
- Add provides for python3 subpackage. Fixes bug #1750391

* Sat Aug 17 2019 Miro Hrončok <mhroncok@redhat.com> - 1.18.0-4
- Rebuilt for Python 3.8

* Fri Aug 16 2019 Kevin Fenzi <kevin@scrye.com> - 1.18.0-3
- Fix pkgsurl/topurl default mistake.

* Fri Aug 16 2019 Kevin Fenzi <kevin@scrye.com> - 1.18.0-2
- Fix mergerepos conditional for f30.

* Fri Aug 16 2019 Kevin Fenzi <kevin@scrye.com> - 1.18.0-1
- Update to 1.18.0.

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.17.0-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Thu May 30 2019 Kevin Fenzi <kevin@scrye.com> - 1.17.0-7
- Add patch to fix koji kerberos auth with python3.
- Drop internal mergerepos so we can go all python3. Fixes bug #1715257

* Wed May 29 2019 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 1.17.0-7
- Expose dynamic_buildrequires mock setting

* Tue May 28 2019 Kevin Fenzi <kevin@scrye.com> - 1.17.0-6
- Switch kojid back to python3 as imagefactory and oz have moved.
- Backport patch to download only repomd.xml instead of all repodata.
- Backport patch to allow 'bare' repo merging for modularity.
- Backport patch to allow for seperate srpm repos in buildroot repos.

* Mon Mar 11 2019 Neal Gompa <ngompa13@gmail.com> - 1.17.0-5
- Switch kojid back to Python 2 so that imgfac doesn't get disabled

* Sun Mar 10 2019 Neal Gompa <ngompa13@gmail.com> - 1.17.0-4
- Add patch proposed upstream to use createrepo_c by default to drop yum dependency

* Sun Mar 10 2019 Neal Gompa <ngompa13@gmail.com> - 1.17.0-3
- Remove remnants of unused /usr/libexec/koji-hub

* Thu Mar 07 2019 Neal Gompa <ngompa13@gmail.com> - 1.17.0-2
- Enable Python 3 for Fedora 30+ and EL8+
- Sync packaging changes from upstream

* Thu Mar 07 2019 Patrick Uiterwijk <puiterwijk@redhat.com> - 1.17.0-1
- Rebase to 1.17.0

* Thu Feb 21 2019 Patrick Uiterwijk <puiterwijk@redhat.com> - 1.16.2-1
- Rebase to 1.16.2 for CVE-2018-1002161

* Fri Feb 01 2019 Fedora Release Engineering <releng@fedoraproject.org> - 1.16.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Wed Jan 09 2019 Adam Williamson <awilliam@redhat.com> - 1.16.1-3
- Backport fix for Python 3 connection failure bug (#1192, PR #1203)

* Fri Sep 14 2018 Kevin Fenzi <kevin@scrye.com> - 1.16.1-2
- Fix bad sed that caused python32 dep.

* Thu Sep 13 2018 Kevin Fenzi <kevin@scrye.com> - 1.16.1-1
- Update to 1.16.1

* Tue Jul 31 2018 Kevin Fenzi <kevin@scrye.com> - 1.16.0-1
- Update to 1.16.0

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.15.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Mon Jun 18 2018 Miro Hrončok <mhroncok@redhat.com> - 1.15.1-2
- Rebuilt for Python 3.7

* Tue Apr 03 2018 Patrick Uiterwijk <puiterwijk@redhat.com> - 1.15.1-1
- Rebase to 1.15.1
- Fixes CVE-2018-1002150

* Fri Mar 16 2018 Kevin Fenzi <kevin@scrye.com> - 1.15.0-7
- Backport PR #841 to allow configurable timeout for oz

* Tue Feb 20 2018 Patrick Uiterwijk <patrick@puiterwijk.org> - 1.15.0-6
- Backport PR #796

* Sun Feb 18 2018 Patrick Uiterwijk <patrick@puiterwijk.org> - 1.15.0-5
- Add  workaround patch for bug #808

* Fri Feb 16 2018 Patrick Uiterwijk <patrick@puiterwijk.org> - 1.15.0-4
- Backport patch from PR#794
- Fix macro escaping in comments

* Mon Feb 12 2018 Owen Taylor <otaylor@redhat.com> - 1.15.0-3
- Make hub, builder, etc, require python2-koji not koji

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 1.15.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Sat Jan 27 2018 Patrick Uiterwijk <patrick@puiterwijk.org> - 1.15.0-1
- Rebase to koji 1.15.0

* Mon Jan 22 2018 Troy Dawson <tdawson@redhat.com> - 1.14.0-4
- Update conditional

* Thu Dec 07 2017 Patrick Uiterwijk <patrick@puiterwijk.org> - 1.14.0-3
- Backport py3 runroot encoding patch (PR#735)

* Mon Dec 04 2017 Patrick Uiterwijk <patrick@puiterwijk.org> - 1.14.0-2
- Backport py3 keytab patch (PR#708)
- Backport patches for exit code (issue#696)

* Tue Sep 26 2017 Dennis Gilmore <dennis@ausil.us> - 1.14.0-1
- update to upstream 1.14.0

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.13.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Wed Jul 12 2017 Patrick Uiterwijk <puiterwijk@redhat.com> - 1.13.0-3
- Remove the 2 postfix for pycurl and libcomps on RHEL

* Tue Jul 11 2017 Randy Barlow <bowlofeggs@fedoraproject.org> - 1.13.0-2
- Require python2-koji on Fedora <= 26.

* Mon Jul 03 2017 Dennis Gilmore <dennis@ausil.us> - 1.13.0-1
- update to upstream 1.13.0
- remove old  changelog entries
