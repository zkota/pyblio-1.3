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

pybdir = $(datadir)/$(PACKAGE)$(EXTENSION)/Legacy

EXTRA_DIST = \
	version.py.in	\
	$(PYTHON)

PYTHON = \
	Autoload.py 	\
	Base.py 	\
	Config.py 	\
	Connector.py 	\
	Exceptions.py 	\
	Fields.py 	\
	Formatter.py 	\
	Help.py 	\
	Iterator.py 	\
	Key.py 		\
	LyX.py 		\
	Open.py 	\
	Resource.py	\
	Search.py 	\
	Selection.py 	\
	Sort.py 	\
	TextUI.py 	\
	Types.py 	\
	Utils.py 	\
	__init__.py 	\
	Query.py	\
	pybtextvar.py	\
	recode.py       \
	userexit.py	\
	userformat.py

SUBDIRS = GnomeUI Output Format ConfDir Style

pyb_DATA = $(PYTHON) version.py

version.py: $(srcdir)/version.py.in ../etc/installer
	$(SHELL) ../etc/installer < $(srcdir)/version.py.in > version.py
	@if test $(srcdir) != '.' ; then cp -f version.py $(srcdir) ; fi
