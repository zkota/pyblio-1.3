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

from gettext import gettext as _

import gtk
import logging
import StringIO

from Pyblio.Cite.WP.LyX import LyX
from Pyblio.Cite.WP import CommunicationError, OperationError
from Pyblio.Cite.Citator import Citator
from Pyblio import Store, Registry
from Pyblio.Parsers.Semantic import BibTeX
from Legacy.GnomeUI import Utils
from Legacy.Iterator import Iterator
from Legacy.Format.BibTeX import writer
from Legacy.Key import Key

log = logging.getLogger('pyblio.ui')

available = [
    (LyX, _('LyX / Kile'))
    ]

try:
    from Pyblio.Cite.WP.OpenOffice import OOo
    available.append((OOo, _('OpenOffice.org')))

except ImportError, msg:
    log.warn('cannot import OpenOffice.org support: %s' % msg)


class _SingleEntryIterator(Iterator):
    def __init__(self, entry):
        self.entry = entry
    def first(self):
        return self.entry
    def next(self):
        return None

def _extract_id(key, db):
    return db[key]['id'][0]


class TransientDB(object):
    """Bind the Legacy database with a pyblio 1.3 db that will be used
    for citing, and keep it in sync """

    def __init__(self, legacy, citator, wp):
        self.citator = citator
        schema = Registry.getSchema('org.pybliographer/bibtex/0.1')
        self.db = Store.get('memory').dbcreate(None, schema)
        self.legacy = legacy
        self.reader = BibTeX.Reader()
        # TODO: once we have per-field queries in pyblio-1.3, directly
        # search for the key instead of keeping this cache
        self.mapping = {}

        self.citator.prepare(self.db, wp, _extract_id)
        
        # pre-fill the pyblio db with the bibtex records indicated in
        # the document, in the extra field. We don't have a clean way
        # to obtain the same record id as the last time when importing
        # from bibtex, so we create a new db afresh, and shuffle
        # things in a second pass.
        tmp = Store.get('memory').dbcreate(None, schema)
        renaming = {}

        self.missing = []
        fetched = self.citator.wp.fetch()
        if fetched is None:
            return

        for pyblio_uid, name, bibtex_key in fetched:
            full_key = Key(legacy, str(bibtex_key))
            if not legacy.has_key(full_key):
                self.missing.append(bibtex_key)
                continue
            tmp_key = self._transfer_entry(tmp, full_key)
            renaming[tmp_key] = pyblio_uid
            self.mapping[full_key] = pyblio_uid

        for tmp_key, record in tmp.entries.iteritems():
            self.db.add(record, key=renaming[tmp_key])

    def _transfer_entry(self, db, bibtex_key):
        # parse the initial bibtex content and insert it in the
        # transient db
        it = _SingleEntryIterator(self.legacy[bibtex_key])
        fd = StringIO.StringIO()
        writer(it, fd)
        fd.seek(0, 0)
        new_rs = self.reader.parse(fd, db)
        assert len(new_rs) == 1, list(new_rs)
        return list(new_rs)[0]

    def cite(self, keys):
        """Start managing the specified legacy key """
        log.info('citing %r' % keys)
        all_keys = []
        for key in keys:
            if key not in self.mapping:
                # parse the initial bibtex content and insert it in the
                # transient db
                local_key = self._transfer_entry(self.db, key)
                self.mapping[key] = local_key
                log.info('mapping %s to %s' % (key, local_key))
            else:
                local_key = self.mapping[key]
                log.info('reusing %s as %s' % (key, local_key))
            all_keys.append(local_key)
        self.citator.cite(all_keys)

    def update(self):
        """Refresh the word-processor copy of the bibliography with
        the current data."""
        self.citator.update()

class Connect(Utils.GladeWindow):
    gladeinfo = { 'file': 'wpconnect.glade',
                  'root': '_w_connect',
                  'name': 'connect'
                  }

    def __init__(self, legacy_db, current_wp):
        Utils.GladeWindow.__init__(self)

        self._buttons = {}
        self._active = current_wp
        self._citator = None
        self._legacy = legacy_db

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
            except (CommunicationError, OperationError), msg:
                e = gtk.MessageDialog(self._w_connect, gtk.DIALOG_MODAL,
                                      gtk.MESSAGE_ERROR, gtk.BUTTONS_OK)
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

        if self._citator:
            citator = TransientDB(self._legacy, self._citator, self._active)
        else:
            citator = None

        if citator:
            if citator.missing:
                e = gtk.MessageDialog(self._w_connect, gtk.DIALOG_MODAL,
                                      gtk.MESSAGE_ERROR, gtk.BUTTONS_OK)
                e.set_markup(_('<b>References are missing</b>'))
                e.format_secondary_text(
                    _('The following references are missing:\n%s') %
                    ', '.join(citator.missing))
                e.run()
                e.destroy()
                citator = None
        return self._active, citator
    
