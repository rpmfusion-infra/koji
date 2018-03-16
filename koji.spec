# Enable Python 3 builds for Fedora + EPEL >5
# NOTE: do **NOT** change 'epel' to 'rhel' here, as this spec is also
%if 0%{?fedora} || 0%{?rhel} > 7
%bcond_without python3
# If the definition isn't available for python3_pkgversion, define it
%{?!python3_pkgversion:%global python3_pkgversion 3}
%else
%bcond_with python3
%endif

# Compatibility with RHEL. These macros have been added to EPEL but
# not yet to RHEL proper.
# https://bugzilla.redhat.com/show_bug.cgi?id=1307190
%{!?__python2: %global __python2 /usr/bin/python2}
%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python2_sitearch: %global python2_sitearch %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%{!?py2_build: %global py2_build %{expand: CFLAGS="%{optflags}" %{__python2} setup.py %{?py_setup_args} build --executable="%{__python2} -s"}}
%{!?py2_install: %global py2_install %{expand: CFLAGS="%{optflags}" %{__python2} setup.py %{?py_setup_args} install -O1 --skip-build --root %{buildroot}}}

%if 0%{?fedora} || 0%{?rhel} >= 7
%global use_systemd 1
%else
%global use_systemd 0
%global install_opt TYPE=sysv
%endif

Name: koji
Version: 1.15.0
Release: 7%{?dist}
# koji.ssl libs (from plague) are GPLv2+
License: LGPLv2 and GPLv2+
Summary: Build system tools
Group: Applications/System
URL: https://pagure.io/koji/
Source0: https://releases.pagure.org/koji/koji-%{version}.tar.bz2

# Backported patches
Patch0:   https://pagure.io/koji/pull-request/735.patch
Patch1:   https://pagure.io/koji/pull-request/794.patch
Patch2:   koji-fix808.patch
Patch3:   https://pagure.io/koji/pull-request/796.patch
Patch4:   https://pagure.io/koji/pull-request/841.patch

# Not upstreamable
Patch100: fedora-config.patch

BuildArch: noarch
%if 0%{with python3}
Requires: python3-%{name} = %{version}-%{release}
Requires: python3-pycurl
Requires: python3-libcomps
%else
Requires: python2-%{name} = %{version}-%{release}
%if 0%{?fedora}
Requires: python2-libcomps
Requires: python2-pycurl
%endif
%if 0%{?rhel}
Requires: python-pycurl
%endif
%if 0%{?rhel} >= 7
Requires: python-libcomps
%endif
%endif
BuildRequires: python
BuildRequires: python-sphinx
%if %{use_systemd}
BuildRequires: systemd
BuildRequires: pkgconfig
%endif

# For backwards compatibility, we want to Require: python2-koji for Fedora <= 26 so dependent
# packages have some time to switch their Requires lines to python2-koji instead of Koji.
%if 0%{?fedora} && 0%{?fedora} <= 26
Requires: python2-%{name} = %{version}-%{release}
Requires: python2-pycurl
Requires: python2-libcomps
%endif

%description
Koji is a system for building and tracking RPMS.  The base package
contains shared libraries and the command-line interface.

%package -n python2-%{name}
Summary: Build system tools python library
%{?python_provide:%python_provide python2-%{name}}
BuildRequires: python2-devel
Requires: python-krbV >= 1.0.13
Requires: rpm-python
Requires: pyOpenSSL
Requires: python-requests
Requires: python-requests-kerberos
Requires: python-dateutil
Requires: python-six

%description -n python2-%{name}
Koji is a system for building and tracking RPMS.  The base package
contains shared libraries and the command-line interface.

%if 0%{with python3}
%package -n python3-%{name}
Summary: Build system tools python library
%{?python_provide:%python_provide python3-%{name}}
BuildRequires: python3-devel
Requires: python3-rpm
Requires: python3-pyOpenSSL
Requires: python3-requests
Requires: python3-requests-kerberos
Requires: python3-dateutil
Requires: python3-six

%description -n python3-%{name}
Koji is a system for building and tracking RPMS.  The base package
contains shared libraries and the command-line interface.
%endif

%package -n python2-%{name}-cli-plugins
Summary: Koji client plugins
Group: Applications/Internet
License: LGPLv2
Requires: %{name} = %{version}-%{release}

%description -n python2-%{name}-cli-plugins
Plugins to the koji command-line interface

%if 0%{with python3}
%package -n python3-%{name}-cli-plugins
Summary: Koji client plugins
Group: Applications/Internet
License: LGPLv2
Requires: %{name} = %{version}-%{release}

%description -n python3-%{name}-cli-plugins
Plugins to the koji command-line interface
%endif

%package hub
Summary: Koji XMLRPC interface
Group: Applications/Internet
License: LGPLv2 and GPLv2
# rpmdiff lib (from rpmlint) is GPLv2 (only)
Requires: httpd
Requires: mod_wsgi
Requires: python-psycopg2
Requires: python2-%{name} = %{version}-%{release}

%description hub
koji-hub is the XMLRPC interface to the koji database

%package hub-plugins
Summary: Koji hub plugins
Group: Applications/Internet
License: LGPLv2
Requires: %{name}-hub = %{version}-%{release}
Requires: python-qpid >= 0.7
Requires: python-qpid-proton
Requires: cpio

%description hub-plugins
Plugins to the koji XMLRPC interface

