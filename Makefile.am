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

pybdir  = $(datadir)/$(PACKAGE)$(EXTENSION)
appdir  = $(datadir)/applications

SUBDIRS = 	Legacy 		\
		.		\
		scripts		\
		tests		\
		Styles		\
		po		\
		doc

binary = pybliographer$(EXTENSION)

appicondir = $(datadir)/pixmaps
appicon_DATA = pyblio.png 

pixmapsdir = $(datadir)/pixmaps
pixmaps_DATA = pyblio-logo.png pyblio-viewer.png


Mimedir = $(datadir)/mime-info
Mime_DATA = pyblio.keys pyblio.mime

app_DATA = pyblio.desktop

bin_SCRIPTS = $(binary)

EXTRA_DIST = 	setup-check.py			\
		COPYING-DOCS			\
		xmldocs.make			\
		omf.make			\
		pybrc.py 			\
	 	pybliographer.py 		\
		etc/installer.in		\
		pyblio.keys.in			\
		pyblio.mime			\
		pyblio.desktop.in		\
		pyblio.png			\
		pyblio-logo.png			\
		pyblio-viewer.png		


dist-hook:
	intltool-merge -d po pyblio.desktop.in $(distdir)/pyblio.desktop

pyblio.desktop: pyblio.desktop.in po/*.po
	intltool-merge -d po pyblio.desktop.in pyblio.desktop \
		|| echo "**** Warning: cannot update desktop file"

$(binary): $(top_srcdir)/pybliographer.py etc/installer
	$(SHELL) etc/installer < $(top_srcdir)/pybliographer.py > $(binary)
	chmod 755 $(binary)

install-data-local:
	mv -f $(DESTDIR)$(pybdir)/pybrc.py $(DESTDIR)$(pybdir)/pybrc.old || true
	$(INSTALL_DATA) $(srcdir)/pybrc.py $(DESTDIR)$(pybdir)
	$(Python) -c "import compileall ; compileall.compile_dir ('"$(DESTDIR)$(pybdir)"');"

pyblio.keys: pyblio.keys.in Makefile
	sed -e 's^\@icondir\@^$(appicondir)^g' \
	< $(srcdir)/pyblio.keys.in > pyblio.keys.tmp \
	&& mv pyblio.keys.tmp pyblio.keys

install-data-hook:
	update-desktop-database $(DESTDIR)$(appdir) \
		|| echo "**** Warning: cannot update mime cache (recommended for Gnome >= 2.8)"

uninstall-hook:
	update-desktop-database $(appdir) \
		|| echo "**** Warning: cannot update mime cache (recommended for Gnome >= 2.8)"
