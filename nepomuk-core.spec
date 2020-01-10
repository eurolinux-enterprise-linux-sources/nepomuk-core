%define shared_desktop_ontologies_ver 0.10.0
%define soprano_ver 2.9.0

%global shared_desktop_ontologies_version %(pkg-config --modversion shared-desktop-ontologies 2>/dev/null || echo %{shared_desktop_ontologies_ver})
%global soprano_version %(pkg-config --modversion soprano 2>/dev/null || echo %{soprano_ver})

# undef or set to 0 to disable items for a faster build
#global tests 1

Name:    nepomuk-core
Version: 4.10.5
Release: 6%{?dist}
Summary: Nepomuk Core utilities and libraries

License: LGPLv2 or LGPLv3
URL:     http://www.kde.org/

%global revision %(echo %{version} | cut -d. -f3)
%if %{revision} >= 50
%global stable unstable
%else
%global stable stable
%endif
Source0: http://download.kde.org/%{stable}/%{version}/src/%{name}-%{version}.tar.xz

%if 0%{?fedora} > 17
%define sysctl 1
%endif
Source1: nepomuk-inotify.conf

# Replace "#!/usr/bin/env python" with "#!/usr/bin/python"
Patch0: nepomuk-core-4.10-simpleresourec-rcgen-shebang-fix.patch

## upstream patches
#define git_patches 1
%if 0%{?git_patches}
BuildRequires: git-core
%endif

BuildRequires: doxygen
BuildRequires: kdelibs4-devel >= %{version}
BuildRequires: pkgconfig
BuildRequires: pkgconfig(soprano) >= %{soprano_ver}
BuildRequires: pkgconfig(libstreamanalyzer) pkgconfig(libstreams)
BuildRequires: pkgconfig(shared-desktop-ontologies)
# fileindexer plugins
BuildRequires: pkgconfig(exiv2) >= 0.20
BuildRequires: pkgconfig(poppler-qt4)
BuildRequires: pkgconfig(taglib)
%if  0%{?tests}
BuildRequires: dbus-x11
BuildRequires: virtuoso-opensource
%endif

Requires: %{name}-libs%{?_isa} = %{version}-%{release}
Requires: kdelibs4%{?_isa} >= %{version}
Requires: shared-desktop-ontologies >= %{shared_desktop_ontologies_version}
Provides: soprano-backend-virtuoso >= %{soprano_version}
Requires: virtuoso-opensource

# moved from kde-runtime in 4.8.80 (nepomuk common has nepomuk-core preference)
Conflicts: kde-runtime < 4.8.80-2

%description
%{summary}.

%package devel
Summary:  Developer files for %{name}
Requires: %{name}-libs%{?_isa} = %{version}-%{release}
Requires: kdelibs4-devel
%description devel
%{summary}.

%package libs
Summary:  Runtime libraries for %{name}
Requires: kdelibs4%{?_isa} >= %{version}
Requires: %{name} = %{version}-%{release}
%description libs
%{summary}.


%prep
%setup -q

%if 0%{?git_patches}
git init
if [ -z "$GIT_COMMITTER_NAME" ]; then
git config user.email "kde@lists.fedoraproject.org"
git config user.name "Fedora KDE SIG"
fi
git add .
git commit -a -q -m "%{version} baseline."

# Apply all the patches
git am -p1 %{patches} < /dev/null
%endif

%patch0 -p1 -b .rcgenshebang


%build
mkdir -p %{_target_platform}
pushd %{_target_platform}
%{cmake_kde4} ..
popd

make %{?_smp_mflags} -C %{_target_platform}


%install

make install/fast DESTDIR=%{buildroot} -C %{_target_platform}

%if 0%{?sysctl}
install -p -m644 -D %{SOURCE1} %{buildroot}%{_prefix}/lib/sysctl.d/nepomuk-inotify.conf
%else
install -p -m644    %{SOURCE1} ./nepomuk-inotify.conf
%endif

# fix multilib
sed -i -e 's!QUERYINTERFACE_H_[0-9]*!QUERYINTERFACE_H!g' %{buildroot}%{_kde4_includedir}/nepomuk2/queryinterface.h
sed -i -e 's!QUERYSERVICEINTERFACE_H_[0-9]*!QUERYSERVICEINTERFACE_H!g' %{buildroot}%{_kde4_includedir}/nepomuk2/queryserviceinterface.h

