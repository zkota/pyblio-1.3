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
import re
from string import *

from Legacy import Key, Autoload, recode

_flat = recode.recode ('latin1..flat')

def compress_page_range (pages, separator='-'):
    """Returns a page range with common prefix
    elided from the second number. Resulte is string
    firstpage(separator)(lastpage), except if separator
    is None, then a sequence is returned."""

    p = re.sub (' *--? *', '-', pages)
    s = p.split('-')
    if len(s) > 1:
        l, r = s
        if len(l) == len(r):
            i = 0
            while r [i] == l[i]:
                i += 1
            r = r[i:]
    else:
        l, r = s[0], ''
    if separator:
        return "%s%s%s" %(l, separator, r)
    else:
        return l, r


def format (string, width, first, next):
    ''' Format a string on a given width '''

    out = []
    current = first

    # if the entry does not fit the current width
    while len (string) > width - current:
	    
        pos = width - current - 1

	# search a previous space
	while pos > 0 and string [pos] <> ' ':
	    pos = pos - 1

	# if there is no space before...
	if pos == 0:
	    pos = width - current
	    taille = len (string)
	    while pos < taille and string [pos] <> ' ':
	        pos = pos + 1

	out.append (' ' * current + string [0:pos])
	string = string [pos+1:]
	current = next

    out.append (' ' * current + string)

    return rstrip (join (out, '\n'))


__entry = 0


def generate_key (entry, table):

    if   entry.has_key ('author'): aut = entry ['author']
    elif entry.has_key ('editor'): aut = entry ['editor']
    else:                          aut = ()

    if len (aut) == 0:
        global __entry
        key = 'entry-%d' % __entry
        __entry = __entry + 1
    else:
        if len (aut) > 1:
            key = ''
            for a in aut:
                honorific, first, last, lineage = a.format ()
                key = key + join (map (lambda x:
                                       x [0], split (last, ' ')), '')
                if len (key) >= 3:
                    if len (aut) > 3:
                        key = key + '+'
                    break
        else:
            honorific, first, last, lineage = aut [0].format ()
            parts = split (last, ' ')
	            
            if len (parts) == 1:
                key = parts [0][0:3]
            else:
                key = join (map (lambda x: x [0], parts), '')
	
                
        if entry.has_key ('date'):
            year = entry ['date'].year
            
            if year: key = key + str (year) [2:]


    base = _flat (key)
    key  = Key.Key (table, base)
    
    if table.has_key (key):
	suff = ord ('a')
	
        while table.has_key (key):
            suff = suff + 1
            
            if suff > ord ('z'):
                suff = ord ('a')
                base = base + 'a'

            key  = Key.Key (table, base + chr (suff))
            
    return Key.Key (table, key)

Autoload.register ('key', 'Default', generate_key)


class StringStream:
    ''' This class simulates a stream and stores it into a simple
    string. '''

    def __init__ (self):
        self.text = ''
        return

    def write (self, text):
        self.text = self.text + text
        return

    
