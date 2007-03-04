# This file is part of Pybliographer
# -*- coding: latin-1 -*-

# Copyright (C) 2004 Peter Schulte-Stracke
# Email : mail@schulte-stracke.de
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



def author_editor_format (item):
    """Return the author or editor of an item, for use
    in list displays."""
    s = []
    r = item.get ('author') or  item.get ('editor', [])


    try:  len(r)
    except TypeError:
        print 'USERFORMAT INPUT:', `r`, str(r) 
        return str(r)
    
    if len (r) == 1:
        a = r[0]
        s.append ("%s, %s" %( 
            a.last, a.initials()))
    
    elif len (r) > 3:       
        a = r[0]
        s.append ("%s, %s et al." %(
            a.last, a.initials()))
    
    elif len (r) > 1:
        for a in r:
            s.append (a.last)
        return '/'.join (s)

    return "".join (s)


def author_title_format (item):
    """Return author/title string for use in list displays."""

    r = author_editor_format (item)
    if r:
        s = [r, ': ']
    else:
        s = []
        
    r = item.get ('title') or item.get ('booktitle', '[no title]')
    s.append (r)

    return ''.join (s)

### Local Variables:
### Mode: python
### py-master-file : "ut_userformat.py"
### End:

