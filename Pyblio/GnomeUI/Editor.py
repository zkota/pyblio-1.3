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

# TO FIX
#   entry editor for more than 50 chars

import string, re
from gnome import ui
import gtk

import copy, re

from Pyblio import Fields, Config, Base, Types, Connector, Exceptions, Key

from Pyblio.GnomeUI import FieldsInfo, Utils, Mime

key_re = re.compile ("^[\w:_+-.]+$")

_newcontent = {
    Fields.AuthorGroup : _("Last Name, First Name"),
    Fields.Text        : _("Text"),
    Fields.URL         : 'http://',
    Fields.Date        : '2000',
    Fields.Reference   : [],
    }


class BaseField (Connector.Publisher):
    ''' common class to each specialized field editor '''
    
    def __init__ (self, entry, field, content, j):

        self.w = gtk.VBox ()

        h = gtk.HBox (spacing = 5)
        self.w.pack_start (gtk.Label (field), False, False)

        field = string.lower (field)
        self.field = field

        self.setup (entry)

        self.edit = None
        expand = self.create_widget (h)
        
        img = gtk.Image ()
        
        if self.loss: img.set_from_stock (gtk.STOCK_CANCEL,
                                          gtk.ICON_SIZE_BUTTON)
        else:         img.set_from_stock (gtk.STOCK_APPLY,
                                          gtk.ICON_SIZE_BUTTON)
        
        h.pack_start (img, False, False)
        
        self.w.pack_start (h, expand, expand)
        self.w.show_all ()

        flag = 0
        if expand: flag = gtk.EXPAND | gtk.FILL
        content.attach (self.w, 0, 1, j, j + 1, yoptions = flag)
        return


    def key_handler (self, widget, ev):
        if ev.keyval == gtk.gdk.Return and \
           ev.state  == gtk.gdk.CONTROL_MASK:
            widget.emit_stop_by_name ('key_press_event')
            self.issue ('apply')
        
        elif ev.keyval == gtk.gdk.Tab and \
           ev.state  == gtk.gdk.CONTROL_MASK:
            widget.emit_stop_by_name ('key_press_event')
            self.issue ('next')

        return 1


    def setup (self, entry):
        if entry.has_key (self.field):
            (self.value, self.loss)  = entry.field_and_loss (self.field)
            self.string = str (self.value)
        else:
            (self.value, self.loss) = (None, 0)
            self.string = ''
        return

    
    def update (self, entry):
        text = string.strip (self.edit.get_chars (0, -1)).encode ('latin-1')

        if text == self.string: return 0

        if text == '':
            del entry [self.field]
            return 1

        self.update_content (entry, text)
        return 1
        

class TextBase (BaseField):
    ''' Virtual class common to Text and Entry '''

    def setup (self, entry):
        BaseField.setup (self, entry)

        if self.string and self.string [0] == '@':
            self.string = ' ' + self.string
        return

    
    def update (self, entry):
        text = string.rstrip (self.edit.get_chars (0, -1)).encode ('latin-1')
        if text == self.string: return 0

        if text == '':
            del entry [self.field]
            return 1

        self.update_content (entry, text)
        return 1


    def update_content (self, entry, text):
        if text [0] == '@' and hasattr (entry, 'set_native'):
            entry.set_native (self.field, string.lstrip (text [1:]))
            return

        text = string.lstrip (text)
        entry [self.field] = Fields.Text (text)
        return

    
