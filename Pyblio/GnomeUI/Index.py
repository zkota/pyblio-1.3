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


# TO FIX
#
#  - DnD with the world
#  - Copy/Paste with the world


''' Main index containing the columned view of the entries '''

from Pyblio import Fields, Config, Connector, Types, Sort

from gnome import ui
import gtk, gobject

from Pyblio.GnomeUI import FieldsInfo, Utils, Mime

from string import *

import gettext, cPickle

pickle = cPickle
del cPickle

_ = gettext.gettext


class Index (Connector.Publisher):
    ''' Graphical index of an iterator '''
    
    def __init__ (self, fields = None):
        ''' Creates a new list of entries '''
        
        fields = fields or Config.get ('gnome/columns').data
        self.fields = map (lower, fields)

        self.model = apply (gtk.ListStore,
                            (gobject.TYPE_STRING,) * len (fields))

        self.list = gtk.TreeView ()
        self.list.set_model (self.model)
        
        self.selinfo = self.list.get_selection ()
        self.selinfo.set_mode (gtk.SELECTION_MULTIPLE)
        
        i = 0
        for f in fields:
            col = gtk.TreeViewColumn (f, gtk.CellRendererText (),
                                      text = i)
            col.set_resizable (True)
            col.set_clickable (True)

            k = '/apps/pybliographic/columns/%s' % self.fields [i]
            w = Utils.config.get_int (k)

            if w:
                col.set_sizing (gtk.TREE_VIEW_COLUMN_FIXED)
                col.set_fixed_width (w)
            
            col.connect ('clicked', self.click_column, i)
            
            self.list.append_column (col)
            i = i + 1
        
        self.w = gtk.ScrolledWindow ()

        self.w.set_policy (gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.w.add (self.list)

        self.access = []

        # contextual popup menu
        self.menu = gtk.Menu ()
        
        Utils.popup_add (self.menu, _('Add...'),
                         self.entry_new)
        Utils.popup_add (self.menu, _('Edit...'),
                         self.entry_edit)
        Utils.popup_add (self.menu, _('Delete...'),
                         self.entry_delete)
        
        # some events we want to react to...
        self.selinfo.connect ('changed', self.select_row)

        self.list.connect ('row-activated', self.entry_edit)
        self.list.connect ('button-press-event', self.button_press)

        # DnD configuration
 
        targets = (
            (Mime.SYM_KEY,    0, Mime.KEY),
            (Mime.SYM_ENTRY,  0, Mime.ENTRY),
            (Mime.SYM_STRING, 0, Mime.STRING),
            )
 
        accept = (
            (Mime.SYM_ENTRY,  0, Mime.ENTRY),
            )
 
        self.list.drag_dest_set (gtk.DEST_DEFAULT_ALL, accept,
                                 gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE)
        self.list.connect ("drag_data_received", self.drag_received)
 
 
        self.list.drag_source_set (gtk.gdk.BUTTON1_MASK | gtk.gdk.BUTTON3_MASK,
                                   targets, gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE)
        self.list.connect ('drag_data_get', self.dnd_drag_data_get)
 
        # Copy/Paste configuration
 
        self.selection_buffer = None
         
        self.list.connect ('selection_received', self.selection_received)
        self.list.connect ('selection_get', self.selection_get)
        self.list.connect ('selection_clear_event', self.selection_clear)

        # We handle three selections: one specific to the application,
        # the clipboard, and the primary. Therefore, we should be able
        # to paste into every kind of editor/application.
        
        self.list.selection_add_target ("PRIMARY",
                                        Mime.SYM_STRING,
                                        Mime.STRING)
        
        self.list.selection_add_target ("CLIPBOARD",
                                        Mime.SYM_STRING,
                                        Mime.STRING)
        
        self.list.selection_add_target (Mime.SYM_APP,
                                        Mime.SYM_ENTRY,
                                        Mime.ENTRY)
        return


    def selection_clear (self, * arg):
        self.selection_buffer = None
        return

    
    def selection_received (self, widget, selection, info):
        
        data = selection.data
        
        if not data: return
 
        entries = pickle.loads (data)
        self.issue ('drag-received', entries)
        return


    def selection_get (self, widget, selection, info, time):

        if not self.selection_buffer: return

        if info == Mime.ENTRY:
            
            text = pickle.dumps (self.selection_buffer)
            selection.set (Mime.SYM_ENTRY, 8, text)

        elif info == Mime.STRING:
            
            if Config.get ('gnome/paste-key').data:
                # if we want the keys, return the keys !
                keys = []
                for e in self.selection_buffer:
                    keys.append (str (e.key.key))
                text = join (keys, ',')
            else:
                # else, return the full entries
                text = join (map (str, self.selection_buffer), '\n\n')

            selection.set ("STRING", 8, text)
        
        return


    def selection_copy (self, entries):
        # Advertise the fact that we hold the selection
        self.list.selection_owner_set (Mime.SYM_APP)
        self.list.selection_owner_set ("PRIMARY")
        self.list.selection_owner_set ("CLIPBOARD")
        
        self.selection_buffer = entries
        return


    def selection_paste (self):
        # Request the selection as a full entry
        self.list.selection_convert (Mime.SYM_APP, Mime.SYM_ENTRY)
        return

        
    def drag_received (self, * arg):
        selection = arg [4]
        info      = arg [5]

        if info == Mime.ENTRY:
            entries = pickle.loads (selection.data)
            self.issue ('drag-received', entries)

        return

    
    def dnd_drag_data_get (self, list, context, selection, info, time):
        ''' send the selected entries as dnd data '''

        entries = self.selection ()
        if not entries: return

        if info == Mime.STRING:
            if Config.get ('gnome/paste-key').data:
                # if we want the keys, return the keys !
                keys = []
                for e in entries:
                    keys.append (str (e.key.key))
                text = join (keys, ',')
            else:
                # else, return the full entries
                text = join (map (str, entries), '\n\n')
                
            selection.set (selection.target, 8, text)
            return
        
        if info == Mime.KEY:
            # must return a set of keys
            data = join (map (lambda e: str (e.key.base or '') + '\0' +
                              str (e.key.key), entries), '\n')
            selection.set (selection.target, 8, data)
            
        elif info == Mime.ENTRY:
            data = pickle.dumps (entries)
            selection.set (selection.target, 8, data)

        else:
            return
        
        if context.action == gtk.gdk.ACTION_MOVE:
            self.issue ('drag-moved', entries)
        
        return
    
    # --------------------------------------------------

    def __len__ (self):
        ''' returns the number of lines in the current index '''

        return len (self.access)


    def get_item_position (self, item):
        try:
            return self.access.index (item)
        except ValueError:
            return -1

        
    def select_item (self, item):
        if type (item) is not type (1):
            item = self.get_item_position (item)

        if item == -1 or item >= len (self.access): return

        path = (item,)
        
        self.selinfo.select_path (path)
        self.list.scroll_to_cell (path)

        self.issue ('select-entry', self.access [item])
        return
    
        
    def set_scroll (self, item):
        if type (item) is not type (1):
            item = self.get_item_position (item)

        if item == -1: return
        
        self.list.scroll_to_cell ((item,),
                                  use_align = True,
                                  row_align = .5)
        return

    
    def display (self, iterator):

        # clear the access table
        self.access = []

        Utils.set_cursor (self.w, 'clock')
        
        self.model.clear ()

        entry = iterator.first ()
        while entry:
            row = []

            i = 0
            for f in self.fields:
                row.append (i)
                i = i + 1
                
                if f == '-key-':
                    row.append (str (entry.key.key))
                    
                elif f == '-type-':
                    row.append (str (entry.type.name))
                    
                elif entry.has_key (f):
                    
                    if Types.get_field (f).type == Fields.AuthorGroup:
                        text = join (map (lambda a: str (a.last), entry [f]), ', ')
                    else:
                        text = str (entry [f])
                        
                    row.append (text.decode ('latin-1'))
                else:
                    row.append ('')

            iter = self.model.append  ()
            apply (self.model.set, [iter] + row)
            
            self.access.append (entry)

            entry = iterator.next ()
            
        Utils.set_cursor (self.w, 'normal')
        return


    def go_to_first (self, query, field):
        ''' Go to the first entry that matches a key '''
        if not isinstance (field, Sort.FieldSort): return 0

        f = field.field
        q = lower (query)
        l = len (q)
        i = 0
        
        for e in self.access:
            if not e.has_key (f): continue

            c = cmp (lower (str (e [f])) [0:l], q)

            if c == 0:
                # matching !
                self.set_scroll (i)
                return 1

            if c > 0:
                # we must be after the entry...
                self.set_scroll (i)
                return 0
            
            i = i + 1

        # well, show the user its entry must be after the bounds
        self.set_scroll (i)
        return  0
        
    
    def click_column (self, listcol, column):
        ''' handler for column title selection '''
        
        self.issue ('click-on-field', self.fields [column])
        return


    def select_row (self, sel, * data):
        ''' handler for row selection '''

        entries = self.selection ()
        
        if len (entries) > 1:
            self.issue ('select-entries', entries)
            return

        if len (entries) == 1:
            self.issue ('select-entry', entries [0])
            return
        return


    def selection (self):
        ''' returns the current selection '''
        
        entries = []

        def retrieve (model, path, iter):
            entries.append (self.access [path [0]])

        self.selinfo.selected_foreach (retrieve)

        return entries


    def select_all (self):
        ''' select all the lines of the index '''
        
        self.clist.select_all ()
        return

    
    def button_press (self, clist, event, *arg):
        ''' handler for double-click and right mouse button '''

        if not (event.type == gtk.gdk.BUTTON_PRESS and
                event.button == 3): return
        
        # what menu items are accessible ?
        sel = self.selection ()
            
        if len (sel) == 0: mask = (1, 0, 0)
        else:              mask = (1, 1, 1)

        child = self.menu.get_children ()
        for i in range (3):
            child [i].set_sensitive (mask [i])
            
        self.menu.popup (None, None, None, event.button, event.time)
        return


    def entry_new (self, * arg):
        self.issue ('new-entry')
        return

    
    def entry_edit (self, * arg):
        sel = self.selection ()
        if not sel: return

        self.issue ('edit-entry', sel)
        return

        
    def entry_delete (self, * arg):
        sel = self.selection ()
        if not sel: return
        
        self.issue ('delete-entry', sel)
        return


    def update_configuration (self):

        for i in range (len (self.fields)):
            w = self.list.get_column (i).get_width ()
            k = '/apps/pybliographic/columns/%s' % self.fields [i]
            
            Utils.config.set_int (k, w)
        return
