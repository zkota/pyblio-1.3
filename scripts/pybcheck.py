# -*- python -*-
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

import os, sys, string
from Pyblio import Config, Exceptions

# check the arguments
if len (sys.argv) < 3:
    print "usage: pybcheck <file | directory>..."
    sys.exit (1)

# list containing the broken entries
broken = []

# set the strictness for bibtex files
Config.set ("bibtex/strict", 1)

# we go over all the specified files
for dir in sys.argv [2:]:

    # eventually expand directories to their content
    if os.path.isdir (dir):
        files = map (lambda x, dir = dir: \
                     os.path.join (dir, x), os.listdir (dir))

        # in the case of a directory, use only .bib extension...
        files = filter (lambda f: os.path.splitext (f) [1] == '.bib',
                        files)
    else:
        files = [dir]


    # loop over the files
    for f in files:
        # try to open the database
        try:
            b = bibopen (f)
            print "file `%s' is ok [%d entries]" % (f, len (b))
        except (Exceptions.ParserError, KeyError), err:
            broken.append (str (err))

# write the error messages (expected to be well formated)
if len (broken) > 0:
    print string.join (broken, "\n")
    sys.exit (1)
