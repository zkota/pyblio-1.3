# -*- python -*-
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
# $Id: pybconvert.py,v 1.2.2.3 2003/08/06 09:09:57 fredgo Exp $

import os, sys, string, gettext

_ = gettext.gettext

if len (sys.argv) < 4 or len (sys.argv) > 5:
    print _("usage: pybconvert <source>..<target> <input> [output]")
    sys.exit (1)


format = sys.argv [2]

try:
    source, target = string.split (format, '..')
except:
    print _("pybconvert: bad conversion format")
    sys.exit (1)


from Pyblio import Open

f_in = sys.argv [3]

if len (sys.argv) == 4:
    f_out = sys.stdout
else:
    f_out = open (sys.argv [4], 'w')

database = Open.bibopen (f_in, source)
Open.bibwrite (database.iterator (), how = target, out = f_out)
    
