from Pyblio import Config, Fields
from Pyblio.GnomeUI import Utils, Editor

import gtk

Config.define ('gnomeui/default', """ Graphical description of the
default field. """)

Config.define ('gnomeui/monospaced', """ A monospaced font, for native edition """)

def _text_get ():

    v = Config.get ('base/fields').data

    fields = filter (lambda x: x.type is Fields.Text, v.values ())
    fields = map (lambda x: x.name.lower (), fields)

    fields.sort ()
    
    return fields

def _on_multiline_select (item, multi, user):

    h = Config.get ('base/fields').data

    for k, v in multi.items ():

        if not h.has_key (k): continue
        
        if v: h [k].widget = Editor.Text
        else: h [k].widget = Editor.Entry
        
    return True


Config.define ('gnomeui/multiline',
               """ Fields displayed in a multi-line widget """,

               Config.Dict (Config.Element (_text_get),
                            Config.Boolean ()),

               hook = _on_multiline_select)


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
    
    if not h.has_key (f): continue

    h [f].width = w
    

Config.set ('gnomeui/default',  (150, gtk.JUSTIFY_LEFT, Editor.Entry))

multi = {}

if h.has_key ('abstract'): multi ['abstract'] = 1

Config.set ('gnomeui/multiline', multi)

