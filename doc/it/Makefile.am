# This file is part of pybliographer
# 
# Copyright (C) 1998-2003 Frederic GOBRY
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

SGML = 	config.sgml database.sgml entry.sgml gui.sgml iterator.sgml key.sgml \
	pyblio.sgml script.sgml selection.sgml styles.sgml url.sgml
PNG  = edit.png main.png open.png search.png sort.png

EXTRA_DIST = \
	topic.dat $(SGML) $(PNG)

pybliographic_helpdir = $(datadir)/gnome/help/pybliographic/it

all: pyblio/book1.html

pyblio/book1.html: $(SGML)
	db2html pyblio.sgml || echo "** can't regenerate documentation"

install-data-local:
	$(mkinstalldirs) $(DESTDIR)$(pybliographic_helpdir)
	$(INSTALL_DATA)  $(srcdir)/topic.dat $(DESTDIR)$(pybliographic_helpdir)
	@echo "installing HTML files"
	@if test -d pyblio ; then cp -rf $(srcdir)/pyblio/* $(DESTDIR)$(pybliographic_helpdir) ; fi
	@echo "installing PNG files"
	@for file in $(srcdir)/*.png ; do \
		$(INSTALL_DATA) $$file $(DESTDIR)$(pybliographic_helpdir) ; \
	done

dist-hook:
	if test -d pyblio ; then cp -rf $(srcdir)/pyblio $(distdir) ; fi

doc-pack:
	mkdir documentation
	cp pyblio/*.html *.png documentation
	tar zcvf doc-pack.tar.gz documentation
	rm -rf documentation