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

class Iterator:

    def iterator (self):
        ''' loop method, so that we can for example call a method by
        passing indifferently a database or a database iterator...
        '''
        
        return self

    
class DBIterator (Iterator):
    ''' This class defines a database iterator '''
    
    def __init__ (self, database):
        self.keys     = database.keys ()
        self.database = database
        return

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

    
