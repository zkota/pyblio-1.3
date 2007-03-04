# -*- python -*-
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

import string, sys, os

from Legacy.Output import latexutils

from Legacy import Base, Autoload, Fields
from Legacy.Style import Utils

import locale
charset = locale.getlocale () [1] or 'ascii'

def usage ():
    print _("usage: pybtex <latexfile> [bibtexfiles...]").encode (charset)
    return

def error (message):
    sys.stderr.write ((_("pybtex: error: %s\n") % message).encode (charset))
    sys.exit (1)
    return

# test input arguments
if len (sys.argv) < 3:
    # user gave wrong arguments...
    usage ()
    sys.exit (1)
    
latex  = sys.argv [2]
bibtex = sys.argv [3:]

# --------------------------------------------------
# Search the entries found in the LaTeX document
# --------------------------------------------------

db, keys, style, missing = latexutils.find_entries (latex, bibtex)

if missing:
    # warn the user that some entries were not found
    print _("pybtex: warning: the following keys were not resolved").encode (charset)
    print '	' + string.join (missing, '\n	') + '\n'

if style is None:
    # If the LaTeX document declares no style...
    error (_("no style defined"))

# --------------------------------------------------
# generate the latex bibliography
# --------------------------------------------------

# Create a formatter that writes in the .bbl file
formatter = Autoload.get_by_name ('output', 'LaTeX').data

# Search style in local path and standard installation
url = None

if os.path.exists (style + '.xml'):
    url = Fields.URL (style + '.xml')
else:

    from Legacy import version
    full = os.path.join (version.pybdir, 'Styles', style)
    full = full + '.xml'
    if os.path.exists (full): url = Fields.URL (full)

if not url:
    error (_("can't find style `%s'") % style)

# open the .bbl file
bblfile = os.path.splitext (os.path.split (latex) [1]) [0] + '.bbl'
bbl = open (bblfile, 'w')

Utils.generate (url, formatter, db, keys, bbl)

bbl.close ()
