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

''' Utility functions for Gnome Interface management. '''

import os

import gtk, pango
import gtk.glade

from gnome import ui

from Pyblio import Config, version

import gconf

class Callback:

    ''' This class provides a simple requested that asks the user a
    queation and waits for an answer. '''
    
    def __init__ (self, question, parent = None):

        self.dialog = \
                    gtk.MessageDialog (parent,
                                       gtk.DIALOG_MODAL |
                                       gtk.DIALOG_DESTROY_WITH_PARENT,
                                       gtk.MESSAGE_QUESTION,
                                       gtk.BUTTONS_YES_NO,
                                       question)
        return

    def answer (self):
        res = self.dialog.run () == gtk.RESPONSE_YES
        self.dialog.destroy ()
        return res


class GladeWindow:

    ''' A Helper class that builds a graphical interface provided by a
    Glade XML file. This class binds the methods with
    signal_autoconnect, and imports wigets whose name starts with _w_
    as instance attributes. Therefore, after init, the instance can refer to:

        self._w_main

    if the glade file defined a _w_main widget.

    This class must be derived and the following class variables must
    be given some sensible value:

        glade_file  : name of the glade file (with no directory info)
        root_widget : name of the root widget

    '''


    # This is a class variable that contains the file name to load for
    # each instance of a subclass.

    gladeinfo = { 'file': None,
                  'root': None,
                  'name': None
                  }

    def __init__ (self, parent = None, window = None):
        
        gp = os.path.join (version.pybdir, 'glade',
                           self.gladeinfo ['file'])
        
        self.xml = gtk.glade.XML (gp, window, domain = "pybliographer")
        self.xml.signal_autoconnect (self)

        for w in self.xml.get_widget_prefix ('_w_'):
            setattr (self, w.name, w)

        # Set the parent window. The root widget is not necessarily
        # exported as an instance attribute.
        root = self.xml.get_widget (self.gladeinfo ['root'])
        cfg  = '/apps/pybliographic/%s/' % self.gladeinfo ['name']
        
        w = config.get_int (cfg + 'width')  or -1
        h = config.get_int (cfg + 'height') or -1

        if w != -1 and h != -1:
            root.set_default_size (w, h)
            root.resize (w, h)
        
        if parent:
            root.set_transient_for (parent)
            
        return

    def size_save (self):
        root = self.xml.get_widget (self.gladeinfo ['root'])
        cfg  = '/apps/pybliographic/%s/' % self.gladeinfo ['name']

        w, h = root.get_size ()

        config.set_int (cfg + 'width',  w)
        config.set_int (cfg + 'height', h)

        return
    
    
config = gconf.client_get_default ()

cursor = {
    'clock' : gtk.gdk.Cursor (gtk.gdk.WATCH),
    'normal': gtk.gdk.Cursor (gtk.gdk.LEFT_PTR),
    }


def set_cursor (self, name):

    window = self.get_toplevel ().window
    if not window: return
    
    window.set_cursor (cursor [name])
        
    while gtk.events_pending ():
        gtk.mainiteration (False)
    return


_tooltips = gtk.Tooltips ()


def set_tip (w, text):
    _tooltips.set_tip (w, text)
    return


if Config.get ('gnome/tooltips').data:
    _tooltips.enable ()
else:
    _tooltips.disable ()


def popup_add (menu, item, action = None, argument = None):
    ''' Helper to add a new menu entry '''
    
    tmp = gtk.MenuItem (item)
    if action:
        tmp.connect ('activate', action, argument)
    
    tmp.show ()
    menu.append (tmp)
    
    return tmp

def error_dialog (title, err, parent = None):

    dialog = \
           gtk.MessageDialog (parent,
                              gtk.DIALOG_MODAL |
                              gtk.DIALOG_DESTROY_WITH_PARENT,
                              gtk.MESSAGE_ERROR,
                              message_format = title)

    b = dialog.add_button (gtk.STOCK_OK, gtk.RESPONSE_OK)
    b.set_property ('has_default', True)
    
    buff = gtk.TextBuffer ()
    title = buff.create_tag ('title', weight = pango.WEIGHT_BOLD)

    text = gtk.TextView ()
    text.set_editable (False)
    text.set_cursor_visible (False)
    text.set_buffer (buff)
    text.set_size_request (400, 200)

    iter = buff.get_start_iter ()
    
    buff.insert_with_tags (iter, _("The following errors occured:\n"),
                           title)
    
    buff.insert (iter, str (err))
    
    holder = gtk.ScrolledWindow ()
    holder.set_policy (gtk.POLICY_AUTOMATIC,
                       gtk.POLICY_AUTOMATIC)
    holder.add (text)
    
    dialog.vbox.pack_start (holder)
    holder.show_all ()
    
    dialog.run ()
    dialog.destroy ()
    
    return

