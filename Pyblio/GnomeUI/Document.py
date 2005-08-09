# -*- coding: utf-8 -*-
#
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

''' This module defines a Document class '''

import gobject

from gnome import ui

import gnome
import gtk
import gtk.glade

from gtk import gdk

from Pyblio.GnomeUI import Index, Entry, Utils, FileSelector, Editor
from Pyblio.GnomeUI import Search, Format
from Pyblio.GnomeUI.Sort import SortDialog
from Pyblio.GnomeUI.Medline import MedlineUI

from Pyblio import Connector, Open, Exceptions, Selection, Sort, Base, Config
from Pyblio import version, Fields, Types, Query

import Pyblio.Style.Utils

import os, string, copy, types, sys, traceback, stat

import cPickle as pickle

printable = string.lowercase + string.uppercase + string.digits


uim_content = '''
<ui>
    <menubar name="Menubar">
        <menu action="File">
             <menuitem action="New"/>
             <menuitem action="Open"/>
             <menuitem action="Merge"/>
             <menuitem action="Medline"/>
             <menuitem action="Save"/>
             <menuitem action="Save_As"/>
             <separator/>
             <menu action="Recent">
                <placeholder name="Previous"/>
             </menu>
             <separator/>
             <menuitem action="Close"/>
             <menuitem action="Quit"/>
        </menu>
        <menu action="EditMenu">
             <menuitem action="Cut"/>
             <menuitem action="Copy"/>
             <menuitem action="Paste"/>
             <menuitem action="Clear"/>
             <separator/>
             <menuitem action="Add"/>
             <menuitem action="Edit"/>
             <menuitem action="Delete"/>
             <separator/>
             <menuitem action="Find"/>
             <menuitem action="Sort"/>
        </menu>
        <menu action="CiteMenu">
             <menuitem action="Cite"/>
             <menuitem action="Format"/>
        </menu>
        <menu action="Settings">
             <menuitem action="Fields"/>
             <menuitem action="Preferences"/>
             <separator/>
             <menuitem action="Forget"/>
        </menu>
        <menu action="HelpMenu">
             <menuitem action="Contents"/>
             <menuitem action="About"/>
        </menu>
    </menubar>

    <toolbar name="Toolbar">
        <toolitem action="Open"/>
        <toolitem action="Save"/>
        <separator/>
        <toolitem action="Add"/>
        <separator/>
        <toolitem action="Find"/>
        <toolitem action="Cite"/>
    </toolbar>
    
    <popup name="Popup">
         <menuitem action="Add"/>
         <menuitem action="Edit"/>
         <menuitem action="Delete"/>
    </popup>
</ui>
'''

