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

for f, w in (('author', 150),
             ('editor', 150),
             ('title',  200),
             ('booktitle', 200),
             ('date', 50)):
    
    if not h.has_key (f):
        continue

    h [f].width = w
    
if h.has_key ('abstract'):
    h ['abstract'].widget = Editor.Text

Config.set ('gnomeui/default',  (150, gtk.JUSTIFY_LEFT, Editor.Entry))