%check
desktop-file-validate %{buildroot}%{_kde4_datadir}/applications/kde4/nepomukbackup.desktop
%if 0%{?tests}
make -C %{_target_platform}/autotests/test test  ||:
%endif


%files
%doc ontologies/README COPYING.LGPL*
%if 0%{?sysctl}
%{_prefix}/lib/sysctl.d/nepomuk-inotify.conf
%else
%doc nepomuk-inotify.conf 
%endif
%{_kde4_appsdir}/fileindexerservice/
%{_kde4_appsdir}/nepomukfilewatch/
%{_kde4_appsdir}/nepomukstorage/
%{_kde4_bindir}/nepomuk-simpleresource-rcgen
%{_kde4_bindir}/nepomukbackup
%{_kde4_bindir}/nepomukcleaner
%{_kde4_bindir}/nepomukindexer
%{_kde4_bindir}/nepomukserver
%{_kde4_bindir}/nepomukservicestub
%{_kde4_bindir}/nepomuk2-rcgen
%{_kde4_libdir}/libkdeinit4_nepomukserver.so
%{_kde4_datadir}/applications/kde4/nepomukbackup.desktop
%{_kde4_datadir}/applications/kde4/nepomukcleaner.desktop
%{_kde4_datadir}/autostart/nepomukserver.desktop
%{_kde4_datadir}/kde4/services/*.desktop
%{_kde4_datadir}/kde4/servicetypes/nepomukservice.desktop
%{_kde4_datadir}/kde4/servicetypes/nepomukextractor.desktop
%{_kde4_datadir}/ontology/kde/
%{_datadir}/dbus-1/interfaces/*.xml
%{_kde4_libdir}/kde4/nepomukfileindexer.so
%{_kde4_libdir}/kde4/nepomukfilewatch.so
%{_kde4_libdir}/kde4/nepomukstorage.so
# metadata extractor plugins
# some of these (poppler, taglib) are good candidates to move to subpkg(s) -- rex
%{_kde4_libdir}/kde4/nepomuk*extractor.so

%files devel
%{_kde4_libdir}/libnepomukcore.so
%{_kde4_libdir}/cmake/NepomukCore/
%{_kde4_includedir}/nepomuk2/
%{_kde4_includedir}/Nepomuk2/

%post libs -p /sbin/ldconfig
%postun libs -p /sbin/ldconfig

%files libs
%{_kde4_libdir}/libnepomukcommon.so
%{_kde4_libdir}/libnepomukcore.so.4*
%{_kde4_libdir}/libnepomukextractor.so


%changelog
* Wed Sep 06 2017 Jan Grulich <jgrulich@redhat.com> - 4.10.5-6
- Rebuild exiv2
  Resolves: bz#1488011

* Tue Mar 18 2014 Than Ngo <than@redhat.com> - 4.10.5-5
- fix multilib issue

* Fri Jan 24 2014 Daniel Mach <dmach@redhat.com> - 4.10.5-4
- Mass rebuild 2014-01-24

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 4.10.5-3
- Mass rebuild 2013-12-27

* Wed Jul 24 2013 Daniel Vrátil <dvratil@redhat.com> - 4.10.5-2
- Resolves: bz#987030 - shebang with /usr/bin/env

* Sun Jun 30 2013 Than Ngo <than@redhat.com> - 4.10.5-1
- 4.10.5

* Sat Jun 01 2013 Rex Dieter <rdieter@fedoraproject.org> - 4.10.4-1
- 4.10.4

* Mon May 06 2013 Than Ngo <than@redhat.com> - 4.10.3-1
- 4.10.3

* Sun Mar 31 2013 Rex Dieter <rdieter@fedoraproject.org> 4.10.2-2
- tarball respin

* Sun Mar 31 2013 Rex Dieter <rdieter@fedoraproject.org> - 4.10.2-1
- 4.10.2

* Thu Mar 21 2013 Rex Dieter <rdieter@fedoraproject.org> 4.10.1-2
- bump minimal exiv2 dep

* Sat Mar 02 2013 Rex Dieter <rdieter@fedoraproject.org> 4.10.1-1
- 4.10.1

* Fri Feb 08 2013 Rex Dieter <rdieter@fedoraproject.org> 4.10.0-2
- pull in a few upstream patches

* Thu Jan 31 2013 Rex Dieter <rdieter@fedoraproject.org> - 4.10.0-1
- 4.10.0

* Sat Jan 19 2013 Rex Dieter <rdieter@fedoraproject.org> - 4.9.98-1
- 4.9.98

* Fri Jan 04 2013 Rex Dieter <rdieter@fedoraproject.org> - 4.9.97-1
- 4.9.97

* Wed Dec 19 2012 Rex Dieter <rdieter@fedoraproject.org> - 4.9.95-1
- 4.9.95

* Fri Dec 07 2012 Rex Dieter <rdieter@fedoraproject.org> 4.9.90-2
- s|/etc/sysctl.d|/usr/lib/sysctl.d|

* Mon Dec 03 2012 Rex Dieter <rdieter@fedoraproject.org> 4.9.90-1
- 4.9.90 (4.10beta2)

* Mon Dec 03 2012 Than Ngo <than@redhat.com> - 4.9.4-1
- 4.9.4

* Fri Nov 02 2012 Rex Dieter <rdieter@fedoraproject.org> - 4.9.3-1
- 4.9.3

* Wed Oct 03 2012 Rex Dieter <rdieter@fedoraproject.org> 4.9.2-5
- respin isEmpty_crash based on 32b44881 upstream commit (#858271)

* Tue Oct 02 2012 Rex Dieter <rdieter@fedoraproject.org> 4.9.2-4
- respin isEmpty_crash patch to guard against NULL (#858271)

* Tue Oct 02 2012 Rex Dieter <rdieter@fedoraproject.org> 4.9.2-3
- sysctl.d/nepomuk-inotify.conf: fs.inotify.max_user_watches=524288 (f18+)

* Mon Oct 01 2012 Rex Dieter <rdieter@fedoraproject.org> 4.9.2-2
- proposed patch to fix/workaround isEmpty crash (#858271)

* Fri Sep 28 2012 Rex Dieter <rdieter@fedoraproject.org> - 4.9.2-1
- 4.9.2

* Mon Sep 03 2012 Than Ngo <than@redhat.com> - 4.9.1-1
- 4.9.1

* Fri Aug 10 2012 Rex Dieter <rdieter@fedoraproject.org> 
- 4.9.0-3.20120810git
- sync 4.9-branch patches
- %%check: do autotests
- Requires: +soprano-backend-virtuoso +virtuoso-opensource

* Thu Aug 02 2012 Rex Dieter <rdieter@fedoraproject.org> 4.9.0-2
- respin

* Thu Jul 26 2012 Lukas Tinkl <ltinkl@redhat.com> - 4.9.0-1
- 4.9.0

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.8.97-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Wed Jul 11 2012 Rex Dieter <rdieter@fedoraproject.org> - 4.8.97-1
- 4.8.97

* Wed Jun 27 2012 Jaroslav Reznik <jreznik@redhat.com> - 4.8.95-1
- 4.8.95

* Tue Jun 12 2012 Rex Dieter <rdieter@fedoraproject.org> 
- 4.8.90-2
- move libkdeinit_* to base pkg (no need for multilib) 
- .spec cleanup
- add shared-desktop-ontologies, soprano runtime deps

* Sat Jun 09 2012 Rex Dieter <rdieter@fedoraproject.org> - 4.8.90-1
- 4.8.90

* Fri Jun 01 2012 Kevin Kofler <Kevin@tigcc.ticalc.org> 4.8.80-4
- BR kdelibs4-devel instead of kdelibs-devel, fixes minimum version (no Epoch)

* Fri Jun 01 2012 Jaroslav Reznik <jreznik@redhat.com> 4.8.80-3
- respin

* Wed May 30 2012 Jaroslav Reznik <jreznik@redhat.com> 4.8.80-2
- split -libs
- fix license

* Sat May 26 2012 Jaroslav Reznik <jreznik@redhat.com> 4.8.80-1
- initial try
