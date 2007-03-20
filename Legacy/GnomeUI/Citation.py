# This file is part of pybliographer
# 
# Copyright (C) 1998-2006 Frederic GOBRY
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

from Pyblio.Cite.WP.LyX import LyX
from Pyblio.Cite.WP import CommunicationError
from Pyblio.Cite.Citator import Citator

from Legacy.GnomeUI import Utils


import logging

from gettext import gettext as _

import gtk

log = logging.getLogger('pyblio.ui')

available = [
    (LyX, _('LyX / Kile'))
    ]

try:
    from Pyblio.Cite.WP.OpenOffice import OOo
    available.append((OOo, _('OpenOffice.org')))

except ImportError, msg:
    log.warn('cannot import OpenOffice.org support: %s' % msg)


class Connect(Utils.GladeWindow):
    gladeinfo = { 'file': 'wpconnect.glade',
                  'root': '_w_connect',
                  'name': 'connect'
                  }

    def __init__(self, current_wp):
        Utils.GladeWindow.__init__(self)

        self._buttons = {}
        self._active = current_wp
        self._citator = None
        
        for m, name in available:
            t = gtk.ToggleButton(name)
            t.connect('toggled', self._toggled, m, name)

            self._buttons[m] = t
            self._w_list.pack_start(t)

        for m, name in available:
            if isinstance(current_wp, m):
                self._buttons[m].set_active(True)

        self._w_connect.show_all()

    def _on_selection(self, chooser):
        self._citator = Citator()
        self._citator.xmlload(open(chooser.get_filename()))
        return
    
    def _toggled(self, w, activate, name):
        # when a button is pushed, we begin by locking the others.
        do_connect = w.get_active()
        for m, b in self._buttons.iteritems():
            if m != activate:
                b.set_sensitive(not do_connect)

        # only then we try to connect
        self._active = None
        
        if do_connect:
            new = activate()

            try:
                new.connect()
            except CommunicationError, msg:
                e = gtk.MessageDialog(self._w_connect,
                                      gtk.DIALOG_MODAL,
                                      gtk.MESSAGE_ERROR,
                                      gtk.BUTTONS_OK)

                e.set_markup(_('Unable to connect to <b>%s</b>') % name)
                e.format_secondary_text(str(msg))

                e.run()
                e.destroy()
                
                w.set_active(False)
                return

            self._active = new
        return
    
    def run(self):
        self._w_connect.run()
        self._w_connect.destroy()
        
        return self._active, self._citator
    