class Entry (TextBase):

    def create_widget (self, h):
        if len (self.string) < 50:
            self.edit = gtk.Entry ()
            self.edit.set_text (self.string.decode ('latin-1'))
            self.edit.set_editable (True)
            self.edit.show ()

            self.buff = None
            
            h.pack_start (self.edit)
            return 0

        w = gtk.ScrolledWindow ()
        w.set_policy (gtk.POLICY_NEVER,
                      gtk.POLICY_AUTOMATIC)
        
        self.edit = gtk.TextView ()
        self.edit.set_editable (True)
        self.edit.set_wrap_mode (gtk.WRAP_WORD)

        self.buff = self.edit.get_buffer ()
        self.buff.set_text (self.string.decode ('latin-1'))

        self.edit.show ()
        
        w.add (self.edit)
        w.show ()
        
        h.pack_start (w)
        return 1


    def update (self, entry):
        if self.buff:
            text = self.buff.get_text (self.buff.get_start_iter (),
                                       self.buff.get_end_iter ())
            text = string.rstrip (text).encode ('latin-1')
        else:
            text = string.rstrip \
                   (self.edit.get_chars (0, -1)).encode ('latin-1')
            
        if text == self.string: return 0

        if text == '':
            del entry [self.field]
            return 1

        self.update_content (entry, text)
        return 1



class Text (TextBase):
    
    def create_widget (self, h):
        w = gtk.ScrolledWindow ()
        w.set_policy (gtk.POLICY_NEVER,
                      gtk.POLICY_AUTOMATIC)
        self.edit = gtk.TextView ()
        self.edit.set_editable (True)
        self.edit.set_wrap_mode (gtk.WRAP_WORD)

        self.buff = self.edit.get_buffer ()
        self.buff.set_text (self.string.decode ('latin-1'))

        self.edit.show ()
        w.add (self.edit)
        w.show ()

        h.pack_start (w)
        return 1


    def update (self, entry):
        text = self.buff.get_text (self.buff.get_start_iter (),
                                   self.buff.get_end_iter ())
        text = string.rstrip (text).encode ('latin-1')
        
        if text == self.string: return 0

        if text == '':
            del entry [self.field]
            return 1

        self.update_content (entry, text)
        return 1

