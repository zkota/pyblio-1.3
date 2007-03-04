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

''' This class defines certain graphical properties of output, in
order to insulate a bibliographic style definition from its
realization in a given language '''

import sys

from Legacy import Autoload, Base

class Formatter:

    coding = 'Latin1'
    
    def __init__ (self, stdout = sys.stdout):
        self.out     = stdout
        self.counter = 1
        return

    def start_group (self, id, table = None):
        pass

    def end_group (self):
        pass

    def next_key (self):
        key = str (self.counter)
        self.counter = self.counter + 1

        return key
    
    def start (self, key, entry):
        return
    
    def write (self, text, style = None):
        self.out.write (text)
        return

    def separator (self):
        self.write (" ")
        return
    
    def end (self):
        self.write ("\n")
        return
    

def format (fields,
            text,
            filter  = None,
            out     = sys.stdout,
            default = {},
            pre     = {},
            post    = {}):

    printable = {}
    # completer le texte
    for f in fields.keys ():
        t = fields [f]
        
        if filter:
            t = filter (t)
        
        if pre.has_key (f):
            t = pre [f] + t
            
        if post.has_key (f):
            t = t + post [f]

        printable [f] = t
        
    # completer les champs
    for f in default.keys ():
        if not fields.has_key (f):
            printable [f] = default [f]


    out.write (text % printable)

    return
