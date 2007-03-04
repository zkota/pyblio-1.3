# -*- coding: latin-1 -*-
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

from Legacy import Fields, Types

import re, string, time

class Sort:
    ''' This class defines the methods used to sort a database '''
    
    def __init__ (self, fields = None):
        ''' Create a Sort class with a given set of SortFields '''
       
        self.fields = fields or []
        return

    def sort (self, iterator):
        ''' Returns a list of keys sorted according to the current
        sort settings '''
	
        self.base = iterator.base

        S = []
        extractors = [f.get_extractor() for f in self.fields]
        for e in iterator:
            s = []
            for f in extractors:
                s.extend (f (e))
	    s.append (e)
            S.append (s)
        S.sort ()
        result = [x [-1] for x in S]
        return result

    def __repr__ (self):
        return 'Sort (%s)' % str (self.fields)

class AnySort (object):
    
    def __init__ (self, ascend = 1):
        self.ascend = ascend
        return

    def get_extractor (self, extractor=None):
        extractor = extractor or self.extractor
        if self.ascend < 0:
            return lambda e: map (
                lambda S: ''.join([unichr(~ord(c) & 65535) for c in S]),
                extractor (e))
        else :
            return extractor
    
class TypeSort (AnySort):

    def get_field (self, entry):
        return entry.type

    def __repr__ (self):
        return 'TypeSort (%d)' % self.ascend

    def __cmp__ (self, other):
        if isinstance (other, TypeSort): return 0
        return -1

    def extractor (self, entry):
        return [str(entry.type).lower()]

class KeySort (AnySort):

    def get_field (self, entry):
        return entry.key

    def __repr__ (self):
        return 'KeySort (%d)' % self.ascend

    def __cmp__ (self, other):
        if isinstance (other, KeySort): return 0
        return -1

    def extractor (self, entry):
        return [str(entry.key).lower()]

class FieldSort (AnySort):
    
    def __init__ (self, field, ascend = 1):
        self.field  = field
        AnySort.__init__ (self, ascend)

    def get_extractor (self):
        field = self.field
        if field ==  'date':
            if self.ascend < 0:
                return lambda x: [- self.date_extractor(x) [0]]
            else: return self.date_extractor
        elif field == '-author/editor-':
            return AnySort.get_extractor (
                self, self.author_editor_extractor)
        elif field in ['author', 'editor']:
            return AnySort.get_extractor (
                self,
                lambda entry: map (
                rakify, entry.get(field, [])))
        else:
            return AnySort.get_extractor(self)
        
    def get_field (self, entry):
        try:
            return entry [self.field]
        except KeyError:
            return Types.get_field (self.field).type ('')

    def __repr__ (self):
        return 'FieldSort (%s, %d)' % (`self.field`, self.ascend)

    def __cmp__ (self, other):
        if not hasattr (other, 'field'): return -1
        
        return cmp (string.lower (self.field),
                    string.lower (other.field))

    def extractor (self, entry):
	try:
	    return   [str(entry[self.field]).rstrip().lower()]
	except KeyError :
	    return []
	
    def author_editor_extractor (self, entry):
        return map (rakify, entry.get('author', entry.get('editor', [])))
 
    def date_extractor (self, entry):
        d = entry.get('date', 0)
        try:
            return [d.asInt()]
        except AttributeError:
            return [0]
        
def rakify (author):

    
    s = "%s,%s" %(author.last,author.first)
    s = s.lower()
    Z = []
    for c in s:
        if c in 'äöüÄÖÜ':
            n = 'äöüÄÖÜ'.index (c)
            Z.append ('%ce' % ('aouAOU' [n]))
        elif c == 'ß':
            Z.append ('ss')
        elif c in '-./':
            Z.append (' ')
        else:
            Z.append (c)
    S = ''.join (Z)
    S = re.sub(' +', ' ', S)
    return S