class Document (Connector.Publisher):
    
    def __init__ (self, database):

        self.uim = gtk.UIManager ()

        self.recents = None
        
        self.actiongroup = gtk.ActionGroup ('Main')
        
        self.actiongroup.add_actions ([
            # id     stock            label         accel   tooltip   callback
            ('File', None,            _('_File')),
            ('EditMenu', None,            _('_Edit')),
            ('CiteMenu', None,            _('_Cite')),
            ('Settings', None,        _('_Settings')),
            ('HelpMenu', None, _('_Help')),
            ('Recent', None, _('Recent documents')),
            
            ('New',  gtk.STOCK_NEW,   None,         None,   None,     self.new_document),
            ('Open', gtk.STOCK_OPEN,  None,         None,   None,     self.ui_open_document),
            ('Save', gtk.STOCK_SAVE,  None,         None,   None,     self.save_document),
            ('Save_As', gtk.STOCK_SAVE_AS,  None,         None,   None,     self.save_document_as),
            ('Close', gtk.STOCK_CLOSE,  None,         None,   None,     self.close_document),
            ('Quit', gtk.STOCK_QUIT,  None,         None,   None,     self.exit_application),

            ('Merge',   None, _('Merge With...'),    '<control>g',  None, self.merge_database),
            ('Medline', None, _('Medline Query...'), '<control>m',  None, self.query_database),



            ('Cut', gtk.STOCK_CUT,  None,         None,   None,     self.cut_entry),
            ('Copy', gtk.STOCK_COPY,  None,         None,   None,     self.copy_entry),
            ('Paste', gtk.STOCK_PASTE,  None,         None,   None,     self.paste_entry),
            ('Clear', gtk.STOCK_CLEAR,  None,         None,   None,     self.clear_entries),
            ('Add', gtk.STOCK_ADD,  None,         None,   None,     self.add_entry),
            ('Delete', gtk.STOCK_DELETE,  None,         None,   None,     self.delete_entry),
            ('Find', gtk.STOCK_FIND,  None,         None,   None,     self.find_entries),
            
            ('Sort', None, _('S_ort...'), None,  None, self.sort_entries),
            ('Cite', gtk.STOCK_JUMP_TO,   _('Cite...'), None,  None, self.lyx_cite),
            ('Format', gtk.STOCK_EXECUTE, _('Format...'), None,  None, self.format_entries),

            ('Fields', None, _('Fields...'), None,  None, self.set_fields),
            ('Preferences', gtk.STOCK_PREFERENCES,  None,         None,   None,     self.set_preferences),
            ('Forget', None, _('Forget all changes'),     None,   None,     self.forget_changes_cb),
            
            ('Contents', gtk.STOCK_HELP, None,   None,   None,     self.on_documentation),
            ])

        if gtk.pygtk_version >= (2,6,0):
            self.actiongroup.add_actions ([
                ('About', gtk.STOCK_ABOUT, None,   None,   None,     self.about),
                ('Edit', gtk.STOCK_EDIT,  None,         None,   None,     self.edit_entry),
                ])

        else:
            self.actiongroup.add_actions ([
                ('About', None, _('_About'),   None,   None,     self.about),
                ('Edit', None,  _('_Edit'),    None,   None,     self.edit_entry),
                ])
            
        prev = self.actiongroup.get_action ('Recent')
        
        prev.set_property ('is-important', True)
        prev.set_property ('hide-if-empty', False)
        
        self.uim.insert_action_group (self.actiongroup, 0)
        self.uim.add_ui_from_string (uim_content)

        self.uim.ensure_update ()

        
        gp = os.path.join (version.pybdir, 'glade', 'pyblio.glade')
        
        self.xml = gtk.glade.XML (gp, 'main', domain = 'pybliographer')
        self.xml.signal_autoconnect (self)

        self.w = self.xml.get_widget ('main')
        self.paned = self.xml.get_widget ('main_pane')

        self.w.set_menus (self.uim.get_widget ('/Menubar'))
        self.w.set_toolbar (self.uim.get_widget ('/Toolbar'))
        
        self.w.add_accel_group (self.uim.get_accel_group ())

        self.w.add_events (gdk.KEY_PRESS_MASK)
        
        self.w_save_btn = self.xml.get_widget ('_w_save_btn')
        self.w_save_mnu = self.xml.get_widget ('_w_save_mnu')
        
        # The Index list
        self.index = Index.Index ()
        self.paned.add1 (self.index.w)
        
        self.index.Subscribe ('new-entry',      self.add_entry)
        self.index.Subscribe ('edit-entry',     self.edit_entry)
        self.index.Subscribe ('delete-entry',   self.delete_entry)
        self.index.Subscribe ('select-entry',   self.update_display)
        self.index.Subscribe ('select-entries', self.freeze_display)
        self.index.Subscribe ('drag-received',  self.drag_received)
        self.index.Subscribe ('drag-moved',     self.drag_moved)
        self.index.Subscribe ('click-on-field', self.sort_by_field)

        self.paned.show_all ()

        # The text area
        self.display = Entry.Entry ()
        self.paned.add2 (self.display.w)

        # Status bar
        self.statusbar = self.xml.get_widget ('statusbar')
        
        # set window size
        ui_width  = Utils.config.get_int ('/apps/pybliographic/ui/width') or -1
        ui_height = Utils.config.get_int ('/apps/pybliographic/ui/height') or -1

        if ui_width != -1 and ui_height != -1:
            self.w.set_default_size (ui_width, ui_height)

        # set paned size
        paned_height = Utils.config.get_int ('/apps/pybliographic/ui/paned') or -1
        self.paned.set_position (paned_height)
        
        self.w.show_all ()
        
        # application variables
        self.data      = database
        self.selection = Selection.Selection ()
        self.search_dg = None
        self.sort_dg   = None
        self.lyx       = None
        self.changed   = 0
        self.directory = None

        self.incremental_start  = None
        self.incremental_search = ''
        
        self.modification_date = None

        # for autosave
        self.source_id = None

        # set the default sort method
        default = Utils.config.get_string ('/apps/pybliographic/sort/default')
        if default is not None: default = pickle.loads (default)

        self.sort_view (default)

        self._title_set ()
        self._set_edit_actions (False)
        return

    def _title_set (self):
        
        if self.data.key is None:
            self.w.set_title (_('Unnamed bibliographic database'))
            return

        name = os.path.basename (self.data.key.url [2])
        
        self.w.set_title (name)
        return
        

    def set_preferences (self, * arg):
        from Pyblio.GnomeUI import Config
        Config.run(self.w)
        return

    def set_fields (self, * arg):
        from Pyblio.GnomeUI import Fields
        Fields.run (self.w)
        return
    
    def forget_changes_cb (self, * arg):
        Config.forget_changes()
        return
    

    def update_history (self, history):
        ''' fill the " Previous Documents " menu with the specified list of documents '''

        if self.recents:
            for mid in self.recents_mid:
                self.uim.remove_ui (mid)
                
            self.uim.remove_action_group (self.recents)

        self.recents_mid = []
        self.recents = gtk.ActionGroup ('Recent')

        self.uim.insert_action_group (self.recents, 1)

        for item in history:
            # Display name in the menu
            quoted   = string.replace (item [0], '_', '__')
        
            mid = self.uim.new_merge_id ()

            self.recents_mid.append (mid)
            
            action = gtk.Action (str (mid), quoted, None, None)
            self.recents.add_action (action)

            action.connect ('activate', self._history_open_cb, item)
        
            self.uim.add_ui (mid, '/Menubar/File/Recent', str (mid),
                             str (mid), gtk.UI_MANAGER_MENUITEM, False)

        return


    def _history_open_cb (self, id, w):

        file, type = w
        
        if not self.confirm (): return

        self.open_document (file, type)
        return
    
    
    def redisplay_index (self, changed = -1):
        ''' redisplays the index. If changed is specified, set the
        self.changed status to the given value '''
        
        if changed != -1:
            self.changed = changed

        self.index.display (self.selection.iterator (self.data.iterator ()))
        
        self.update_status ()
        return


    def format_query (self, style, format, output):
        try:
            file = open (output, 'w')
        except IOError, err:
            self.w.error (_("can't open file `%s' for writing:\n%s")
                          % (output, str (err)))
            return
        
        entries = map (lambda x: x.key, self.index.selection ())
        
        if not entries:
            iter    = self.selection.iterator (self.data.iterator ())
            entries = []
            
            e = iter.first ()
            while e:
                entries.append (e.key)
                e = iter.next ()

        url = Fields.URL (style)

        try:
            Pyblio.Style.Utils.generate (url, format, self.data, entries, file)
        except RuntimeError, err:
            print err
            self.w.error (_("Error while parsing `%s':\n%s") % (style, err))
        return


    def format_entries (self, * arg):
        format_dg = Format.FormatDialog (self.w)
        format_dg.Subscribe ('format-query', self.format_query)
        return

    
    def update_status (self, status = -1):
        ''' redisplay status bar according to the current status '''

        if status != -1: self.changed = status
        
        if self.data.key is None:
            text = _("New database")
        else:
            text = str (self.data.key)

        li = len (self.index)
        ld = len (self.data)
        
        if li == ld:
            if   ld == 0: num = _("[no entry]")
            elif ld == 1: num = _("[1 entry]")
            else:         num = _("[%d entries]")    %  ld
        else:
            if   ld == 0: num = _("[no entry]")
            elif ld == 1: num = _("[%d/1 entry]")    % li
            else:         num = _("[%d/%d entries]") % (li, ld)

        text = text + ' ' + num
        
        if self.changed:
            text = text + ' ' + _("[modified]")

        if self.selection.search:
            text += ' - ' + _('view limited to: %s') % self.selection_name

        self.actiongroup.get_action ('Save').set_property ('sensitive', self.changed)

        self.statusbar.set_default (text)
        return

    
    def confirm (self):
        ''' eventually ask for modification cancellation '''
        
        if self.changed:
            return Utils.Callback (_("The database has been modified.\nDiscard changes ?"),
                                   self.w).answer ()
        
        return 1

        
    def new_document (self, * arg):
        ''' callback corresponding to the "New Document" button '''
        
        self.issue ('new-document', self)
        return


    def query_database (self, * arg):
        ''' callback corresponding to the "Medline Query..." button '''

        if not self.confirm (): return

        data = MedlineUI (self.w).run ()
        if data is None: return
        
        url = apply (Query.medline_query, data)

        if url is None:
            # no result.
            self.w.error (_("Your query returned no result"))
            return
        
        self.open_document (url, 'medline', no_name = True)
        return


    def merge_database (self, * arg):
        ''' add all the entries of another database to the current one '''
        # get a new file name
        (url, how) = FileSelector.URLFileSelection (_("Merge file"),
                                                    url = True, has_auto = True).run ()

        if url is None: return

        try:
            iterator = Open.bibiter (url, how = how)
            
        except (Exceptions.ParserError,
                Exceptions.FormatError,
                Exceptions.FileError), error:
            
            Utils.error_dialog (_("Open error"), error,
                                parent = self.w)
            return

        # loop over the entries
        errors = []
        try:
            entry = iterator.first ()
        except Exceptions.ParserError, msg:
            errors = errors + msg.errors
        
        while entry:
            self.data.add (entry)
            while 1:
                try:
                    entry = iterator.next ()
                    break
                except Exceptions.ParserError, msg:
                    errors = errors + list (msg.errors)
                    continue

        self.redisplay_index (1)

        if errors:
            Utils.error_dialog (_("Merge status"), string.join (errors, '\n'),
                                parent = self.w)
        return

        
    def ui_open_document (self, * arg):
        ''' callback corresponding to "Open" '''
        
        if not self.confirm (): return

        # get a new file name
        (url, how) = FileSelector.URLFileSelection (_("Open file")).run ()

        if url is None: return
        self.open_document (url, how)
        return

    
    def open_document (self, url, how = None, no_name = False):

        Utils.set_cursor (self.w, 'clock')

        orig_url = Fields.URL (url)
        url = str (orig_url)

        restore = False

        if orig_url.url [0] == 'file':

            name = orig_url.url [2]
            auto_save = os.path.join (os.path.dirname (name),
                            'x-pyblio-save-' + os.path.basename (name))

            if os.path.exists (auto_save):
                mod_date = os.stat (name) [stat.ST_MTIME]
                mod_date_auto = os.stat (auto_save) [stat.ST_MTIME]
                if mod_date < mod_date_auto:
                    restore = Utils.Callback (_("An autosave file was found which is newer than the original file.\nDo you want to restore it?"), self.w).answer ()

                    if restore: url = auto_save


        try:
            data = Open.bibopen (url, how = how)
            
        except (Exceptions.ParserError,
                Exceptions.FormatError,
                Exceptions.FileError), error:
            
            Utils.set_cursor (self.w, 'normal')
            Utils.error_dialog (_("Open error"), error,
                                parent = self.w)
            return


        # remove the old autosave object
        if self.data.key is not None and self.source_id:
            gobject.source_remove (self.source_id)

        # remove old autosave file if exists
        if self.data.key:
            if self.data.key.url [0] == 'file':
                old_file = self.data.key.url [2]
                old_auto_save = os.path.join (os.path.dirname (old_file),
                                'x-pyblio-save-' + os.path.basename (old_file))

                if os.path.exists (old_auto_save):
                    try:
                        os.remove (old_auto_save)
                    except (OSError, IOError), error:
                        Utils.set_cursor (self.w, 'normal')
                        self.w.error (_("Unable to remove autosave file `%s':\n%s") % (str (old_auto_save), str (error)))
                        return


        Utils.set_cursor (self.w, 'normal')

        if no_name: data.key = None
        
        self.data    = data


        if restore:

            # restore the original url internally,
            # and change the document status
            self.data.key = orig_url
            self.redisplay_index (1)

        else:
            self.redisplay_index (0)
        

        self._title_set ()

        # eventually warn interested objects
        self.issue ('open-document', self)

        # create autosave object if needed
        if Config.get ('base/autosave').data:
    	    savetimeout = Config.get ('base/autosave interval').data
            self.source_id = gobject.timeout_add (savetimeout * 60 * 1000, self.autosave, url, self.data.id)

        return


    def autosave (self, url, how):
        ''' autosave file as x-pyblio-save-filename '''

        if self.data.key.url [0] != 'file': return False

        name = self.data.key.url [2]

        # create an autosave file
        save = os.path.join (os.path.dirname (name),
                            'x-pyblio-save-' + os.path.basename (name))

        if self.changed:

            try:
                savefile = open (save, 'w')
            except (IOError, OSError), error:
                self.w.error (_("Error during autosaving:\n%s") % error [1])
                return False

            iterator = Selection.Selection (sort = self.selection.sort)
            Open.bibwrite (iterator.iterator (self.data.iterator ()),
                           out = savefile, how = how)

            savefile.close ()

        return True

    
    def save_document (self, * arg):
        if self.data.key is None:
            self.save_document_as ()
            return

        file = self.data.key.url [2]
        
        if self.modification_date:
            mod_date = os.stat (file) [stat.ST_MTIME]
            
            if mod_date > self.modification_date:
                if not Utils.Callback (_("The database has been externally modified.\nOverwrite changes ?"),
                                       self.w).answer ():
                    return
        
        Utils.set_cursor (self.w, 'clock')
        try:
            try:
                self.data.update (self.selection.sort)
            except (OSError, IOError), error:
                Utils.set_cursor (self.w, 'normal')
                self.w.error (_("Unable to save `%s':\n%s") % (str (self.data.key),
                                                               str (error)))
                return
        except:
            etype, value, tb = sys.exc_info ()
            traceback.print_exception (etype, value, tb)
            
            Utils.set_cursor (self.w, 'normal')
            self.w.error (_("An internal error occured during saving\nTry to Save As..."))
            return

        Utils.set_cursor (self.w, 'normal')

        # get the current modification date
        self.modification_date = os.stat (file) [stat.ST_MTIME]
        
        self.update_status (0)
        return
    
    
    def save_document_as (self, * arg):
        # get a new file name
        (url, how) = FileSelector.URLFileSelection (_("Save As..."),
                                                    url = False, has_auto = False, is_save = True).run ()
        
        if url is None: return

        if os.path.exists (url):
            if not Utils.Callback (_("The file `%s' already exists.\nOverwrite it ?")
                                   % url, parent = self.w).answer ():
                return

        try:
            file = open (url, 'w')
        except IOError, error:
            self.w.error (_("During opening:\n%s") % error [1])
            return

        Utils.set_cursor (self.w, 'clock')

        iterator = Selection.Selection (sort = self.selection.sort)
        Open.bibwrite (iterator.iterator (self.data.iterator ()),
                       out = file, how = how)
        file.close ()

        # remove the old autosave object
        if self.data.key is not None and self.source_id:
            gobject.source_remove (self.source_id)

        # remove old autosave file
        if self.data.key:
            if self.data.key.url [0] == 'file':
                old_file = self.data.key.url [2]
                old_auto_save = os.path.join (os.path.dirname (old_file),
                                'x-pyblio-save-' + os.path.basename (old_file))

                if os.path.exists (old_auto_save):
                    try:
                        os.remove (old_auto_save)
                    except (OSError, IOError), error:
                        Utils.set_cursor (self.w, 'normal')
                        self.w.error (_("Unable to remove autosave file `%s':\n%s") % (str (old_auto_save), str (error)))
                        return

        
        try:
            self.data = Open.bibopen (url, how = how)
                
        except (Exceptions.ParserError,
                Exceptions.FormatError,
                Exceptions.FileError), error:
                    
            Utils.set_cursor (self.w, 'normal')
            Utils.error_dialog (_("Reopen error"), error,
                                parent = self.w)
            return
            
        self.redisplay_index ()
        self._title_set ()

        self.issue ('open-document', self)
            
        Utils.set_cursor (self.w, 'normal')

        self.update_status (0)

        # create the new autosave object if needed
        if Config.get ('base/autosave').data:
            savetimeout = Config.get ('base/autosave interval').data
            self.source_id = gobject.timeout_add (savetimeout * 60 * 1000, self.autosave, url, self.data.id)

        return

    
    def close_document (self, * arg):
        self.issue ('close-document', self)
        return 1

    def close_or_exit (self, * arg):
        self.issue ('close-document', self, True)
        return 1


    def close_document_request (self):
        answer = self.confirm ()
        # remove autosave object with closing
        if answer and self.source_id:
            gobject.source_remove (self.source_id)

        # remove old autosave file
        if answer and self.data.key:
            if self.data.key.url [0] == 'file':
                old_file = self.data.key.url [2]
                old_auto_save = os.path.join (os.path.dirname (old_file),
                                'x-pyblio-save-' + os.path.basename (old_file))

                if os.path.exists (old_auto_save):
                    try:
                        os.remove (old_auto_save)
                    except (OSError, IOError), error:
                        Utils.set_cursor (self.w, 'normal')
                        self.w.error (_("Unable to remove autosave file `%s':\n%s") % (str (old_auto_save), str (error)))
                        return

        return answer

    
    def exit_application (self, * arg):
        self.issue ('exit-application', self)
        return


    def drag_moved (self, entries):
        if not entries: return
        
        for e in entries:
            del self.data [e.key]

        self.redisplay_index (1)
        return

    
    def drag_received (self, entries):
        for entry in entries:
            
            if self.data.would_have_key (entry.key):
                if not Utils.Callback (_("An entry called `%s' already exists.\nRename and add it anyway ?")
                                       % entry.key.key, parent = self.w).answer ():
                    continue
                
            self.changed = 1
            self.data.add (entry)

        self.redisplay_index ()
        self.index.set_scroll (entries [-1])
        return

                
    def cut_entry (self, * arg):
        entries = self.index.selection ()
        if not entries: return
        
        self.index.selection_copy (entries)
        for entry in entries:
            del self.data [entry.key]
            
        self.redisplay_index (1)
        pass

    
    def copy_entry (self, * arg):
        self.index.selection_copy (self.index.selection ())
        return

    
    def paste_entry (self, * arg):
        self.index.selection_paste ()
        return

    
    def clear_entries (self, * arg):
        if len (self.data) == 0: return

        if not Utils.Callback (_("Really remove all the entries ?"),
                               parent = self.w).answer ():
            return

        keys = self.data.keys ()
        for key in keys:
            del self.data [key]

        self.redisplay_index (1)
        return
    
    
    def select_all_entries (self, * arg):
        self.index.select_all ()
        return
    
    
    def add_entry (self, * arg):
        entry = self.data.new_entry (Config.get ('base/defaulttype').data)
        
        edit = Editor.Editor (self.data, entry, self.w, _("Create new entry"))
        edit.Subscribe ('commit-edition', self.commit_edition)
        return

    
    def edit_entry (self, entries):
        if not (type (entries) is types.ListType):
            entries = self.index.selection ()
        
        l = len (entries)

        if l == 0: return
        
        if l > 5:
            if not Utils.Callback (_("Really edit %d entries ?") % l):
                return

        for entry in entries:
            edit = Editor.Editor (self.data, entry, self.w)
            edit.Subscribe ('commit-edition', self.commit_edition)

        return


    def commit_edition (self, old, new):
        ''' updates the database and the display '''

        if old.key != new.key:
            if self.data.has_key (old.key):
                del self.data [old.key]

        if new.key:
            self.data [new.key] = new
        else:
            self.data.add (new)

        self.freeze_display (None)

        self.redisplay_index (1)
        self.index.select_item (new)
        return
    
    
    def delete_entry (self, * arg):
        ''' removes the selected list of items after confirmation '''
        entries = self.index.selection ()
        l = len (entries)
        if l == 0: return

        offset = self.index.get_item_position (entries [-1])

        if l > 1:
            question = _("Remove all the %d entries ?") % len (entries)
        else:
            question = _("Remove entry `%s' ?") % entries [0].key.key
            
        if not Utils.Callback (question,
                               parent = self.w).answer ():
            return

        for entry in entries:
            del self.data [entry.key]
            
        self.redisplay_index (1)
        self.index.select_item (offset)
        return
    
    
    def find_entries (self, * arg):
        if self.search_dg is None:
            self.search_dg = Search.SearchDialog (self.w)
            self.search_dg.Subscribe ('search-data', self.limit_view)
        else:
            self.search_dg.show ()
        return


    def limit_view (self, name, search):
        self.selection.search = search
        self.selection_name = name
        self.redisplay_index ()
        return

    
    def sort_entries (self, * arg):
        sort_dg = SortDialog (self.selection.sort, self.w)
        sort_dg.Subscribe ('sort-data', self.sort_view)
        return


    def sort_view (self, sort):
        self.selection.sort = sort
        self.redisplay_index ()
        return
    

    def sort_by_field (self, field):
        if field == '-key-':
            mode = Sort.KeySort ()
        elif field == '-type-':
            mode = Sort.TypeSort ()
        else:
            mode = Sort.FieldSort (field)

        # Check if we are toggling or changing
        cur = self.selection.sort
        
        if cur and len (cur.fields) == 1:
            cur = cur.fields [0]

            # We are still filtering according to the same field,
            # simply toggle the direction
            if cur == mode:
                mode.ascend = - cur.ascend
            
        self.selection.sort = Sort.Sort ([mode])
        self.redisplay_index ()
        return


    def lyx_cite (self, * arg):

        import locale

        try:
            enc = locale.getpreferredencoding ()

        except AttributeError:
            enc = locale.getdefaultlocale()[1]

        
        entries = self.index.selection ()
        if not entries: return
        
        if self.lyx is None:
            from Pyblio import LyX

            try:
                self.lyx = LyX.LyXClient ()
            except IOError, msg:
                msg = msg [1].decode (enc)
                self.w.error (_("Can't connect to LyX:\n%s") % msg)
                return

        keys = string.join (map (lambda x: x.key.key, entries), ', ')
        try:
            self.lyx ('citation-insert', keys)
        except IOError, msg:
            msg = msg [1].decode (enc)
            self.w.error (_("Can't connect to LyX:\n%s") % msg)
        return
    

    def _set_edit_actions (self, value):
        for action in ('Delete', 'Edit', 'Cut', 'Copy', 'Cite'):
            self.actiongroup.get_action (action).set_property ('sensitive', value)
        
        return
        
    def update_display (self, entry):
        if entry:
            self.display.display (entry)

        self._set_edit_actions (entry is not None)
        return

    
    def freeze_display (self, entry):
        self.display.clear ()
        self._set_edit_actions (True)
        return


    def key_pressed (self, app, event):

        # filter out special keys
        
        if event.keyval == gtk.keysyms.Escape:
            # the Esc key restores view to "all entries"
            self.limit_view (None, None)
        
        if (event.string < 'a' or event.string > 'z') and \
           (event.string < '0' or event.string > '9'): return False

        if self.selection.sort is None:
            app.flash ("Select a column to search in first.")
            return False
        
        if event.string in printable:
            # the user searches the first entry in its ordering that starts with this letter
            if self.incremental_search == '':
                self.incremental_search = event.string
                self.incremental_start  = event.time
            else:
                if event.time - self.incremental_start > 1000:
                    self.incremental_search = event.string
                else:
                    # two keys in a same shot: we search for the composition of the words
                    self.incremental_search = self.incremental_search + event.string
                
                self.incremental_start  = event.time

            # search first occurence
            if self.index.go_to_first (self.incremental_search,
                                       self.selection.sort.fields [0]):
                app.flash ("Searching for '%s...'" % self.incremental_search)
            else:
                app.flash ("Cannot find '%s...'" % self.incremental_search)
                
        return False


    def update_configuration (self):
        ''' save current informations about the program '''
        
        # Save the graphical aspect of the interface
        # 1.- Window size
        alloc = self.w.get_allocation ()
        Utils.config.set_int ('/apps/pybliographic/ui/width',  alloc [2])
        Utils.config.set_int ('/apps/pybliographic/ui/height', alloc [3])

        # 2.- Proportion between list and text
        height = self.paned.get_position ()
        Utils.config.set_int ('/apps/pybliographic/ui/paned', height)

        # updates the index's config
        self.index.update_configuration ()

        return

    def on_documentation (self, *args):
        import gobject

        try:
            gnome.help_display ('pybliographer', 'getting-started')
            
        except gobject.GError, msg:
            self.w.error (_("Can't display documentation:\n%s") % msg)
            
        return
    
    def about (self, *arg):
        
        about = ui.About ('Pybliographic',
                          version.version,
                          _("This program is copyrighted under the GNU GPL"),
                          _("Gnome interface to the Pybliographer system."),
                          ['Hervé Dréau',
                           'Frédéric Gobry',
                           'Zoltán Kóta',
                           'Travis Oliphant',
                           'Darrell Rudmann',
                           'Peter Schulte-Stracke',
                           'John Vu'],
                          ['Yuri Bongiorno',
                           'Frédéric Gobry',
                           'Zoltán Kóta'],
                          _('Gnome Translation Team'))

        about.set_transient_for (self.w)
        
        link = ui.HRef ('http://www.pybliographer.org/',
                        _("Pybliographer Home Page"))
        link.show ()
        about.vbox.pack_start (link)
        about.show()
        return

