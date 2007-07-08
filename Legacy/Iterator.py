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

# TODO: get rid of all of this, and use standard iterators / generators

class Iterator:

    base = None
    title = "Some Selection"
    
    def iterator (self):
        ''' loop method, so that we can for example call a method by
        passing indifferently a database or a database iterator...
        '''
        return self

    def __iter__ (self):
        retval =  self.first ()
        while retval != None:
            yield retval
            retval = self.next()
        raise StopIteration
            
    def set_position (self, pos=0):
        self._position = 0

    def get_position (self):
        return self._position
    
    def first (self):
        self.set_position (0)
        return self.next ()

    
class DBIterator (Iterator):
    ''' This class defines a database iterator '''
    
    def __init__ (self, database):
        self.keys = database.keys ()
        self.base = database
	self.database = database
        self.count = 0
        return

    def __iter__ (self):
        self._position = 0
        for k in self.keys:
            yield self.database [k]
            self._position += 1

    def first (self):
        self.count = 0
        return self.next ()
        
    def next (self):

        try:
            entry = self.database [self.keys [self.count]]
        except IndexError:
            entry = None
        
        self.count = self.count + 1
        return entry
    
