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
# added: Note taking widget

try: _
except NameError:
    import gettext
    _ = gettext.gettext


import gettext, re, string
from gnome import ui
import gtk

import copy, re

from Pyblio import Base, Config, Connector, Exceptions, Fields, Key, Types

from Pyblio.GnomeUI import FieldsInfo, Mime, Utils

key_re = re.compile ("^[\w:_+-.]+$")

_newcontent = {
    Fields.AuthorGroup : _("Last Name, First Name"),
    Fields.Text        : _("Text"),
    Fields.URL         : 'http://',
    Fields.Date        : '2000',
    Fields.Reference   : [],
    Fields.LongText    : '',
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

    
    def update_content (self, entry, text):
        if text [0] == '@' and hasattr (entry, 'set_native'):
            try:
                entry.set_native (self.field, string.lstrip (text [1:]))
                
            except Exceptions.ParserError, msg:
                Utils.error_dialog (_("Error in native string parsing"), str (msg))
                return -1
            
            return 1

        text = string.lstrip (text)
        entry [self.field] = Fields.Text (text)
        return 1

    
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

        return self.update_content (entry, text)



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

        return self.update_content (entry, text)


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
                ui.gnome_error_dialog_parented (_("Invalid day field in date"),
                                                self.day.get_toplevel ())
                return -1
        
        text = string.strip (self.month.get_chars (0, -1)).encode ('latin-1')
        if text != '':
            try: month = int (text)
            except ValueError, err:
                ui.gnome_error_dialog_parented (_("Invalid month field in date"),
                                                self.day.get_toplevel ())
                return -1
        
        text = string.strip (self.year.get_chars (0, -1)).encode ('latin-1')
        if text != '':
            try: year = int (text)
            except ValueError: 
                ui.gnome_error_dialog_parented (_("Invalid year field in date"),
                                                self.day.get_toplevel ())
                return -1
        
        if self.initial == (day, month, year): return 0

        if (day, month, year) == (None, None, None):
            del entry [self.field]
            return 1

        try:
            entry [self.field] = Fields.Date ((year, month, day))
        except Exceptions.DateError, error:
            ui.gnome_error_dialog_parented (str (error),
                                            self.day.get_toplevel ())
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
            (self.current, self.loss)  = entry.field_and_loss (self.field)
            
            if self.current.list:
                self.string = string.join (map (lambda x: x.key, self.current.list), ', ')
            else:
                self.string = _("[ Drop an Entry here ]")
        else:
            (self.current, self.loss) = (Fields.Reference ([]), 0)
            self.string = _("[ Drop an Entry here ]")

        self.initial = self.current
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

        if self.current == self.initial: return 0

        if self.current == Fields.Reference ([]):
            del entry [self.field]
            return 1

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

    def __init__ (self, database, entry, dialogue):
        self.entry    = entry
        self.database = database
        self.dialogue = dialogue
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

        # navigation buttons
        self.backward_b = gtk.Button(_('Back'))
        self.backward_b.connect ('clicked', self.back_cb)
        self.newfield_area.pack_start (self.backward_b)
        self.forward_b = gtk.Button(_('Next'))
        self.forward_b.connect ('clicked', self.next_cb)
        self.newfield_area.pack_start (self.forward_b)
        
        self.w.pack_start (self.newfield_area, False, False)       

        self.newfield_area.show_all ()
        
        # Notebook
        self.notebook = gtk.Notebook ()
        self.notebook.show ()
        self.notebook.connect ('switch-page', self.switch_page_cb)
        
        self.w.pack_start (self.notebook)
        self.w.show_all ()

        self.lt_init (self.entry, self.fields)
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


    def apply_cb (self, * args):
        self.issue ('apply')
        return
        
    def back_cb  (self, *args):
        if self.current_page == self.lt_detail.page:
            self.lt_prev ()
        else:
            self.issue('back')

    def next_cb (self, * args):
        if self.current_page == self.lt_detail.page:
            self.lt_next ()
        else: 
            self.issue ('next')
            return

    def add_cb (self, *args):
        if (self.lt_listvw and self.current_page == self.lt_listvw.page) or \
           (self.lt_detail and self.current_page == self.lt_detail.page): 
            self.lt_new()
        
    def del_cb (self, *args):
        if self.lt_detail and self.current_page == self.lt_detail.page:
            node = self.lt_nodes [self.lt_current]
            key = node['key']
            if self.entry.has_key(key) and self.entry[key]:
                dialog = gtk.MessageDialog(
                    self.w.get_toplevel(), gtk.DIALOG_DESTROY_WITH_PARENT,
                    gtk.MESSAGE_WARNING, gtk.BUTTONS_OK_CANCEL,
                    "Text will be lost if you click OK.")
                rc = dialog.run()
                dialog.destroy()
                
                if rc == gtk.RESPONSE_CANCEL:
                    return
            self.lt_delete (self.lt_current)

    def set_buttons (self, pos):
        """sets the button's sensitivity according to
        current page."""
        
       
        if (self.lt_listvw and self.current_page == self.lt_listvw.page) \
            or (self.lt_detail and self.current_page == self.lt_detail.page):
            self.dialogue.new_b.set_sensitive (True)
            if len(self.lt_nodes) > 1:
                self.forward_b.set_sensitive (True)
                self.backward_b.set_sensitive (True)
        else:
            self.dialogue.new_b.set_sensitive (False)
            self.forward_b.set_sensitive (False)
            self.backward_b.set_sensitive (False)

        if self.lt_detail and self.current_page == self.lt_detail.page:
            self.dialogue.del_b.set_sensitive (True)
        else:
            self.dialogue.del_b.set_sensitive (False)

   
    def switch_page_cb (self, nb, dummy, pos):
        assert self.notebook == nb
        page = self.notebook.get_nth_page(pos)
        self.current_page = page
        self.set_buttons(pos)
        if self.lt_listvw and self.current_page == self.lt_listvw.page:
            self.lt_listvw.display_list (self.entry, self.lt_nodes)


    def update_notebook (self):

        if self.notebook_init:
            self.notebook.foreach(
                lambda x: self.notebook.remove_page(0))
        
        self.notebook_init = True
        self.current_page = None
        
        names  = (_("Mandatory"), _("Optional"), _("Notes"), _("Extra"))

        self.fields = map (string.lower, self.entry.keys ())

        self.content = []

        for i in range (len(names)):
            label   = gtk.Label (names [i])
            if   i == 0:
                table = [x.name.lower() for x
                         in self.entry.type.mandatory
                         if x.type != Fields.LongText]
                self.add_type1_widget (label, table, i)
                list_remove (self.fields, table)

            elif i == 1:
                table = [x.name.lower() for x
                         in self.entry.type.optional
                         if x.type != Fields.LongText]
                self.add_type1_widget (label, table, i)
                list_remove (self.fields, table)
                
            elif i == 2:
                self.lt_nodes = self.lt_node_list (
                    self.entry, self.fields)
                self.lt_listvw = LT_Widget_1 (
                    self, i, self.dialogue)
                self.lt_detail = LT_Widget_2 (
                    self.notebook, i, self.dialogue)
                list_remove  (self.fields,
                      [x['key'] for x in self.lt_nodes])
            else:
                table = [x for x in self.fields if
                         Types.get_field(x).type != Fields.LongText]
                self.add_type1_widget (label, table, i)

        self.notebook.show ()
        return

    def add_type1_widget (self, label, table, pos):
        
        if len (table) == 0: return
        scroll = gtk.ScrolledWindow ()
        scroll.set_policy (gtk.POLICY_AUTOMATIC,
                           gtk.POLICY_AUTOMATIC)
        content = gtk.Table (1, len (table))
        scroll.add_with_viewport (content)

        j = 0
        for field in table:

            widget = FieldsInfo.widget (field) (self.entry, field, content, j)
            self.content.append (widget)
            
            widget.Subscribe ('apply', self.apply_cb)
            widget.Subscribe ('next', self.next_cb)
                
            j = j + 1

        label.show ()
        content.show ()
        scroll.show ()
            
        self.notebook.insert_page (scroll, label, pos)

    #--------------------------------------------------
    # Longtext stuff

    def lt_init (self, item, fields):

        self.lt_current = None
        self.lt_listvw = None 
        self.lt_detail = None

    def lt_update (self):
        self.lt_detail.update()
        modified = False
        for i in self.lt_nodes:
            modified |= i.get('modified', False)
            
        return modified
        
    def lt_prev (self):
        self.lt_display (self.lt_current - 1)

    def lt_next (self):
        self.lt_display (self.lt_current + 1) 

    def lt_display (self, pos):
        if self.lt_nodes:
            pos %= len(self.lt_nodes)
            self.lt_current = pos
            self.set_buttons (pos)
            self.lt_detail.display (self.lt_nodes[pos], self.entry)
        else:
            self.lt_current = None
            self.lt_detail.hide()

    def lt_new (self):
        d = LT_Dialog_1(parent = self.w.get_toplevel ())
        newname = d.run()
        if not newname:
            return
        new = {'key': newname.lower(), 'name': newname, 'mandatory': False}
        pos = len (self.lt_nodes)
        self.lt_nodes.append (new)
        assert self.lt_nodes[pos] == new
        self.set_buttons(len (self.lt_nodes) -1)
        self.entry[new['key']] = Fields.LongText('')
        self.lt_listvw.display_list (self.entry, self.lt_nodes)
        self.lt_display (pos)
        
    def lt_delete (self, pos):
        node = self.lt_nodes[pos]
        key = node ['key']
        del self.entry [key]
        self.lt_nodes.pop (pos)
        self.lt_listvw.display_list (self.entry, self.lt_nodes)
        self.lt_display (pos)
        try: self.fields.remove(key)
        except ValueError: pass
        
    def lt_node_list (self, item, fields):

        """Return a list of longtexts (annotations) associated
        with item """  
        fields = fields[:]
        nodes = []
        self.lt_list_add1 (item, nodes,
                          item.type.mandatory, {'mandatory': True})
        self.lt_list_add1 (item, nodes,
                          item.type.optional, {'mandatory': False})
        remaining = list_remove (fields, [ x['key'] for x in nodes])
        self.lt_list_add1 (
            item, nodes, [Types.get_field(x) for x in remaining],
            {'mandatory': False})
        return nodes

    def lt_list_add1 (self, item, nodes, fields, iv):
        """Accumulates """
        list2 = fields[:]
        for i in list2:
            if i.type == Fields.LongText:
                value = iv.copy()
                value['key'] =  i.name.lower()
                value['name'] = i.name
                value['type'] = i
                nodes.append (value)

    #--------------------------------------------------
    
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
                ui.gnome_error_dialog_parented (
                    _("Invalid key format"), self.w.get_toplevel ())
                return None

            key = Key.Key (database, key)

            if key != self.entry.key:
                if database.has_key (key):
                     ui.gnome_error_dialog_parented (
                         _("Key `%s' already exists") % str (key.key),
                         self.w.get_toplevel ())
                     return None
                
                self.entry.key = key
                modified = True
                
        modified = self.type != self.entry.type or modified
        
        for item in self.content:
            try:
                result = item.update (self.entry)
                
            except UnicodeError:
                f = Types.get_field (item.field)
                
                ui.gnome_error_dialog_parented (
                    _("The `%s' field contains a non Latin-1 symbol") %
                    f.name, self.w.get_toplevel ())
                return None
            
            if result == -1: return None
            
            modified = result or modified

        modified |= self.lt_update()

        if not modified:
            fields = self.entry.keys ()
            fields.sort ()

            if fields != self.fields: modified = 1
        
        if modified:
            return self.entry
        
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

        self.w = gtk.ScrolledWindow ()
        self.w.set_policy (gtk.POLICY_NEVER,
                           gtk.POLICY_AUTOMATIC)
        
        self.w_txt = gtk.TextView ()
        self.w_txt.set_editable (True)
        self.w_txt.set_wrap_mode (gtk.WRAP_WORD)
        
        self.w.add (self.w_txt)

        self.w_txt.show ()
        
        self.buff = self.w_txt.get_buffer ()

        iter = self.buff.get_start_iter ()
        mono = self.buff.create_tag ('body', family = 'Monospace')

        self.buff.insert_with_tags (
            iter, self.original.decode ('latin-1'), mono)
        return


    def update (self, database, entry):
        ''' updates and returns the new entry '''

        new  = None

        text = self.buff.get_text (
            self.buff.get_start_iter (),
            self.buff.get_end_iter ())
        try:
            text = text.encode ('latin-1')

        except UnicodeError:
            ui.gnome_error_dialog_parented (
                _("Your text contains non Latin-1 symbols"),
                self.w.get_toplevel ())
            return None

        try:
            new = self.database.create_native (text)
        except Exceptions.ParserError, msg:
            Utils.error_dialog (
                _("Error in native string parsing"), str (msg))
        return new

    
class Editor (Connector.Publisher):
    
    def __init__ (self, database, entry, parent = None, title = None):
        self.w = gtk.Dialog ()
        
        self.w.set_resizable (True)
        
        if title: self.w.set_title (title)
        else:     self.w.set_title (
            _("Edit entry") + ' [%s]' % str (entry.key) )
        
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
        self.close_bid = self.close_b.connect (
            'clicked', self.close_dialog)
        self.close_b.show ()

        # Use Escape to abort, Ctrl-Return to accept
        accelerator = gtk.AccelGroup ()
        self.w.add_accel_group (accelerator)

        self.close_b.add_accelerator (
            'clicked', accelerator, gtk.keysyms.Escape, 0, 0)
        self.apply_b.add_accelerator (
            'clicked', accelerator, gtk.keysyms.Return,
            gtk.gdk.CONTROL_MASK, 0)


        # for use with annotations
        self.del_b = gtk.Button(stock = gtk.STOCK_DELETE)
        self.del_b.connect ('clicked', self.del_cb, None)
        self.del_b.set_sensitive(False)
        self.w.action_area.add (self.del_b)
        self.new_b = gtk.Button (stock = gtk.STOCK_NEW)
        self.new_b.connect ('clicked', self.add_cb, None)
        self.new_b.set_sensitive(False)
        self.w.action_area.add (self.new_b)

        self.w.action_area.add (self.apply_b)
        if self.has_native: self.w.action_area.add (self.native_b)
        self.w.action_area.add (self.close_b)

        self.entry       = entry
        self.database    = database
        self.editor      = None

        # this is the working copy of the entry
        self.current     = copy.deepcopy (entry)
        
        # put the negated value, so that we can call
        # toggle to switch and create
        self.native_mode = not (self.has_native and Config.get (
            'gnome/native-as-default').data)

        self.toggle_native ()
        
        self.w.show_all ()
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
                self.native_b.get_children () [0].set_text (
                    _("Native Editing"))

            self.editor = RealEditor (self.database, self.current, self)
            
            ui_width  = Utils.config.get_int (
                '/apps/pybliographic/editor/width')  or -1
            ui_height = Utils.config.get_int (
                '/apps/pybliographic/editor/height') or -1

        else:
            if self.editor:
                cur = self.editor.update (self.database, self.current)

                if cur is None: return

                if not self.database.has_key (cur.key):

                    # We need to insert the entry as it is currently,
                    # in order to generate a Key
                    cur = self.database.add (cur)
                
                self.editor.w.destroy ()
                self.current = cur

            # native edition
            self.native_mode = True

            if self.has_native:
                self.native_b.get_children () [0].set_text (
                    _("Standard Editing"))
            
            self.editor = NativeEditor (self.database, self.current)

            ui_width  = Utils.config.get_int (
                '/apps/pybliographic/native/width')  or -1
            ui_height = Utils.config.get_int (
                '/apps/pybliographic/native/height') or -1


        self.editor.Subscribe ('apply', self.apply_changes)
        self.editor.Subscribe ('next',  self.next_item)
        
        self.w.vbox.pack_start (self.editor.w)

        # set window size
        if ui_width != -1 and ui_height != -1:
            self.w.set_default_size (ui_width, ui_height)
            self.w.resize (ui_width, ui_height)
        
        self.editor.w.show ()
        return

    def apply_changes (self, * arg):
        
        new = self.editor.update (self.database, self.current)
        if new:
            self.close_dialog ()
            if new is not self.entry:
                self.issue ('commit-edition', self.entry, new)
        return
    

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

    def add_cb (self, button, data):
        """Called when the add button is pressed"""

        if self.editor:
            self.editor.add_cb (button, data)

    def del_cb (self, button, data):
        """Called when the delete button is pressed"""

        if self.editor:
            self.editor.del_cb (button, data)


    def update_buttons (self, **argh):
        old = self.lt_callbacks
        self.callbacks.update(argh)  

        return old

    def set_buttons (self, **argh):
        self.callbacks = argh
        

    
    
        
#####################################################################

class LT_Widget_1:

    def __init__ (self, editor, position, dialogue):
        self.editor = editor
        self.notebook = editor.notebook
        self.entry = self.editor.entry
        self.dialogue = dialogue
        self.node = None
        
        self.page = gtk.ScrolledWindow ()
        self.label = gtk.Label (_('Notes'))
        self.page.set_policy (gtk.POLICY_AUTOMATIC,
                              gtk.POLICY_AUTOMATIC)
        self.display_list (self.entry, self.editor.lt_nodes)

        self.page.set_data ('pyblio-owner', self)
        self.page.show_all()
        self.notebook.insert_page (self.page, self.label, position)
        #list_remove (self.editor.fields, self.keys) 

        #self.enable_buttons()

    def display_list (self, entry, nodes):
        content = gtk.VBox()
        for i in range (len(nodes)):
            node = nodes[i]
            key = node['key'] 
            vbox =  gtk.VBox()
            anno_label = gtk.Label()
            anno_label.set_alignment (0, 0.5)
            if node.get('mandatory', False):
                l = '<b>%s</b>  <span color="red">%s</span>' %(
                    key, _('mandatory'))
            else:
                l = "<b>%s</b>" %(key)
            anno_label.set_markup(l)
            vbox.pack_start (anno_label)
            
            if entry.has_key(key): t = str (entry[key])
            else:                  t = ''

            l = min (len(t), 150)
            text_label = gtk.Label(t[0:l])
            text_label.set_line_wrap (True)
            text_label.set_size_request ( 500, 45) ##  XXX
            text_label.set_alignment (0.1, .2)
            vbox.pack_start (text_label)
            ebox = gtk.Button()
            ebox.add (vbox)
            ebox.connect ('clicked', self.lt_select_detail, i)
            content.pack_start(ebox, False, False)

        page_child = self.page.get_child()
        if page_child:
            self.page.remove (page_child)
        self.page.add_with_viewport (content)
        self.page.show_all()


    #------------------------------------------------------------
    #   Buttons

    def enable_buttons(self):
        """Sets and enables buttons for the longtext fields."""
        d = self.dialogue
        d.new_b.set_sensitive (True)

    def lt_select_detail (self, button, pos):
        self.editor.lt_display (pos)



class LT_Widget_2:

    def __init__ (self, notebook, position, dialogue):
        self.notebook = notebook
        self.position = position + 1
        self.dialogue = dialogue
        self.node = None
        self.page = gtk.ScrolledWindow()
        self.page.set_policy (gtk.POLICY_AUTOMATIC,
                              gtk.POLICY_AUTOMATIC)
        self.buff = gtk.TextBuffer()
        self.content = gtk.TextView(self.buff)
        self.label = gtk.Label()
        self.page.add(self.content)
        self.content.grab_focus()
        self.page.set_data ('pyblio-owner', self)
        self.content.set_wrap_mode (gtk.WRAP_WORD)
        self.buff.connect('changed', self.changed_cb)
        self.hidden = True
        
    def display (self, node, item):
        self.node = node
        self.entry = item
        self.label.set_text (node.get('name', _('Text')))
        key = node['key']
        if not item.has_key(key):
            item[key] = Fields.LongText(_('Enter text here'))
        self.buff.set_text (str(item[key]), -1)
        self.buff.set_modified (False)
        self.page.show_all ()
        if self.hidden:
            self.hidden = False
            self.notebook.insert_page (
                self.page, self.label, self.position)
        pos = self.notebook.page_num (self.page)
        self.notebook.set_current_page (self.position)

    def update (self):
        if self.node and self.buff.get_modified ():
            start, end = self.buff.get_bounds()
            
            key = self.node['key']
            text = self.buff.get_text (start, end)
            if text.strip():
                self.entry[key] = Fields.LongText(text)
            else:
                del self.entry [key]
            self.node.setdefault ('modified', True)
        
    def hide (self):
        if self.hidden:
            return
        pos = self.notebook.page_num (self.page)
        if pos == -1:
            print 'ERROR -- LT WIDGET 2: not in notebook'
            return
        self.node = None
        #self.disable_buttons()
        if not self.hidden:
            self.notebook.remove_page (pos)#position)
        self.hidden = True

    def changed_cb (self, *args):

        start, end = self.buff.get_bounds()
        key = self.node['key']
        self.entry[key].text = self.buff.get_text (start, end)
        

    def enable_buttons (self):
        """Add and enable buttons."""
        d = self.dialogue
        d.del_b.set_sensitive(True)

class  LT_Dialog_1     :

    def __init__ (self, parent=None):
        self.dialog = gtk.Dialog(
            _('New Annotation Name'), parent, 0,
            (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,
             gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT))
        self.dialog.vbox.set_border_width (24)
        self.dialog.vbox. pack_start (
            gtk.Label (
            _('Name of the new annotation:')),
            True, True, 6)
        menu = gtk.Menu()
        self.options = gtk.OptionMenu()
        self.options.set_menu(menu)
        self.dialog.vbox.pack_start (self.options, True, True, 12)
        self.fields = [ x for x in Config.get ('base/fields').data
                        if Types.get_field(x).type == Fields.LongText]
        self.fields.sort()
        for i in self.fields:
            menu.append(gtk.MenuItem(i))
        self.options.set_history(0)
        self.options.grab_focus()
        self.options.connect ('changed', self.changed)
        self.dialog.set_default_response(gtk.RESPONSE_ACCEPT)
        self.value = self.fields[0]

    def changed (self, *args):
        val = self.options.get_history()
        self.value = self.fields[val]

    def run (self):
        self.dialog.show_all()
        r = self.dialog.run()
        if r == gtk.RESPONSE_ACCEPT:
            name= self.value
        else:
            name = None
        self.dialog.destroy()
        return name


     
def list_remove (target, subtrahend):
    for k in subtrahend:
        try:
            target.remove(k)
        except ValueError:
            pass
    return target
