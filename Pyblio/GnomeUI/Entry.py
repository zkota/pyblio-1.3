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

from gtk import *
from gnome import ui

import pango, gnome

import string

from Pyblio.GnomeUI import Utils
from Pyblio import Config, recode, Fields


class Entry:
    ''' Displays a bibliographic entry as simple text '''

    def __init__ (self):
        ''' Create the graphical widget '''
        
        self.text = TextView ()
        self.buff = self.text.get_buffer ()

        self.tag = {}
        
        self.tag ['title'] = \
                 self.buff.create_tag ('title',
                                       weight = pango.WEIGHT_BOLD)
        self.tag ['field'] = \
                 self.buff.create_tag ('field',
                                       indent = -20,
                                       style = pango.STYLE_OBLIQUE)
        self.tag ['body'] = \
                 self.buff.create_tag ('body',
                                       left_margin = 20)

        self.w = ScrolledWindow ()
        self.w.set_policy (POLICY_AUTOMATIC, POLICY_AUTOMATIC)
        self.w.add (self.text)

        self.text.set_editable (False)
        self.text.set_cursor_visible (False)
        self.text.set_wrap_mode (WRAP_WORD)
        self.text.set_left_margin (5)
        self.text.set_right_margin (5)
        
        # currently, nothing to display
        self.entry = None
        return

    def display (self, entry):
        self.entry = entry

        if not self.entry:
            self.buff.set_text ('')
            return
        
        # Display this entry
        self.buff.delete (self.buff.get_start_iter (),
                          self.buff.get_end_iter ())
        
        iter = self.buff.get_start_iter ()
        
        self.buff.insert_with_tags (iter, entry.type.name,
                                    self.tag ['title'])
        self.buff.insert_with_tags (iter, ' {'+ str (entry.key.key) + '}\n\n',
                                    self.tag ['title'])

        dico = entry.keys ()


        def maybe_insert_button (field):
            """ Create a button that opens the URL if the field is of type URL """
            
            if not isinstance (field, Fields.URL): return
            
            # Add a button to open the URL
            self.buff.insert (iter, ' ')

            anchor = self.buff.create_child_anchor (iter)
            
            button = Button ('...')
            button.show ()

            def url_open (w, url):
                gnome.url_show (url)
                return
                
            button.connect ('clicked', url_open, str (field))
            
            self.text.add_child_at_anchor (button, anchor)
            return
        
        for f in entry.type.fields:
            
            field = string.lower (f.name)
            
            if entry.has_key (field):

                n = f.name + ': '
                t = str (entry [field]).decode ('latin-1')
                
                si = iter.get_offset ()

                self.buff.insert (iter, n)
                mi = iter.get_offset ()
                
                self.buff.insert (iter, t)

                si = self.buff.get_iter_at_offset (si)
                mi = self.buff.get_iter_at_offset (mi)
                
                self.buff.apply_tag (self.tag ['body'],
                                     si, iter)
                self.buff.apply_tag (self.tag ['field'],
                                     si, mi)

                maybe_insert_button (entry [field])
                
                self.buff.insert (iter, '\n')
                
                dico.remove (field)


        self.buff.insert (iter, '\n')

        dico.sort ()
        
        for f in dico:
            n = f + ': '
            t = str (entry [f]).decode ('latin-1')
            
            si = iter.get_offset ()
            
            self.buff.insert (iter, n)
            mi = iter.get_offset ()
            
            self.buff.insert (iter, t)
                
            si = self.buff.get_iter_at_offset (si)
            mi = self.buff.get_iter_at_offset (mi)
                
            self.buff.apply_tag (self.tag ['body'],
                                 si, iter)
            self.buff.apply_tag (self.tag ['field'],
                                 si, mi)

            maybe_insert_button (entry [f])
            
            self.buff.insert (iter, '\n')

        return

    def clear (self):
        self.buff.set_text ('')
        return


        
