%define pyb_prefix   /usr

Summary: A framework for working with bibliographic databases.
Name: pybliographer
Version: 1.0.3
Release: 4
Copyright: GPL
Group: Applications/Productivity
Source: pybliographer-1.0.3.tar.gz
Patch: pybliographer.patch
Requires: python, pygnome >= 1.0.53
Packager: Konrad Hinsen <hinsen@cnrs-orleans.fr>
BuildRoot: /var/tmp/pybliographer-root

%description
Pybliographer is a tool for managing bibliographic databases. It currently supports the following formats: 

- BibTeX (quite complete) 
- Medline (read-only) 
- Ovid files (from ovid.com) 
- Refer and EndNote (read only)
- SGML DocBook (write only) 

Pybliographer can be used for searching, editing, reformatting, etc.
In fact, it's a simple framework that provides easy to use python
classes and functions, and therefore can be extended to any usage
(generating HTML pages according to bibliographic searches, etc).

In addition to the scripting environment, a graphical GNOME interface
is available. It provides powerful editing capabilities, in addition
to a nice hierarchical search mechanism.

%prep
%setup -n pybliographer-1.0.3
CFLAGS="$RPM_OPT_FLAGS" ./configure --prefix=%{pyb_prefix}
%patch

%build
make

%install
rm -rf $RPM_BUILD_ROOT
make DESTDIR=$RPM_BUILD_ROOT install

%files
%{pyb_prefix}/bin/pybcheck    
%{pyb_prefix}/bin/pybconvert	
%{pyb_prefix}/bin/pybliographer  
%{pyb_prefix}/bin/pybtex
%{pyb_prefix}/bin/pybcompact  
%{pyb_prefix}/bin/pybformat	
%{pyb_prefix}/bin/pybliographic
%{pyb_prefix}/include/bibtex.h
%{pyb_prefix}/lib/libbibtex.a  
%{pyb_prefix}/lib/libbibtex.la  
%{pyb_prefix}/lib/libbibtex.so  
%{pyb_prefix}/lib/libbibtex.so.1  
%{pyb_prefix}/lib/libbibtex.so.1.0.0
%{pyb_prefix}/lib/pybliographer
%{pyb_prefix}/share/pybliographer
%{pyb_prefix}/share/gnome/apps/Applications/pybliographic.desktop 
%{pyb_prefix}/share/gnome/help/pybliographic
%{pyb_prefix}/share/mime-info/pybliographic.keys
%{pyb_prefix}/share/mime-info/pybliographic.mime
%{pyb_prefix}/share/pixmaps/pybliographic-logo.png
%{pyb_prefix}/share/pixmaps/pybliographic.png
%{pyb_prefix}/share/locale/fr/LC_MESSAGES/pybliographer.mo
%{pyb_prefix}/share/locale/it/LC_MESSAGES/pybliographer.mo
%{pyb_prefix}/share/locale/de/LC_MESSAGES/pybliographer.mo
%{pyb_prefix}/share/locale/hu/LC_MESSAGES/pybliographer.mo