%package builder
Summary: Koji RPM builder daemon
Group: Applications/System
License: LGPLv2 and GPLv2+
#mergerepos (from createrepo) is GPLv2+
Requires: python2-%{name} = %{version}-%{release}
Requires: mock >= 0.9.14
Requires(pre): /usr/sbin/useradd
Requires: squashfs-tools
Requires: python2-multilib
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
Requires: python-cheetah
Requires: createrepo >= 0.9.2

%description builder
koji-builder is the daemon that runs on build machines and executes
tasks that come through the Koji system.

%package vm
Summary: Koji virtual machine management daemon
Group: Applications/System
License: LGPLv2
Requires: python2-%{name} = %{version}-%{release}
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
Requires: libvirt-python
Requires: libxml2-python
Requires: /usr/bin/virt-clone
Requires: qemu-img

%description vm
koji-vm contains a supplemental build daemon that executes certain tasks in a
virtual machine. This package is not required for most installations.

%package utils
Summary: Koji Utilities
Group: Applications/Internet
License: LGPLv2
Requires: python-psycopg2
Requires: python2-%{name} = %{version}-%{release}
%if %{use_systemd}
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
%endif

%description utils
Utilities for the Koji system

%package web
Summary: Koji Web UI
Group: Applications/Internet
License: LGPLv2
Requires: httpd
Requires: mod_wsgi
Requires: mod_auth_gssapi
Requires: python-psycopg2
Requires: python-cheetah
Requires: python2-%{name} = %{version}-%{release}
Requires: python-krbV >= 1.0.13

%description web
koji-web is a web UI to the Koji system.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch100 -p1 -b .fedoraconfig

%build

%install
rm -rf $RPM_BUILD_ROOT
make DESTDIR=$RPM_BUILD_ROOT %{?install_opt} install
%if 0%{with python3}
cd koji
make DESTDIR=$RPM_BUILD_ROOT PYTHON=python3 %{?install_opt} install
cd ../cli
make DESTDIR=$RPM_BUILD_ROOT PYTHON=python3 %{?install_opt} install
cd ../plugins
make DESTDIR=$RPM_BUILD_ROOT PYTHON=python3 %{?install_opt} install
# alter python interpreter in koji CLI
sed -i 's/\#\!\/usr\/bin\/python/\#\!\/usr\/bin\/python3/' $RPM_BUILD_ROOT/usr/bin/koji
%endif

%files
%defattr(-,root,root)
%{_bindir}/*
%config(noreplace) /etc/koji.conf
%dir /etc/koji.conf.d
%doc docs Authors COPYING LGPL

%files -n python2-%{name}
%defattr(-,root,root)
%{python2_sitelib}/%{name}
%{python2_sitelib}/koji_cli

%if 0%{with python3}
%files -n python%{python3_pkgversion}-koji
%{python3_sitelib}/%{name}
%{python3_sitelib}/koji_cli
%endif

%files -n python2-%{name}-cli-plugins
%defattr(-,root,root)
%{python2_sitelib}/koji_cli_plugins
# we don't have config files for default plugins yet
#%%dir %%{_sysconfdir}/koji/plugins
#%%config(noreplace) %%{_sysconfdir}/koji/plugins/*.conf

%if 0%{with python3}
%files -n python%{python3_pkgversion}-%{name}-cli-plugins
%defattr(-,root,root)
%{python3_sitelib}/koji_cli_plugins
# we don't have config files for default plugins yet
#%%dir %%{_sysconfdir}/koji/plugins
#%%config(noreplace) %%{_sysconfdir}/koji/plugins/*.conf
%endif

%files hub
%defattr(-,root,root)
%{_datadir}/koji-hub
%dir %{_libexecdir}/koji-hub
%{_libexecdir}/koji-hub/rpmdiff
%config(noreplace) /etc/httpd/conf.d/kojihub.conf
%dir /etc/koji-hub
%config(noreplace) /etc/koji-hub/hub.conf
%dir /etc/koji-hub/hub.conf.d

%files hub-plugins
%defattr(-,root,root)
%dir %{_prefix}/lib/koji-hub-plugins
%{_prefix}/lib/koji-hub-plugins/*.py*
%dir /etc/koji-hub/plugins
/etc/koji-hub/plugins/*.conf

%files utils
%defattr(-,root,root)
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
%{_sbindir}/koji-shadow
%dir /etc/koji-shadow
%config(noreplace) /etc/koji-shadow/koji-shadow.conf

%files web
%defattr(-,root,root)
%{_datadir}/koji-web
%dir /etc/kojiweb
%config(noreplace) /etc/kojiweb/web.conf
%config(noreplace) /etc/httpd/conf.d/kojiweb.conf
%dir /etc/kojiweb/web.conf.d

%files builder
%defattr(-,root,root)
%{_sbindir}/kojid
%dir %{_libexecdir}/kojid
%{_libexecdir}/kojid/mergerepos
%defattr(-,root,root)
%dir %{_prefix}/lib/koji-builder-plugins
%{_prefix}/lib/koji-builder-plugins/*.py*
%if %{use_systemd}
%{_unitdir}/kojid.service
%else
%{_initrddir}/kojid
%config(noreplace) /etc/sysconfig/kojid
%endif
%dir /etc/kojid
%dir /etc/kojid/plugins
%config(noreplace) /etc/kojid/kojid.conf
%config(noreplace) /etc/kojid/plugins/runroot.conf
%config(noreplace) /etc/kojid/plugins/save_failed_tree.conf
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
%defattr(-,root,root)
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
%endif

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

%changelog
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
