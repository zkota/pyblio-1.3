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

''' This module implements a Dialog to define Sort criterions '''

import os, string

import gtk, gobject
from gnome import ui

from Pyblio import Connector, Sort, Config, version
from Pyblio.GnomeUI import Utils

import cPickle

pickle = cPickle
del cPickle


class SortDialog (Connector.Publisher, Utils.GladeWindow):

    """ Provide a configuration dialog for sorting the main index.
    Emit a 'sort-data' signal when the user chooses new sort options.
    """

   # This dialog is described as a glade XML file
    gladeinfo = { 'file': 'sort.glade',
                  'root': '_w_sort',
                  'name': 'sort'
                  }
    
    def __init__ (self, sort, parent = None):

        """ Create the dialog.

          - current_sort: the current sorting options
          - parent: parent window
       """
        
        Utils.GladeWindow.__init__ (self, parent)

        self._model = gtk.ListStore (gtk.gdk.Pixbuf, str, gobject.TYPE_PYOBJECT, int)
        self._w_tree.set_model (self._model)


        # Only the first two rows are visibles, the others are for
        # internal bookkeeping.
        
        col = gtk.TreeViewColumn ('Direction', gtk.CellRendererPixbuf (), pixbuf = 0)
        self._w_tree.append_column (col)

        col = gtk.TreeViewColumn ('Field', gtk.CellRendererText (), text = 1)
        self._w_tree.append_column (col)

        self._w_sort.show ()

        self._icon = {0: None}

        for id, stock in ((1, gtk.STOCK_GO_UP), (-1, gtk.STOCK_GO_DOWN)):
                          
            self._icon [id] = self._w_tree.render_icon (stock_id = stock,
                                                        size = gtk.ICON_SIZE_MENU,
                                                        detail = None)
        

        # Gather the current sort info for all the available
        # fields. We create a tuple containing:
        #  (display name, sort criterion instance, sort direction)
        #
        # The sort direction can be:
        #   0: not sorting according to this
        #   1: ascending sort
        #  -1: descending sort
        
        if sort: sort = sort.fields
        else:    sort = []

        # These are additional search fields
        avail = [[_("[Entry Type]"), Sort.TypeSort (), 0],
                 [_("[Key Value]"),  Sort.KeySort (), 0]]

        
        fields = map (lambda x: x.name,
                      Config.get ('base/fields').data.values ())
        fields.sort ()

        def make_one (x):
            return [x, Sort.FieldSort (x.lower ()), 0]

        avail = avail + map (make_one, fields)

        # Update the list with the current user settings
        for v in avail:

            if v [1] not in sort: continue
            
            i = sort.index (v [1])
            
            if sort [i].ascend: v [2] = +1
            else:               v [2] = -1

        # In the list, display the fields that are used in the current
        # sort procedure first.
        
        for k, v, d in filter (lambda x: x [2], avail):
            s = self._icon [d]

            self._model.append ((s, k, v, d))
        
        s = self._icon [0]
        for k, v, d in filter (lambda x: x [2] == 0, avail):
            self._model.append ((s, k, v, d))
        
        return


    def on_activate (self, view, path, col):

        ''' Toggle between the three states for the selected field (do
        not sort, ascending sort, descending sort) '''
        
        row = self._model [path]

        d = ((row [3] + 2) % 3) - 1

        row [3] = d
        row [0] = self._icon [d]
        return


    def _results (self):

        ''' Extract the current sorting settings '''
        
        sort = []

        for r in self._model:
            item, dir = r [2], r [3]

            # Only consider fields on which we sort
            if dir == 0: continue

            # Store the direction of sorting in each item
            if dir > 0: item.ascend = True
            else:       item.ascend = False
            
            sort.append (item)

        if not sort: sort = None
        else:  sort = Sort.Sort (sort)

        return sort
    

    def set_as_default (self, * arg):

        ''' Pickle the current sorting settings to be used as the
        default value '''
        
        Utils.config.set_string ('/apps/pybliographic/sort/default',
                                 pickle.dumps (self._results ()))
        return
    

    def on_cancel (self, * arg):
        ''' Invoked when the user clicks on Cancel '''
        
        self.size_save ()
        self._w_sort.destroy ()
        return


    def on_accept (self, * arg):
        ''' Invoked when the user clicks on Apply '''

        self.size_save ()
        self.issue ('sort-data', self._results ())
        self._w_sort.destroy ()
        return
    
