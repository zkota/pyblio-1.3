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


update-potfiles:
	echo $(top_srcdir)/pybliographer.in > ,,POTFILES
	find $(top_srcdir)/Pyblio  -name '*.py'    >> ,,POTFILES
	find $(top_srcdir)/scripts -name '*.py'    >> ,,POTFILES
	find $(top_srcdir)/glade   -name '*.glade' >> ,,POTFILES
	sed -e 's/^$(top_srcdir)\///' ,,POTFILES | sort > $(srcdir)/POTFILES.in
	rm -f ,,POTFILES

check:
	for f in $(LANGUAGES) ; do \
	  echo "$$f: "`msgfmt --statistics $$f.po 2>&1` ; \
	done
