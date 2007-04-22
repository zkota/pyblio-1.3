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

from gnome import ui
import os
import gtk
import gobject
import datetime
import StringIO
import Legacy.Format.BibTeX
from xml.sax.saxutils import escape

from Legacy import Fields, Connector
from Legacy.GnomeUI import Utils
from Pyblio.External import PubMed
from Pyblio import Store, Registry, Adapter
from Pyblio.Cite import Citator
from Pyblio.Format import HTML
from Pyblio.Parsers.Semantic import BibTeX

class MedlineUI (Utils.GladeWindow):

    gladeinfo = { 'name': 'medline',
                  'file': 'medline.glade',
                  'root': '_w_medline'
                  }

    helper = PubMed.QueryHelper()

    def __init__ (self, document, parent=None):
        Utils.GladeWindow.__init__(self, parent)
        self.document = document
        # helper to fill in combo boxes with values from a dictionary
        def new_box(w, title, values, sorted=True, default=None):
            model = gtk.ListStore(gobject.TYPE_PYOBJECT,
                                  gobject.TYPE_STRING)
            w.set_model(model)
            cell = gtk.CellRendererText()
            w.pack_start(cell, True)
            w.add_attribute(cell, 'text', 1)
            if sorted:
                pairs = values.items()
                pairs.sort(key=lambda x:x[1])
            else:
                pairs = values
            if title:
                model.append((default, title))
            for pair in pairs:
                model.append(pair)
            w.set_active(0)

        new_box(self._w_pub_type, _("Any publication type"),
                self.helper.publication_types)
        new_box(self._w_language, _("Any language"),
                self.helper.language)
        new_box(self._w_subset, _("Any journal"),
                self.helper.subset)
        new_box(self._w_age, _("Any age"),
                self.helper.age_range, sorted=False)
        new_box(self._w_human, _("Human or animal"),
                self.helper.human_animal)
        new_box(self._w_gender, _("Any gender"),
                self.helper.gender)

        today = datetime.date.today()
        def range(days):
            return (today - datetime.timedelta(days), today)
        new_box(self._w_entrez_date, _("Entrez date"), [
            (range(30), _("30 days")), (range(60), _("60 days")),
            (range(90), _("90 days")), (range(180), _("180 days")),
            (range(365), _("1 year")), (range(365*2), _("2 years")),
            (range(365*5), _("5 years")), (range(365*10), _("10 years")),
            ], sorted=False, default=(None, None))

        new_box(self._w_pub_date, None,
                [(True, _("Publication date")),
                 (False,_("Entrez date"))],
                sorted=False)

        self._w_medline.show ()
        return

    def _w_close(self, w):
        self.size_save()
        self._w_medline.destroy()

    def _on_search(self, w):
        def get(w):
            return w.get_model()[w.get_active()][0]

        from_date, to_date = get(self._w_entrez_date)
        if from_date is None:
            def parse(text):
                try:
                    parts = [int(x) for x in text.split('/')]
                except ValueError:
                    return None
                if not parts:
                    return None
                if len(parts) == 1:
                    return datetime.date(year=parts[0],
                                         month=12, day=31)
                if len(parts) == 2:
                    return (datetime.date(year=parts[0],
                                          month=parts[1]+1,
                                          day=1) -
                            datetime.timedelta(days=1))
                return datetime.date(*parts[:3])
            from_date, to_date = (
                parse(self._w_from_date.get_text()),
                parse(self._w_to_date.get_text()))

        q = self.helper.makeQuery(
            keyword=self._w_keyword.entry.get_text(),
            abstract=self._w_abstracts.get_active(),
            epubahead=self._w_ahead.get_active(),
            publication_type=get(self._w_pub_type),
            language=get(self._w_language),
            subset=get(self._w_subset),
            age_range=get(self._w_age),
            human_animal=get(self._w_human),
            gender=get(self._w_gender),
            use_publication_date=get(self._w_pub_date),
            from_date=from_date, to_date=to_date)

        Fetch(self.document, q, self._w_medline)

class Fetch(Utils.GladeWindow):

    gladeinfo = { 'name': 'fetch',
                  'file': 'fetch.glade',
                  'root': '_w_fetch'
                  }

    def __init__ (self, document, query, parent=None):
        self.cell = None
        Utils.GladeWindow.__init__(self, parent)

        s = Registry.getSchema('org.pybliographer/pubmed/0.1')
        db = Store.get('memory').dbcreate(None, s)
        pm = PubMed.PubMed(db)
        pm.BATCH_SIZE = 50

        self.document = document
        self.db = db
        url = Fields.URL('file:/dev/null')
        self.parser = Legacy.Format.BibTeX.DataBase(url)
        self._w_fetch.set_title(_("PubMed results for: %s") % query)
        self._w_summary.set_markup(_("PubMed results for <i>%s</i>") %
                                   escape(query))
        self.writer = BibTeX.Writer()
        # in order to display a compact form of the results, we need
        # to format them. use a mapping on top of the bibtex version.
        self.bibtex = Adapter.adapt_schema(db, 'org.pybliographer/bibtex/0.1')
        self.cite = Citator.Citator()
        self.cite.xmlload(os.path.join(
            Registry.RIP_dirs['system'], 'full.cip'))
        self.cite.prepare(self.bibtex, None)

        model = gtk.ListStore(gobject.TYPE_PYOBJECT,
                              gobject.TYPE_STRING)
        self.cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn(None, self.cell, markup=1)
        self._w_view.append_column(column)
        self._w_view.set_model(model)

        callback = pm.count(query)

        self._w_progress.set_fraction(0.0)
        self._w_progress.set_text(_("Fetching results"))

        def failure(msg):
            # TODO: provide a user level error message
            print "FAILURE", msg
        
        def done_count(total):
            self._total = total
            self._got = 0.0
            target = min(total, 100)
            def set_progress():
                self._w_progress.set_fraction(self._got / target)
                self._w_progress.set_text(_("Done %d/%d (%d total)") % (
                    len(db.entries), target, self._total))
            set_progress()

            l2cb, rs = pm.search(query, maxhits=100)
            def _on_add(k):
                v = db[k]
                t = HTML.generate(self.cite.formatter(v))
                model.append((k, t))
                self._got += 1
                set_progress()
            rs.register('add-item', _on_add)
            # ensure this function won't be garbage collected too
            # quickly
            self._on_add = _on_add

            def done(total):
                self._w_stop.set_sensitive(False)
                self._w_progress.set_fraction(1.0)
                self._w_progress.set_text(_("Done %d (%d total)") % (
                    len(db.entries), total))
            l2cb.addCallback(done).addErrback(failure)
        callback.addCallback(done_count).addErrback(failure)

    def _w_close(self, w):
        self.size_save()
        self._w_fetch.destroy()
        
    def _on_stop(self, w):
        # TODO: cancel action
        return
    
    def _w_row_activate(self, w, position, column):
        m = w.get_model()
        io = StringIO.StringIO()
        rs = self.bibtex.rs.new()
        rs.add(m[position][0])
        self.writer.write(io, rs, self.bibtex)
        entry = self.parser.create_native(io.getvalue())
        self.document.drag_received([entry])
        
    def _on_new_size(self, w, rectangle):
        if self.cell:
            self.cell.set_property('wrap-width', rectangle.width)
