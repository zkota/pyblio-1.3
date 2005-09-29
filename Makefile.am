# This file is part of pybliographer
# 
# Copyright (C) 1998-2004 Frederic GOBRY
# Email : gobry@pybliographer.org
# 	   
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2 
# of the License, or (at your option) any later version.
#   
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details. 
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
# 
# 

pybdir  = $(datadir)/$(PACKAGE)
appdir  = $(datadir)/applications

SUBDIRS = 	Pyblio 		\
		glade		\
		.		\
		scripts		\
		tests		\
		Styles		\
		po		\
		doc


appicondir = $(datadir)/pixmaps
appicon_DATA = pybliographic.png 

pixmapsdir = $(datadir)/pixmaps
pixmaps_DATA = pybliographic-logo.png


Mimedir = $(datadir)/mime-info
Mime_DATA = pybliographic.keys pybliographic.mime

app_DATA = pybliographic.desktop

bin_SCRIPTS = pybliographer

EXTRA_DIST = 	setup-check.py			\
		COPYING-DOCS			\
		ChangeLog-1.2			\
		ChangeLog-1.0			\
		xmldocs.make			\
		omf.make			\
		pybrc.py 			\
	 	pybliographer.py 		\
		etc/installer.in		\
		pybliographic.keys.in		\
		pybliographic.mime		\
		pybliographic.desktop.in	\
		pybliographic.png		\
		pybliographic-logo.png


dist-hook:
	intltool-merge -d po pybliographic.desktop.in $(distdir)/pybliographic.desktop

pybliographic.desktop: pybliographic.desktop.in po/*.po
	intltool-merge -d po pybliographic.desktop.in pybliographic.desktop \
		|| echo "**** Warning: cannot update desktop file"

pybliographer: $(top_srcdir)/pybliographer.py etc/installer
	$(SHELL) etc/installer < $(top_srcdir)/pybliographer.py > pybliographer
	chmod 755 pybliographer

install-data-local:
	mv -f $(DESTDIR)$(pybdir)/pybrc.py $(DESTDIR)$(pybdir)/pybrc.old || true
	$(INSTALL_DATA) $(srcdir)/pybrc.py $(DESTDIR)$(pybdir)
	$(Python) -c "import compileall ; compileall.compile_dir ('"$(DESTDIR)$(pybdir)"');"

pybliographic.keys: pybliographic.keys.in Makefile
	sed -e 's^\@icondir\@^$(appicondir)^g' \
	< $(srcdir)/pybliographic.keys.in > pybliographic.keys.tmp \
	&& mv pybliographic.keys.tmp pybliographic.keys

install-data-hook:
	update-desktop-database $(DESTDIR)$(appdir) \
		|| echo "**** Warning: cannot update mime cache (recommended for Gnome >= 2.8)"

uninstall-hook:
	update-desktop-database $(appdir) \
		|| echo "**** Warning: cannot update mime cache (recommended for Gnome >= 2.8)"
