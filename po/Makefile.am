# This file is part of pybliographer
# 
# Copyright (C) 1998-2003 Frederic GOBRY
# Email : gobry@idiap.ch
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
# $Id: Makefile.am,v 1.1.2.3 2003/10/10 08:56:28 fredgo Exp $

LANGUAGES = 					\
	az 					\
	da 					\
	de 					\
	fi 					\
	fr 					\
	hu 					\
	it 					\
	ja 					\
	no 					\
	pt_BR 					\
	ru 					\
	sk 					\
	sr@Latn 				\
	sr 					\
	sv 					\
	tr 					\
	uk

MO = $(LANGUAGES:%=%.mo)

localedir = $(datadir)/locale

all: $(MO)

%.mo: %.po
	msgfmt $< -o $@

install-data-hook:
	for f in $(LANGUAGES) ; \
	  do $(mkinstalldirs) $(DESTDIR)$(localedir)/$${f}/LC_MESSAGES ; \
	  $(install_sh_DATA) $${f}.mo \
	  $(DESTDIR)$(localedir)/$${f}/LC_MESSAGES/$(PACKAGE).mo ; \
	done

EXTRA_PY = 						\
	$(top_srcdir)/pybliographer.py			\
	$(top_srcdir)/scripts/pybcheck.py 		\
	$(top_srcdir)/scripts/pybcompact.py 		\
	$(top_srcdir)/scripts/pybconvert.py 		\
	$(top_srcdir)/scripts/pybformat.py 		\
	$(top_srcdir)/scripts/pybliographic.py 		\
	$(top_srcdir)/scripts/pybtex.py


update:
	find $(top_srcdir)/Pyblio -name '*.py' -print | \
		xargs pygettext -d py $(EXTRA_PY)
	$(MAKE) -C ../glade messages.pot
	msgcat py.pot ../glade/messages.pot -o $(PACKAGE).pot
	for f in $(LANGUAGES) ; do \
	  mv $$f.po $$f.old.po ; \
	  if msgmerge $$f.old.po $(PACKAGE).pot -o $$f.po ; then \
	    rm -f $$f.old.po ; else \
	    echo "msgmerge for $$f failed" ; \
	    rm -f $$f.po ; mv $$f.old.po $$f.po ; \
	  fi ; \
	done

check:
	for f in $(LANGUAGES) ; do \
	  echo "$$f: "`msgfmt --statistics $$f.po 2>&1` ; \
	done
