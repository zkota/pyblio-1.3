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

'''This module provides a dialog to configure the structure of the
bibliography '''

# TO DO:
# adapt menu item for this dialog
# cleaning up


import gobject, gtk

import copy, gettext, os, re, string

_ = gettext.gettext

from Pyblio import Config, Fields, Types, version
from Pyblio.GnomeUI import Utils

_typename = {
    Fields.AuthorGroup : _('Authors'),
    Fields.Text        : _('Text'),
    Fields.URL         : _('URL'),
    Fields.Reference   : _('Reference'),
    Fields.Date        : _('Date')
    }

class FieldsDialog:

    def __init__ (self, parent = None):

        gp = os.path.join (version.prefix, 'glade', 'fields1.glade')
        
        self.xml = gtk.glade.XML (gp, 'fields1')
        self.xml.signal_autoconnect (self)

        self.dialog = self.xml.get_widget ('fields1')
        self.w = self.xml.get_widget ('notebook')

        tooltips = gtk.Tooltips ()
        tooltips.enable ()
        
        #self.dialog.set_parent (parent) ####
        self.dialog.set_title (_("Entry types and field names configuration"))
        self.warning = 0
        self.parent = parent
        self.init_page_1()
        self.init_page_2()
        self.init_page_3()
        self.show()

        self.changed = 0
        return

    def show(self):
        self.dialog.show_all ()

    def on_close (self, w):
        self.dialog.hide_all()

    def on_add(self, *args):
        page = self.w.get_current_page ()
        if page == 0: self.page1_add (*args)
        elif page == 1: self.page2_add (*args)
        elif page == 2: self.page3_add (*args)
        
    def on_remove (self, *args):
        page = self.w.get_current_page()
        if page == 0: self.page1_rm (*args)
        elif page == 1: self.page2_rm (*args)
        elif page == 2: self.page3_rm (*args)

    def on_help (self, *args):
        print 'ON HELP:', args

    def check (self):
        if len(self.fields) != len(self.fm):
            print 'ERROR LEN OF FIELDS (%d) /= LEN OF FM (%)' %(
                len(self.fields), len(self.fm))
            import traceback
            traceback.print_tb()
            k = self.fields.keys()
            l = []
            for i in self.fm:
                j = i[2]
                l.append(j)
                try: k.remove(j)
                except KeyError:
                    print 'fieldname %s (%s) not in Keys' %(
                        j, i[0])
            if k:
                print 'keys %s unused' %(k)
    
    #------------------------------------------------------------
    # Page 1

    def init_page_1 (self):
        
        self.fields1 = self.xml.get_widget('f_list_1')
        rend = gtk.CellRendererText()
        col = gtk.TreeViewColumn(_('Name'), rend, text = 0)
        self.fields1.append_column(col)
        rend = gtk.CellRendererText()
        col = gtk.TreeViewColumn(_('Type'), rend, text = 1)
        self.fields1.append_column(col)
        
        self.fm = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING,
                                gobject.TYPE_STRING, gobject.TYPE_PYOBJECT)
        self.sfm = gtk.TreeModelSort(self.fm)
        self.sfm.set_sort_column_id(2, gtk.SORT_ASCENDING)
        self.fields1.set_model(self.sfm)
        self.s1 = self.fields1.get_selection()
        self.s1.connect ('changed', self.list_1_select)
        self.fields = copy.copy (Config.get ('base/fields').data)
        for key, item in  self.fields.iteritems():
            self.fm.append((item.name,
                            _typename [item.type], key, item)) 
        
        self.name1 = self.xml.get_widget('name1')
        self.menu1 = self.xml.get_widget('type1')
        menu = gtk.Menu ()
        self.menu1.set_menu (menu)
        self.menu_items = _typename.keys ()
        for item in self.menu_items:
            Utils.popup_add (menu, _typename [item], self.select_menu, item)
        self.menu1.set_history (0)
        self.current_menu = self.menu_items [0]
        self.check()

    def page1_add (self, *args):
        t = self.menu_items[0]
        description = Types.FieldDescription('')
        iter = self.fm.append((
            'new field', _typename[t], '_new field_',
            description))
        if iter:
            s_iter = self.sfm.convert_child_iter_to_iter(None, iter)
            s_path = self.sfm.get_path(s_iter)
            self.fields1.scroll_to_cell(s_path)
            self.s1.select_iter(s_iter)
            self.check()
            # Config save?
            
    def page1_rm (self, *args):
        m, iter = self.s1.get_selected()
        if iter:
            p = self.sfm.convert_iter_to_child_iter(None, iter)
            #print 'SELF:FM[P][2]:', self.fm[p] [2]
            try: del self.fields [self.fm[p][2]]
            except KeyError: pass
            self.fm.remove(p)
            Config.set_and_save('base/fields', self.fields)
            self.check()

    def list_1_select (self, sel):
        m, iter = sel.get_selected()
        if iter:
            p = self.sfm.convert_iter_to_child_iter(None, iter)
            data = self.fm[p]
            self.name1.set_text(self.fm[p][0])
            try:
                self.menu1.set_history (
                    self.menu_items.index(self.fm[p][3].type))
            except ValueError:
                print self.menu_items, self.fm[p][0], self.fm[p][2]

    def on_name1_changed (self, *args):
        sel = self.fields1.get_selection()
        m, iter = sel.get_selected()
        if iter:
            p = self.sfm.convert_iter_to_child_iter(None, iter)
            oldname = self.fm[p][2]
            newname = self.name1.get_text()
            try: del self.fields [oldname]
            except KeyError: pass
            self.fm[p] [0] = newname
            self.fm[p] [2] = newname.lower()
            self.fm[p] [3].name = newname
            self.fields [newname.lower()] = self.fm[p][3]
            self.check()
            self.change_fields()

    def on_type1_changed (self, *args):
        x = self.menu_items[self.menu1.get_history()]
        sel = self.fields1.get_selection()
        m, iter = sel.get_selected()
        if iter:
            p = self.sfm.convert_iter_to_child_iter(None, iter)
            #print 'TYP!', args, x, sel, m, iter
            self.fm[p] [1] = _typename[x]
            self.fm[p] [3].type = x
            self.change_fields()
            self.check()


    #------------------------------------------------------------
    # Page 2

    def init_page_2 (self):
                # PAGE 2

        self.entries2 = self.xml.get_widget('e_list_2')
        self.em = gtk.ListStore(gobject.TYPE_STRING,
                                gobject.TYPE_PYOBJECT,
                                gobject.TYPE_STRING )
        self.entries = copy.copy (Config.get ('base/entries').data)
        for i in self.entries.itervalues():
            self.em.append ((i.name, i, i.name.lower()))
        self.sem = gtk.TreeModelSort(self.em)
        self.sem.set_sort_column_id(2, gtk.SORT_ASCENDING)
        self.entries2.set_model(self.sem)
        rend = gtk.CellRendererText()
        col = gtk.TreeViewColumn(_('Entry type'), rend, text = 0)
        self.entries2.append_column(col)
        self.name2 = self.xml.get_widget('name2')
        self.s2 = self.entries2.get_selection()
        self.s2.connect('changed', self.elist_select)
        self.check()

    def page2_add (self, *args):
        description = Types.EntryDescription('NEW')
        iter = self.em.append(('NEW', description, 'new'))
        if iter:
            s_iter = self.sem.convert_child_iter_to_iter(None, iter)
            s_path = self.sem.get_path(s_iter)
            self.entries2.scroll_to_cell(s_path)
            self.s2.select_iter(s_iter)
            self.entries [self.em[iter][2]] = self.em[iter][1]
            self.check()

    def page2_rm (self, *args):
        self.check()
        m, iter = self.s2.get_selected()
        if iter:
            p = self.sem.convert_iter_to_child_iter(None, iter)
            del self.entries [self.em[p] [2]]
            self.em.remove(p)
            Config.set_and_save('base/entries', self.entries)
            self.check()

    def elist_select (self, sel):
        self.list_2_select(sel)

    def list_2_select (self, sel):
        m, iter = sel.get_selected()
        if iter:
            p = self.sem.convert_iter_to_child_iter(None, iter)
            self.name2.set_text (self.em[p] [0])
            self.page3_setup (self.em[p] [1])
        self.check()

    def on_name2_changed (self, *args):
        sel = self.entries2.get_selection()
        m, iter = sel.get_selected()
        if iter:
            p = self.sem.convert_iter_to_child_iter(None, iter)
            newname = self.name2.get_text()
            try: del self.entries [self.em[p][2]]
            except KeyError: print 'Keyerror', self.em[
                p] [2], self.entries.keys()
            self.em[p][1].name = newname
            self.em[p][0] = newname
            self.em[p][2] = newname.lower()
            self.entries[newname.lower()] = self.em[p][1]
            Config.set_and_save ('base/entries', self.entries)
        self.check()
        #print self.entries.keys()

    #------------------------------------------------------------
    # Page 3

    def init_page_3 (self):
        
        self.flist3a = self.xml.get_widget ('f_list_3a')
        self.flist3a.set_model (self.sfm)       
        rend = gtk.CellRendererText()
        col = gtk.TreeViewColumn(_('Available'), rend, text = 0)
        self.flist3a.append_column(col)
        self.s3a = self.flist3a.get_selection()
        self.label3 = self.xml.get_widget ('entry_type_label')
        self.flist3b = self.xml.get_widget ('f_list_3b')
        rend = gtk.CellRendererToggle()
        rend.connect('toggled', self.toggle_mandatory)
        col = gtk.TreeViewColumn('X', rend, active = 1)
        self.flist3b.append_column(col)
        rend = gtk.CellRendererText()
        col = gtk.TreeViewColumn(_('Associated'), rend, text = 2)
        self.flist3b.append_column(col)
        self.sm = gtk.ListStore(gobject.TYPE_STRING,
                                gobject.TYPE_BOOLEAN,
                                gobject.TYPE_STRING,
                                gobject.TYPE_PYOBJECT)
        self.ssm = gtk.TreeModelSort(self.sm)
        self.ssm.set_sort_column_id(0, gtk.SORT_ASCENDING)
        self.flist3b.set_model(self.ssm)
        self.s3b = self.flist3b.get_selection()
        self.label3.set_markup (
            _('Please, select an entry type from previous page.' ))
        self.check()

    def page3_setup (self, item):
        self.sm.clear()
        self.current_entry = item
        for i in item.mandatory:
             self.sm.append((i.name, True, i.name, i))
        for i in item.optional:
             self.sm.append((i.name, False, i.name, i))
        self.label3.set_markup (
            _('Fields associated with <b>%s</b> entry type' %(
            item.name)))
        self.check()

    def page3_add (self, *args):
        m, iter = self.s3a.get_selected()
        if iter:
            p = self.sfm.convert_iter_to_child_iter(None, iter)
            field = self.fm[p] [3]
            self.current_entry.optional.append(field)
            self.sm.append ((field.name, False, field.name, field))
            Config.set_and_save('base/entries', self.entries)
        self.check()

    def page3_rm (self, *args):
        m, iter = self.s3b.get_selected()
        if iter:
            p = self.ssm.convert_iter_to_child_iter (None, iter)
            field = self.sm[p] [3]
            if self.sm[p] [1]:
                self.current_entry.mandatory.remove(field)
            else:
                self.current_entry.optional.remove(field)
            del self.sm [p]
            Config.set_and_save('base/entries', self.entries)
        self.check()

    def toggle_mandatory (self, rend, path):
        p = self.ssm.convert_path_to_child_path(path)
        iter = self.sm.get_iter(p)
        field = self.sm[iter][3]
        x = self.sm.get_value (iter, 1)
        self.sm.set_value(iter, 1, not x)
        if x:
            self.current_entry.mandatory.remove(field)
            self.current_entry.optional.append(field)
        else:
            self.current_entry.optional.remove(field)
            self.current_entry.mandatory.append(field)
        self.entries [self.current_entry.name.lower()] = self.current_entry
        Config.set_and_save ('base/entries', self.entries)
        self.check()

    def select_menu (self, w, data):
        self.current_menu = data
        return

    def change_fields (self, item=None):
        Config.set_and_save('base/fields', self.fields)
        

    def set (self, data):
        self.list.freeze ()
        self.list.clear ()
        self.data = data
        keys = self.data.keys ()
        keys.sort ()
        for key in keys:
            item = self.data [key]
            self.list.append ((item.name, _typename [item.type]))
            self.list.set_row_data (self.list.rows - 1, item)
        self.list.thaw ()
        pass


    def get (self):
        return self.data


    def select_row (self, widget, row, col, event):
        item = self.list.get_row_data (row)
        self.name.set_text (item.name)
        self.menu1.set_history (self.menu_items.index (item.type))
        self.current_menu = item.type
        return


    def apply (self, * arg):
        if not self.changed: return
        
        result = self.get ()
        
        Config.set_and_save ('base/fields', result)

        if self.parent:
            self.parent.warning (_("Some changes require to restart Pybliographic\n"
                                   "to be correctly taken into account"))
        return


    def add_cb (self, * arg):
        name = string.strip (self.name.get_text ())
        if name == '': return

        table = self.get ()
        field = Types.FieldDescription (name, self.current_menu)
        table [string.lower (name)] = field
        self.set (table)

        self.changed = 1
        return


    def remove_cb (self, * arg):
        selection = self.list.selection
        if not selection: return

        selection = selection [0]
        item = self.list.get_row_data (selection)
        table = self.get ()
        del table [string.lower (item.name)]
        self.set (table)

        self.changed = 1
        return


_status = (
    '',
    _("Mandatory"),
    _("Optional")
    )

__fields_object = None

def run (w):
    global __fields_object
    if __fields_object:
        __fields_object.show()
    else:
        __fields_object = FieldsDialog(w)

