# -*- coding: UTF-8 -*-
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
# Modified version of text.py. It is used for abbrvnum.xml style.
# Created by Zoltán Kóta.

""" This is a module that codes bibliographies into simple text output """

import sys, string

from Legacy import Autoload, Utils, Formatter

class TextFormat (Formatter.Formatter):

    coding = 'Latin1'
    
    def start_group (self, id, key_list = None):
        self.out.write ("%s\n\n" % id)
        
        if key_list:
            self.length = 0
            for k in key_list:
                if len (k) > self.length:
                    self.length = len (k)
        else:
            self.length = 3

        # add [] plus one space
        self.length = self.length + 3
        return

    def end_group (self):
        self.out.write ("\n")
        pass

    def start (self, key, entry):
        if key is None: key = self.next_key ()
        
        self.data = ""
        self.key  = '[%s] ' % key
        extra = self.length - len (self.key)
        if extra > 0:
            self.key = self.key + ' ' * extra
        return
    
    def write (self, text, style = None):
        self.data = self.data + text
        return

    def separator (self):
        self.write (" ")
        return
    
    def end (self):
        self.data = string.strip (self.data)
        
        text = Utils.format (self.data, 79, self.length, self.length)
        self.out.write (self.key + text [self.length:] + '\n\n')
        return
    

Autoload.register ('output', 'textnum', TextFormat)
