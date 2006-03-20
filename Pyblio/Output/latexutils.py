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

import string, os, re, copy
from Pyblio import Base, Key, Open

# regular expression to match in the .aux file
citation_re = re.compile ('^\\\\citation\\{([^\\}]+)\\}')
include_re  = re.compile ('^\\\\\@input\\{([^\\}]+)\\}')

style_re = re.compile ('^\\\\bibstyle\\{([^\\}]+)\\}')
data_re  = re.compile ('^\\\\bibdata\\{([^\\}]+)\\}')


def find_entries (auxfile, bibtex):
    """ Parse an auxiliary file and extract the entries from the given BibTeX databases """
    
    entries, data, style = list_entries (auxfile)

    if not bibtex:
        bibtex = data

    # we have to create a Reference database to hold the entries contained in the
    # current database.
    r    = Base.DataBase (None)
    keys = copy.copy (entries)
    
    # is there something to do ?
    if len (entries) == 0: return r, style, entries
	
    # use the bibliographic databases in order of declaration
    # to solve the references
	
    for bib in bibtex:
        (root, ext) = os.path.splitext (bib)
        if not ext: ext = '.bib'
        
        # open the database
        db = Open.bibopen (root + ext)

        # as we are modifying the list of entries in this loop, we make a copy
        # of it in order to avoir strange behaviors
        orig = copy.copy (entries)
	
        # loop over the expected entries
        for e in orig:
	
            # create a key in the current database
            key = Key.Key (db, e)
            
            # does the database provide the key ?
            if db.has_key (key):
	            
                # yes, add it to the reference
                r [Key.Key (None, e)] = db [key]
                
                # and remove it from the list
                entries.remove (e)
	
        # is it finished ?
        if len (entries) == 0: break

    # return the reference on all the entries, plus the missing ones
    keys = filter (lambda x, entries = entries: not entries.count (x), keys)
    keys = map (lambda x, r = r: Key.Key (r, x), keys)

    return r, keys, style, entries


def list_entries (file):
    """ This function extracts the citation keys from the .aux files """
    
    def r_list_entries (file, get_data = 0):
	    
        auxfile = os.path.splitext (file) [0] + '.aux'

        if get_data:
            data  = None
            style = None
            
        aux = open (auxfile, 'r')
        citations = []
	
        # parse the whole file
        while 1:
            line = aux.readline ()
            if line == '': break
	
            line = string.strip (line)
            
            # we match a new citation
            match = citation_re.search (line)
            if match:
                citations += [ref.strip() for ref in match.split(',')]
                continue
	
            # we have to enter an additional .aux file
            match = include_re.search (line)
            if match:
                citations = citations + r_list_entries (match.group (1))
                continue

            if get_data:
                match = data_re.search (line)
                if match:
                    data = match.group (1)
                    data = string.split (data, ",")
                    data = map (string.strip, data)
                    continue
                
                match = style_re.search (line)
                if match:
                    style = match.group (1)
                    continue

        aux.close ()
        
        if get_data:
            return citations, data, style
        
        return citations

    # create the list of entries
    entries, data, style = r_list_entries (file, 1)

    # ensure citation keys unicity
    h = {}
    def filter_function (k, h = h):
        if h.has_key (k): return 0

        h [k] = 1
        return 1

    entries = filter (filter_function, entries)
	
    return entries, data, style
