%define name pybliographer
%define version 1.2.2
%define release 1.rhfdr_core_1

Summary: A framework for working with bibliographic databases.
Name: %{name}
Version: %{version}
Release: %{release}
License: GPL
Group: Applications/Productivity
Source: http://prdownloads.sourceforge.net/pybliographer-1.2.2.tar.gz
Url: http://pybliographer.org/
BuildRoot: %{_tmppath}/%{name}-%{version}-buildroot
BuildArch: noarch

PreReq: scrollkeeper >= 0.1.4

Buildrequires: gnome-python2
Buildrequires: gnome-python2-gconf
Buildrequires: python-bibtex
Buildrequires: pygtk2-libglade

Requires: python
Requires: python-bibtex >= 1.1.93.1
Requires: recode
Requires: gnome-python2
Requires: gnome-python2-gconf
Requires: pygtk2
Requires: pygtk2-libglade


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

/bin/rm -rf $RPM_BUILD_ROOT/var/scrollkeeper


%{find_lang} %{name}

%clean
rm -rf $RPM_BUILD_ROOT

%post
scrollkeeper-update

%postun
scrollkeeper-update


%files -f %{name}.lang
%defattr(-,root,root)
%doc AUTHORS COPYING* ChangeLog* INSTALL NEWS README TODO
%{_bindir}/*
%{_datadir}/gnome/apps/Applications/pybliographic.desktop
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
%config %{_datadir}/pybliographer/pybrc.py
%config %{_datadir}/pybliographer/pybrc.pyc
