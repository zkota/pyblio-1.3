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

from Pyblio import Types

import string, gettext
_ = gettext.gettext


class Sort:
    ''' This class defines the methods used to sort a database '''
    
    def __init__ (self, fields = None):
        ''' Create a Sort class with a given set of SortFields '''
        
        self.fields = fields or []
        return

    def sort (self, iterator):
        ''' Returns a list of keys sorted according to the current
        sort settings '''
        
        data = {}
        keys = []
        ent  = {}
        
        # get the data for each field
        entry = iterator.first ()
        while entry:
            item = []
            for field in self.fields:
                f = field.get_field (entry)
                a = field.ascend
                
                item.append ((f, a))
                
            data [entry.key] = item
            keys.append (entry.key)
            ent  [entry.key] = entry
            
            entry = iterator.next ()

        # sort them
        def cmp_fcn (a, b, data = data):
            da = data [a]
            db = data [b]
            for i in range (len (da)):
                a = da [i]
                b = db [i]
                c = cmp (a [0], b [0]) * a [1]

                if c: return c
            return 0

        keys.sort (cmp_fcn)
        
        return keys, ent


    def __repr__ (self):
        return 'Sort (%s)' % str (self.fields)

    
class TypeSort:

    def __init__ (self, ascend = 1):
        self.ascend = ascend
        return

    
    def get_field (self, entry):
        return entry.type


    def __repr__ (self):
        return 'TypeSort ()'


    def __cmp__ (self, other):
        if isinstance (other, TypeSort): return 0
        return -1
    

class KeySort:

    def __init__ (self, ascend = 1):
        self.ascend = ascend
        return

    
    def get_field (self, entry):
        return entry.key


    def __repr__ (self):
        return 'KeySort ()'


    def __cmp__ (self, other):
        if isinstance (other, KeySort): return 0
        return -1
    

class FieldSort:
    
    def __init__ (self, field, ascend = 1):
        self.field  = field
        self.ascend = ascend
        return

    def get_field (self, entry):
        try:
            return entry [self.field]
        except KeyError:
            return Types.get_field (self.field).type ('')
        

    def __repr__ (self):
        return 'FieldSort (%s)' % `self.field`


    def __cmp__ (self, other):
        if not hasattr (other, 'field'): return -1
        
        return cmp (string.lower (self.field),
                    string.lower (other.field))
