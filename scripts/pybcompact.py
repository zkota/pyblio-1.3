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

import string, os, re, copy, gettext, sys
from Pyblio import Base, Key

_ = gettext.gettext

def usage ():
    print _("usage: pybcompact <latexfile> <bibtexfiles...>")
    return

def error (msg):
    sys.stderr.write (_("pybcompact: error: %s\n") % msg)
    sys.exit (1)
    return


# test input arguments
if len (sys.argv) < 4:
    usage ()
    sys.exit (1)


latex  = sys.argv [2]
bibtex = sys.argv [3:]

# regular expression to match in the .aux file
citation_re = re.compile ('\\citation\{([^\}]+)\}')
include_re  = re.compile ('^\\\@input\{([^\}]+)\}')

# this function extracts the citation keys from the .aux files
def list_entries (file):
    
    auxfile = os.path.splitext (file) [0] + '.aux'

    try:
        aux = open (auxfile, 'r')
    except IOError, err:
        error ('%s: %s' % (auxfile, err))
    
    citations = []

    # parse the whole file
    while 1:
        line = aux.readline ()
        if line == '': break

        line = string.strip (line)

        # we match a new citation
        match = citation_re.search (line)
        if match:
            citations.append (match.group (1))
            continue

        # we have to enter an additional .aux file
        match = include_re.search (line)
        if match:
            citations = citations + list_entries (match.group (1))
            continue

    aux.close ()
    return citations


entries = list_entries (latex)

# ensure citation keys unicity
h = {}
for e in entries:
    h [e] = 1
entries = h.keys ()

# is there something to do ?
if len (entries) == 0:
    error (_("no entry"))


# use the bibliographic databases in order of declaration
# to solve the references

for bib in bibtex:

    # open the database
    db = bibopen (bib)

    # as we are modifying the list of entries in this loop, we make a copy
    # of it in order to avoir strange behaviors
    orig = copy.copy (entries)

    # we have to create a new database to hold the entries contained in the
    # current database.
    
    r = Base.DataBase (None)
    
    # loop over the expected entries
    for e in orig:

        # create a key in the current database
        key = Key.Key (db, e)

        # does the database provide the key ?
        if db.has_key (key):
            
            # yes, add it to the reference
            r [key] = db [key]

            # and remove it from the list
            entries.remove (e)

    # if we found some entries in the current database...
    if len (r) > 0:
        bibwrite (r.iterator (), how = 'BibTeX')

    # is it finished ?
    if len (entries) == 0: break


# check if we were able to solve all the citations
if len (entries) > 0:
    error (_("can't find the following entries: %s")
           % string.join (entries, ", "))

