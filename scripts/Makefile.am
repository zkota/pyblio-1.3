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
# 

pybdir  = $(datadir)/$(PACKAGE)

bin_SCRIPTS = 	pybliographic	\
		pybcheck	\
		pybconvert	\
		pybcompact	\
		pybtex		\
		pybformat

pyb_SCRIPTS = 	pybliographic.py	\
		pybcheck.py 		\
		pybconvert.py 		\
		pybcompact.py 		\
		pybtex.py		\
		pybformat.py		

noinst_SCRIPTS = pybscript

EXTRA_DIST = 	pybscript.in			\
	 	pybliographic.py 		\
		pybcheck.py			\
		pybconvert.py			\
		pybtex.py			\
		pybformat.py			\
		pybcompact.py

#pybliographic pybcheck pybconvert pybcompact pybtex pybformat:
$(bin_SCRIPTS):
	$(LN_S) pybscript $@

pybscript: $(srcdir)/pybscript.in ../etc/installer
	$(SHELL) ../etc/installer < $(srcdir)/pybscript.in > pybscript
	chmod 755 pybscript
