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
# $Id: LaTeX.py,v 1.2.2.1 2003/08/06 09:09:54 fredgo Exp $


""" This module is a formatter for LaTeX output """

from Pyblio import Formatter, Autoload
import string

class LaTeX (Formatter.Formatter):

    coding = 'LaTeX'
    
    def write (self, text, style = None):
        if   style == 'bold':
            self.out.write ('{\bf %s}' % text)
        elif style == 'italic':
            self.out.write ('{\it %s}' % text)
        elif style == 'emph':
            self.out.write ('{\em %s}' % text)
        elif style == 'slanted':
            self.out.write ('{\sl %s}' % text)
        elif style == 'smallcaps':
            self.out.write ('{\sc %s}' % text)
        else:
            self.out.write (text)

    def start_group (self, id, key_list = None):
        if key_list:
            id = ''
            l  = 0
            for k in key_list:
                # compute length
                w = 0
                for i in range (0, len (k)):
                    if k [i] == string.lower (k [i]):
                        w = w + .5
                    else:
                        w = w + 1
                        
                if w > l:
                    id = k
                    l  = w
                    
        else:
            id = 'KEY99'
            
        self.out.write ('\\begin{thebibliography}{%s}\n' % id)
        return

    def separator (self):
        self.out.write ('\n\\newblock ')
        return
    
    def end_group (self):
        self.out.write ('\\end{thebibliography}\n')
        return

    def start (self, key, entry):
        if key is None: key = self.next_key ()
        
        self.out.write ('\\bibitem[%s]{%s}\n' % (key, entry.key.key))
        return

    
Autoload.register ('output', 'LaTeX', LaTeX)

