Summary: A framework for working with bibliographic databases.
Name: pybliographer
Version: 1.2.4
Release: 1.rhfdr_core_1
License: GPL
Group: Applications/Publishing
Source: http://dl.sf.net/pybliographer/pybliographer-1.2.4.tar.gz
Url: http://www.pybliographer.org/
Packager: Zoltan Kota <z.kota at gmx.net>
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildArch: noarch

PreReq: scrollkeeper >= 0.1.4

BuildRequires: python >= 2.2
BuildRequires: pygtk2 >= 2.0.0
BuildRequires: pygtk2-libglade >= 2.0.0
BuildRequires: gnome-python2 >= 2.0.0
BuildRequires: gnome-python2-gconf >= 2.0.0
BuildRequires: python-bibtex >= 1.1.93.1
BuildRequires: gettext
BuildRequires: scrollkeeper >= 0.1.4
BuildRequires: intltool

Requires: python >= 2.2
Requires: pygtk2 >= 2.0.0
Requires: pygtk2-libglade >= 2.0.0
Requires: gnome-python2 >= 2.0.0
Requires: gnome-python2-gconf >= 2.0.0
Requires: python-bibtex >= 1.1.93.1
Requires: recode >= 3.6-11


%description
Pybliographer is a tool for managing bibliographic databases. It can be 
used for searching, editing, reformatting, etc. In fact, it's a simple 
framework that provides easy to use python classes and functions, and 
therefore can be extended to many uses (generating HTML pages according
to bibliographic searches, etc).
In addition to the scripting environment, a graphical Gnome interface 
is available. It provides powerful editing capabilities, a nice 
hierarchical search mechanism, direct insertion of references into LyX, 
direct queries on Medline, and more. It currently supports the following 
file formats: BibTeX, ISI, Medline, Ovid, Refer.


%prep
%setup -q

%build
%configure
make

%install
rm -rf $RPM_BUILD_ROOT
%makeinstall

%__rm -rf $RPM_BUILD_ROOT%{_localstatedir}/scrollkeeper


%{find_lang} %{name}

%clean
rm -rf $RPM_BUILD_ROOT

%post
scrollkeeper-update

%postun
scrollkeeper-update


%files -f %{name}.lang
%defattr(-,root,root)
%doc AUTHORS COPYING* ChangeLog* NEWS README TODO
%{_bindir}/*
%{_datadir}/applications/pybliographic.desktop
%{_datadir}/gnome/help/pybliographer
%{_datadir}/mime-info/*
%{_datadir}/omf/pybliographer
%{_datadir}/pixmaps/*
%dir %{_datadir}/pybliographer
%{_datadir}/pybliographer/Pyblio
%{_datadir}/pybliographer/Styles
%{_datadir}/pybliographer/glade
%{_datadir}/pybliographer/pybcheck.py
%{_datadir}/pybliographer/pybcompact.py
%{_datadir}/pybliographer/pybconvert.py
%{_datadir}/pybliographer/pybformat.py
%{_datadir}/pybliographer/pybliographic.py
%{_datadir}/pybliographer/pybtex.py
%{_datadir}/pybliographer/pybtext.py
%config %{_datadir}/pybliographer/pybrc.py
%ghost %{_datadir}/pybliographer/pybrc.pyc

%changelog
* Fri Jul 23 2004 Zoltan Kota <z.kota at gmx.net> - 1.2.4-1.rhfdr_core_1
- new version
- using macros for rm and localstatedir
- add intltool in buildrequires

* Mon Mar 22 2004 Zoltan Kota <z.kota at gmx.net> - 1.2.3-1.rhfdr_core_1
- new version
- remove desktop file fix and perl from buildrequires
- changing pybrc.pyc to ghost in file list

* Wed Feb 18 2004 Zoltan Kota <z.kota at gmx.net> 1.2.2-4.rhfdr_core_1
- fix requires and buildrequires
- change rpm group category
- some rpm cosmetics

* Tue Jan 20 2004 Zoltán Kóta <z.kota at gmx.net> 1.2.2-3.rhfdr_core_1
- fixing requires version numbers

* Mon Jan 12 2004 Zoltán Kóta <z.kota at gmx.net> 1.2.2-2.rhfdr_core_1
- fixing Categories in pybliographic.desktop

* Thu Jan 8 2004 Zoltán Kóta <z.kota at gmx.net> 1.2.2-1.rhfdr_core_1
- new version
- added omf file to the filelist
- added 'post' and 'pustun' (scrollkeeper-update)
- removed docbook-utils from BuildReq
- added scrollkeeper to PreReq
- using 'configure' and 'makeinstall' macros
- added rm -rf to 'install' section to remove temporary scrollkeeper files
- using macros in filelist

* Tue Jan 6 2004 Zoltán Kóta <z.kota at gmx.net> 1.2.1-2.rhfdr_core_1
- Fix buildrequires and requires

* Wed Nov 21 2003 Zoltán Kóta <z.kota at gmx.net>
- initial RPM package for Redhat Fedora Core 1
