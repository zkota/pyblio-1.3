import gtk

from Pyblio import Config, Fields
from Pyblio.GnomeUI import Utils, Editor

Config.define ('gnomeui/default', """ Graphical description of the
default field. """)

Config.define ('gnomeui/monospaced', """ A monospaced font, for native edition """)

# --------------------------------------------------

Config.set ('gnomeui/monospaced',
            gtk.load_font ('-*-*-*-r-normal-*-*-*-*-*-c-*-iso8859-1'))

h = Config.get ('base/fields').data

Fields.AuthorGroup.widget = Editor.AuthorGroup
Fields.Text.widget        = Editor.Entry
Fields.URL.widget         = Editor.URL
Fields.Reference.widget   = Editor.Reference

Fields.Date.widget        = Editor.Date
Fields.Date.justification = gtk.JUSTIFY_RIGHT

h ['author'].width     = 150
h ['editor'].width     = 150
h ['title'].width      = 200
h ['booktitle'].width  = 200
h ['date'].width       = 50

h ['abstract'].widget  = Editor.Text

Config.set ('gnomeui/default',  (150, gtk.JUSTIFY_LEFT, Editor.Entry))

