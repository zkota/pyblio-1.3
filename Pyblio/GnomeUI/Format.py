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

''' Defines a Dialog to format a subset of entries as a bibliography '''

import gtk
from gnome import ui

import string, os

from Pyblio import Connector, version, Autoload
from Pyblio.GnomeUI import Utils


class FormatDialog (Connector.Publisher, Utils.GladeWindow):

    """ Class implementing the Format dialog. This class issues a

        'format-query'

        signal when the user applies its settings
    """

    gladeinfo = { 'file': 'format.glade',
                  'root': '_w_format',
                  'name': 'format'
                  }
    
    def __init__ (self, parent = None):

        Utils.GladeWindow.__init__ (self, parent)

        # Fill the output format drop-down menu
        menu = gtk.Menu ()
        self._w_menu.set_menu (menu)
        
        outlist = Autoload.available ('output')
        outlist.sort ()
        
        for avail in outlist:
            Utils.popup_add (menu, avail, self._menu_select, avail)

        self._w_menu.set_history (0)
        self.menu_item = outlist [0]

        path = os.path.join (version.pybdir, 'Styles')
        
        self._w_style_entry.set_default_path (path)
        self._w_format.show ()
        return


    def _menu_select (self, menu, item):
        self.menu_item = item
        return
    

    def _on_validate (self, * arg):

        style  = self._w_style_entry.get_full_path (False)
        output = self._w_output_entry.get_full_path (False)
        
        format = Autoload.get_by_name ('output', self.menu_item).data

        if style is None or output is None: return
        self._w_format.destroy ()

        self.issue ('format-query', style, format, output)
        return
    

    def _on_close (self, * arg):

        self.size_save ()
        self._w_format.destroy ()
        return
