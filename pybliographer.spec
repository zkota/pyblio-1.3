Summary: A framework for working with bibliographic databases.
Name: pybliographer
Version: 1.2.5
Release: 1.rhfdr_core_1
License: GPL
Group: Applications/Publishing
Source: http://dl.sf.net/pybliographer/pybliographer-1.2.5.tar.gz
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

Requires: python >= 2.2
Requires: pygtk2 >= 2.0.0
Requires: pygtk2-libglade >= 2.0.0
Requires: gnome-python2 >= 2.0.0
Requires: gnome-python2-gconf >= 2.0.0
Requires: python-bibtex >= 1.1.93.1
Requires: recode >= 3.6-11
Requires: desktop-file-utils

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

# Compile .pyc and .pyo
%{__python} -c "import compileall; compileall.compile_dir('$RPM_BUILD_ROOT%{_datadir}/pybliographer', ddir='%{_datadir}/pybliographer', force=1)"
%{__python} -O -c "import compileall; compileall.compile_dir('$RPM_BUILD_ROOT%{_datadir}/pybliographer', ddir='%{_datadir}/pybliographer', force=1)"


%{find_lang} %{name}

%clean
rm -rf $RPM_BUILD_ROOT


%post
scrollkeeper-update

# run update-desktop-database if exists
if [ -x update-desktop-database ]; then
	update-desktop-database %{_datadir}/applications
fi


%postun
scrollkeeper-update

# run update-desktop-database if exists
if [ -x update-desktop-database ]; then
	update-desktop-database %{_datadir}/applications
fi


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
%{_datadir}/pybliographer/Pyblio/ConfDir/*.py
%{_datadir}/pybliographer/Pyblio/ConfDir/*.pyc
%ghost %{_datadir}/pybliographer/Pyblio/ConfDir/*.pyo
%{_datadir}/pybliographer/Pyblio/Format/*.py
%{_datadir}/pybliographer/Pyblio/Format/*.pyc
%ghost %{_datadir}/pybliographer/Pyblio/Format/*.pyo
%{_datadir}/pybliographer/Pyblio/GnomeUI/*.py
%{_datadir}/pybliographer/Pyblio/GnomeUI/*.pyc
%ghost %{_datadir}/pybliographer/Pyblio/GnomeUI/*.pyo
%{_datadir}/pybliographer/Pyblio/Output/*.py
%{_datadir}/pybliographer/Pyblio/Output/*.pyc
%ghost %{_datadir}/pybliographer/Pyblio/Output/*.pyo
%{_datadir}/pybliographer/Pyblio/Style/*.py
%{_datadir}/pybliographer/Pyblio/Style/*.pyc
%ghost %{_datadir}/pybliographer/Pyblio/Style/*.pyo
%{_datadir}/pybliographer/Pyblio/*.py
%{_datadir}/pybliographer/Pyblio/*.pyc
%ghost %{_datadir}/pybliographer/Pyblio/*.pyo
%{_datadir}/pybliographer/Styles
%{_datadir}/pybliographer/glade
%{_datadir}/pybliographer/pybcheck.py
%{_datadir}/pybliographer/pybcompact.py
%{_datadir}/pybliographer/pybconvert.py
%{_datadir}/pybliographer/pybformat.py
%{_datadir}/pybliographer/pybliographic.py
%{_datadir}/pybliographer/pybtex.py
%{_datadir}/pybliographer/pybtext.py
%ghost %{_datadir}/pybliographer/pybcheck.pyc
%ghost %{_datadir}/pybliographer/pybcompact.pyc
%ghost %{_datadir}/pybliographer/pybconvert.pyc
%ghost %{_datadir}/pybliographer/pybformat.pyc
%ghost %{_datadir}/pybliographer/pybliographic.pyc
%ghost %{_datadir}/pybliographer/pybtex.pyc
%ghost %{_datadir}/pybliographer/pybtext.pyc
%ghost %{_datadir}/pybliographer/pybcheck.pyo
%ghost %{_datadir}/pybliographer/pybcompact.pyo
%ghost %{_datadir}/pybliographer/pybconvert.pyo
%ghost %{_datadir}/pybliographer/pybformat.pyo
%ghost %{_datadir}/pybliographer/pybliographic.pyo
%ghost %{_datadir}/pybliographer/pybtex.pyo
%ghost %{_datadir}/pybliographer/pybtext.pyo
%config %{_datadir}/pybliographer/pybrc.py
%ghost %{_datadir}/pybliographer/pybrc.pyc
%ghost %{_datadir}/pybliographer/pybrc.pyo