class AuthorGroup (BaseField):
    
    def create_widget (self, h):
        w = gtk.ScrolledWindow ()
        w.set_policy (gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        
        self.edit = gtk.TextView ()
        self.edit.set_wrap_mode (gtk.WRAP_WORD)
        self.edit.set_editable (True)

        self.buff = self.edit.get_buffer ()
        self.buff.set_text (self.string.decode ('latin-1'))
        self.edit.show ()
        w.add (self.edit)
        w.show ()

        h.pack_start (w)
        return 1


    def update (self, entry):
        text = self.buff.get_text (self.buff.get_start_iter (),
                                   self.buff.get_end_iter ())
        text = string.strip (text).encode ('latin-1')
        
        if text == self.string: return 0

        if text == '':
            del entry [self.field]
            return 1

        self.update_content (entry, text)
        return 1


    def setup (self, entry):
        if entry.has_key (self.field):
            (self.value, self.loss)  = entry.field_and_loss (self.field)
            names = map (str, self.value)
            self.string = string.join (names, '\n')
        else:
            (self.value, self.loss) = (None, 0)
            self.string = ''
            
        return
        

    def update_content (self, entry, text):
        group = Fields.AuthorGroup ()
        for author in string.split (text, '\n'):
            author = string.strip (author)
            if author == '': continue

            fields = string.split (author, ',')

            if   len (fields) == 1:
                (first, last, lineage) = (None, fields [0], None)
            elif len (fields) == 2:
                (first, last, lineage) = (fields [1], fields [0], None)
            else:
                (first, last, lineage) = (fields [2], fields [0], fields [1])
                
            group.append (Fields.Author ((None, first, last, lineage)))
        
        entry [self.field] = group
        return


class Date (BaseField):
    
    def create_widget (self, h):
        hbox = gtk.HBox (False, 5)

        self.day = gtk.Entry ()
        (width, height) = self.day.size_request ()
        self.day.set_size_request (width / 4, height)
        self.day.set_max_length (2)

        if self.initial [0]:
            self.day.set_text (str (self.initial [0]).decode ('latin-1'))
        hbox.pack_start (self.day)
        hbox.pack_start (gtk.Label (_("Day")), False, False)
        
        self.month = gtk.Entry ()
        self.month.set_size_request (width / 4, height)
        self.month.set_max_length (2)

        if self.initial [1]:
            self.month.set_text (str (self.initial [1]).decode ('latin-1'))
        hbox.pack_start (self.month)
        hbox.pack_start (gtk.Label (_("Month")), False, False)
        
        self.year = gtk.Entry ()
        self.year.set_max_length (4)
        self.year.set_size_request (width / 3, height)

        if self.initial [2]:
            self.year.set_text (str (self.initial [2]).decode ('latin-1'))
        hbox.pack_start (self.year)
        hbox.pack_start (gtk.Label (_("Year")), False, False)

        hbox.show_all ()
        h.pack_start (hbox)
        return 0


    def setup (self, entry):
        if entry.has_key (self.field):
            date = entry [self.field]
            self.initial = (date.day, date.month, date.year)
        else:
            self.initial = (None, None, None)
            
        self.loss = 0
        return

    
    def update (self, entry):
        (day, month, year) = (None, None, None)
        
        text = string.strip (self.day.get_chars (0, -1)).encode ('latin-1')
        if text != '':
            try: day = int (text)
            except ValueError:
                GnomeErrorDialog (_("Invalid day field in date"),
                                  self.day.get_toplevel ()).show ()
                return -1
        
        text = string.strip (self.month.get_chars (0, -1)).encode ('latin-1')
        if text != '':
            try: month = int (text)
            except ValueError, err:
                GnomeErrorDialog (_("Invalid month field in date"),
                                  self.day.get_toplevel ()).show ()
                return -1
        
        text = string.strip (self.year.get_chars (0, -1)).encode ('latin-1')
        if text != '':
            try: year = int (text)
            except ValueError: 
                GnomeErrorDialog (_("Invalid year field in date"),
                                  self.day.get_toplevel ()).show ()
                return -1
        
        if self.initial == (day, month, year): return 0

        if (day, month, year) == (None, None, None):
            del entry [self.field]
            return 1

        try:
            entry [self.field] = Fields.Date ((year, month, day))
        except Exceptions.DateError, error:
            GnomeErrorDialog (str (error),
                              self.day.get_toplevel ()).show ()
            return -1
        return 1


class Reference (BaseField):
    
    def create_widget (self, h):
        accept = (
            (Mime.SYM_KEY, 0, Mime.KEY),
            )

        box = gtk.HBox ()
        box.set_border_width (5)
        
        self.edit = gtk.Label ()
        self.edit.justify = False

        self.edit.set_line_wrap (True)
        self.edit.set_selectable (True)
        
        #self.edit.set_editable (True)
        self.edit.set_text (self.string)
        
        self.edit.drag_dest_set (gtk.DEST_DEFAULT_ALL,
                                 accept,
                                 gtk.gdk.ACTION_COPY)
        
        self.edit.connect ('drag_data_received', self.drag_received)
        
        self.current = Fields.Reference ([])

        box.pack_start (self.edit, True, True)
        h.pack_start (box)

        # A delete button
        button = gtk.Button (_('Delete'), gtk.STOCK_DELETE)
        button.connect ('clicked', self._delete)
        
        h.pack_start (button, False, False)
        
        box.show_all ()
        return 0

    def _delete (self, * args):

        self.current = Fields.Reference ([])
        self.string  = _("[ Drop an Entry here ]")

        self.edit.set_text (self.string)
        return
    

    def setup (self, entry):
        if entry.has_key (self.field):
            (self.value, self.loss)  = entry.field_and_loss (self.field)
            if self.value.list:
                self.string = string.join (map (lambda x: x.key, self.value.list), ', ')
            else:
                self.string = _("[ Drop an Entry here ]")
        else:
            (self.value, self.loss) = (None, 0)
            self.string = _("[ Drop an Entry here ]")
        return
    
    def drag_received (self, *arg):
        selection = arg [4]
        info      = arg [5]

        if not info == Mime.KEY: return

        keys = string.split (selection.data, '\n')
        reflist = []
        for k in keys:
            (base, key) = string.split (k, '\0')
            if not base: base = None
            
            reflist.append (Key.Key (base, key))

        self.current = Fields.Reference (reflist)
        
        text = string.join (map (lambda x: x.key, self.current.list), ', ')
        self.edit.set_text (text)
        return
    

    def update (self, entry):
        
        if self.current == Fields.Reference ([]):
            del entry [self.field]
            return 1

        if self.current == self.value: return 0

        entry [self.field] = self.current
        return 1



class URL (BaseField):
    
    def create_widget (self, h):
        self.edit = gtk.Entry ()
        self.edit.set_editable (True)
        self.edit.set_text (self.string.decode ('latin-1'))
        self.edit.show ()

        h.pack_start (self.edit)
        return 0


    def update_content (self, entry, text):
        entry [self.field] = Fields.URL (text)
        return


class RealEditor (Connector.Publisher):
    ''' Edits in standard form '''

    def __init__ (self, database, entry):
        self.entry    = entry
        self.database = database
        self.type     = entry.type
        self.fields   = entry.keys ()

        self.fields.sort ()
        
        self.w = gtk.VBox ()
        table  = gtk.Table (2, 2)
        table.set_border_width (5)
        table.set_col_spacings (5)
        
        table.attach (gtk.Label (_("Entry type")),
                      0, 1, 0, 1, yoptions = 0)
        table.attach (gtk.Label (_("Key")),
                      1, 2, 0, 1, yoptions = 0)

        self.key = gtk.Entry ()
        self.key.set_editable (True)
        
        if self.entry.key:
            self.key.set_text (self.entry.key.key)
        
        table.attach (self.key,
                      1, 2, 1, 2, yoptions = 0)

        self.menu = gtk.OptionMenu ()
        menu = gtk.Menu ()
        self.menu.set_menu (menu)

        table.attach (self.menu,
                      0, 1, 1, 2, yoptions = 0)

        entry_list = Config.get ("base/entries").data.values ()
        entry_list.sort (lambda x, y: cmp (x.name, y.name))

        i = 0
        history = 0
        for entry in entry_list:
            if entry == self.entry.type: history = i
            Utils.popup_add (menu, entry.name,
                             self.menu_select, entry)
            i = i + 1

        self.menu.set_history (history)
        
        table.show_all ()
        self.w.pack_start (table, False, False)

        self.newfield_area = gtk.HBox (spacing = 5)
        self.newfield_area.set_border_width (5)
        self.newfield = ui.Entry ('newfield')
        
        self.newfield_area.pack_start (self.newfield)

        b = gtk.Button (_("Create Field"))
        b.connect ('clicked', self.create_field)
        self.newfield_area.pack_start (b)
        self.newfield_area.show_all ()
        
        self.w.pack_start (self.newfield_area, False, False)
        
        # Notebook
        # scroll = gtk.ScrolledWindow ()
        # scroll.set_policy (GTK.POLICY_AUTOMATIC, GTK.POLICY_AUTOMATIC)
        self.notebook = gtk.Notebook ()
        self.notebook.show ()

        #scroll.add_with_viewport (self.notebook)
        
        self.w.pack_start (self.notebook)
        self.w.show_all ()
        
        self.notebook_init = False
        self.update_notebook ()
        return


    def menu_select (self, menu, entry):
        # update the current entry
        new = self.update (self.database, copy.deepcopy (self.entry))
        if new is None:
            entry_list = Config.get ("base/entries").data.values ()
            entry_list.sort (lambda x, y: cmp (x.name, y.name))
            self.menu.set_history (entry_list.index (self.entry.type))
            return
        else:
            new.type = entry
            
        self.entry = new
        self.update_notebook ()
        return


    def apply_cb (self, * arg):
        self.issue ('apply')
        return
        
    def next_cb (self, * arg):
        self.issue ('next')
        return

    
    def update_notebook (self):
        if self.notebook_init:
            for i in range (0, 3):
                self.notebook.remove_page (0)
        
        self.notebook_init = True

        names  = (_("Mandatory"), _("Optional"), _("Extra"))
        fields = map (string.lower, self.entry.keys ())
        
        self.content = []
        for i in range (0, 3):
            label   = gtk.Label (names [i])

            if   i == 0: table = map (lambda x: x.name, self.entry.type.mandatory)
            elif i == 1: table = map (lambda x: x.name, self.entry.type.optional)
            else:        table = copy.copy (fields)

            if len (table) == 0: continue

            scroll = gtk.ScrolledWindow ()
            scroll.set_policy (gtk.POLICY_AUTOMATIC,
                               gtk.POLICY_AUTOMATIC)

            content = gtk.Table (1, len (table))
            
            scroll.add_with_viewport (content)

            j = 0
            for field in table:
                lcfield = string.lower (field)

                try: fields.remove (lcfield)
                except ValueError: pass

                widget = FieldsInfo.widget (lcfield) (self.entry, field, content, j)
                self.content.append (widget)

                widget.Subscribe ('apply', self.apply_cb)
                widget.Subscribe ('next', self.next_cb)
                
                j = j + 1

            label.show ()
            content.show ()
            scroll.show ()
            
            self.notebook.insert_page (scroll, label, i)
            
        self.notebook.show ()
        return


    def create_field (self, * arg):
        widget = self.newfield.gtk_entry ()
        text   = string.strip (string.lower (widget.get_text ()))
        if text == '': return

        # update the current entry
        self.entry = self.update (self.database, copy.deepcopy (self.entry))

        newtype = Types.get_field (text).type
        self.entry [text] = newtype (_newcontent [newtype])
        self.update_notebook ()
        return
    

    def update (self, database, entry):
        modified = False
        
        key = string.strip (self.key.get_text ())
        if key == '':
            self.entry.key = None
            modified = True
        else:
            if not key_re.match (key):
                GnomeErrorDialog (_("Invalid key format"),
                                  self.w.get_toplevel ())
                return None

            key = Key.Key (database, key)

            if key != self.entry.key:
                if database.has_key (key):
                    GnomeErrorDialog (_("Key `%s' already exists") % str (key.key),
                                      self.w.get_toplevel ())
                    return None
                
                self.entry.key = key
                modified = True
                
        modified = self.type != self.entry.type or modified
        
        for item in self.content:
            result = item.update (self.entry)
            if result == -1: return None
            
            modified = result or modified

        if not modified:
            fields = self.entry.keys ()
            fields.sort ()

            if fields != self.fields: modified = 1
        
        if modified: return self.entry
        
        return entry
    
            
class NativeEditor (Connector.Publisher):
    ''' Composit widget to edit an entry in its native format '''

    def __init__ (self, database, entry):

        self.entry    = entry
        self.database = database

        if database.has_key (entry.key):
            self.original = database.get_native (entry)
        else:
            self.original = ''
        
        self.w = gtk.TextView ()
        self.w.set_editable (True)

        self.buff = self.w.get_buffer ()

        iter = self.buff.get_start_iter ()
        mono = self.buff.create_tag ('body', family = 'Monospace')

        self.buff.insert_with_tags (iter, self.original.decode ('latin-1'), mono)
        return


    def update (self, database, entry):
        ''' updates and returns the new entry '''

        new  = None
        text = self.buff.get_text (self.buff.get_start_iter (),
                                   self.buff.get_end_iter ()).encode ('latin-1')
        try:
            new = self.database.create_native (text)
            
        except Exceptions.ParserError, msg:
            Utils.error_dialog (_("Error in native string parsing"),
                                str (msg))
        return new

    
class Editor (Connector.Publisher):
    
    def __init__ (self, database, entry, parent = None, title = None):
        self.w = gtk.Dialog ()
        
        self.w.set_resizable (True)
        
        if title: self.w.set_title (title)
        else:     self.w.set_title (_("Edit entry") + ' [%s]' % str (entry.key) )
        
        self.w.connect ('delete_event', self.close_dialog)

        if parent: self.w.set_transient_for (parent)

        self.apply_b = gtk.Button (stock = gtk.STOCK_APPLY)
        self.apply_b.connect ('clicked', self.apply_changes)
        self.apply_b.show ()

        # check if the database supports native editing
        self.has_native = hasattr (database, 'get_native')

        if self.has_native:
            self.native_b = gtk.Button (_("Native Editing"))
            self.native_b.connect ('clicked', self.toggle_native)
            self.native_b.show ()
        
        self.close_b = gtk.Button (stock = gtk.STOCK_CANCEL)
        self.close_b.connect ('clicked', self.close_dialog)
        self.close_b.show ()

        # Use Escape to abort, Ctrl-Return to accept
        accelerator = gtk.AccelGroup ()
        self.w.add_accel_group (accelerator)

        self.close_b.add_accelerator ('clicked', accelerator,
                                      gtk.keysyms.Escape, 0, 0)
        self.apply_b.add_accelerator ('clicked', accelerator,
                                      gtk.keysyms.Return, gtk.gdk.CONTROL_MASK, 0)

        self.w.action_area.add (self.apply_b)
        if self.has_native: self.w.action_area.add (self.native_b)
        self.w.action_area.add (self.close_b)

        self.entry       = entry
        self.database    = database
        self.editor      = None

        # this is the working copy of the entry
        self.current     = copy.deepcopy (entry)
        
        # put the negated value, so that we can call toggle to switch and create
        self.native_mode = not (self.has_native and
                                Config.get ('gnome/native-as-default').data)

        self.toggle_native ()
        
        self.w.show ()
        return


    def toggle_native (self, * arg):
        self.save_size ()
        
        if self.native_mode:

            if self.editor:
                cur = self.editor.update (self.database, self.current)

                # Reject the switch if the data is invalid
                if cur is None: return
                
                self.editor.w.destroy ()
                self.current = cur
                
            # real edition
            self.native_mode = False
            
            if self.has_native:
                self.native_b.get_children () [0].set_text (_("Native Editing"))

            
            self.editor = RealEditor (self.database, self.current)
            
            ui_width  = Utils.config.get_int ('/apps/pybliographic/editor/width')  or -1
            ui_height = Utils.config.get_int ('/apps/pybliographic/editor/height') or -1

        else:
            if self.editor:
                cur = self.editor.update (self.database, self.current)

                # Reject the switch if the data is invalid
                if cur is None: return
                
                self.editor.w.destroy ()
                self.current = cur

            # native edition
            self.native_mode = True

            if self.has_native:
                self.native_b.get_children () [0].set_text (_("Standard Editing"))
            
            self.editor = NativeEditor (self.database, self.current)

            ui_width  = Utils.config.get_int ('/apps/pybliographic/native/width')  or -1
            ui_height = Utils.config.get_int ('/apps/pybliographic/native/height') or -1


        self.editor.Subscribe ('apply', self.apply_changes)
        self.editor.Subscribe ('next',  self.next_item)
        
        self.w.vbox.pack_start (self.editor.w)

        # set window size
        if ui_width != -1 and ui_height != -1:
            self.w.set_default_size (ui_width, ui_height)
            self.w.resize (ui_width, ui_height)
        
        self.editor.w.show ()
        return

    
    def next_item (self, * arg):
        if self.native_mode: return
        
        n = self.editor.notebook
        box = n.get_nth_page (n.get_current_page ())
        
        box.focus (DIR_DOWN)
        pass


    def save_size (self):
        if not self.editor: return
        
        w, h = self.w.get_size ()
        if self.native_mode: field = 'native'
        else:                field = 'editor'

        Utils.config.set_int ('/apps/pybliographic/%s/width' % field,  w)
        Utils.config.set_int ('/apps/pybliographic/%s/height' % field, h)
        return

    
    def close_dialog (self, *arg):
        self.save_size ()
        self.w.destroy ()
        return


    def apply_changes (self, * arg):
        new = self.editor.update (self.database, self.current)
        if new:
            self.close_dialog ()
            if new is not self.entry:
                self.issue ('commit-edition', self.entry, new)
        return
    
