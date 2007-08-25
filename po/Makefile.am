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

LANGUAGES = 		\
	ar		\
	az 		\
	ca		\
	cs 		\
	da 		\
	de 		\
	dz		\
	el		\
	en_CA		\
	en_GB		\
	es		\
	fi 		\
	fr 		\
	hr		\
	hu 		\
	it 		\
	ja 		\
	nb		\
	ne		\
	nl		\
	oc		\
	pa		\
	pt_BR 		\
	pt		\
	ru 		\
	rw		\
	sk 		\
	sr@Latn 	\
	sr 		\
	sv 		\
	tr 		\
	uk		\
	vi		\
	zh_CN


EXTRA_DIST = $(LANGUAGES:%=%.po)

MO = $(LANGUAGES:%=%.mo)

localedir = $(datadir)/locale

all: $(MO)

%.mo: %.po
	msgfmt $< -o $@

install-data-hook: all
	for f in $(LANGUAGES) ; \
	  do $(mkinstalldirs) $(DESTDIR)$(localedir)/$${f}/LC_MESSAGES ; \
	  $(INSTALL_DATA) $${f}.mo \
	  $(DESTDIR)$(localedir)/$${f}/LC_MESSAGES/$(PACKAGE).mo ; \
	done

check:
	@rm -f ,,intl-1.tmp
	@for l in $(LANGUAGES) ; do \
	  echo $${l}.po >> ,,intl-1.tmp ; \
	done
	@cat ,,intl-1.tmp | sort > ,,intl-1 && rm -f ,,intl-1.tmp
	@find $(srcdir) -name '*.po' -exec basename {} \; | sort > ,,intl-2
	diff ,,intl-1 ,,intl-2
	@rm -f ,,intl-1 ,,intl-2
	for f in $(LANGUAGES) ; do \
	  echo "$$f: "`msgfmt --statistics $$f.po 2>&1` ; \
	done
