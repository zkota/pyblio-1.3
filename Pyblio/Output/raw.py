# This file is part of pybliographer
# 
# Copyright (C) 1998-2003 Frederic GOBRY
# Email : gobry@idiap.ch
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
# $Id: raw.py,v 1.2.2.1 2003/08/06 09:09:54 fredgo Exp $

""" This is a module that codes bibliographies into simple text output """

import sys

from Pyblio import Autoload, Base, Formatter

class TextFormat (Formatter.Formatter):

    coding = 'Latin1'
    
    def start_group (self, id, table = None):
        self.out.write ("Bibliography\n\n")
        pass

    def end_group (self):
        self.out.write ("\n")
        pass

    def start (self, key, entry):
        if key is None: key = self.next_key ()

        text = ('[%s] ' % key)
        self.write (text)
        extra = 16 - len (text)
        if extra > 0:
            self.write (' ' * extra)
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
    

Autoload.register ('output', 'raw', TextFormat)
