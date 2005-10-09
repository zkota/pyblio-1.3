# -*- coding: 'utf-8' -*-
from Pyblio import Config, Fields

def _get_fields ():
    return Config.get ('base/fields').data.keys ()

def _get_url_fields ():
    fields = Config.get ('base/fields').data
    return [ x for x in fields.keys () if fields [x] == Fields.URL]
 
Config.define  ('resource/viewable-fields',
		"""A list of fieldnames referring to
		viewable resources (with URL or otherwise).""",
		Config.List (Config.Element (_get_fields)))

Config.define ('resource/viewers',
	       """A list of mime type, viewer application name tuples. """,
	       Config.List (Config.Tuple ((Config.String(), Config.String ()))))



Config.set     ('resource/viewable-fields',
		['url', ])


Config.set ('resource/viewers',
	    [['application/pdf', 'acroread'],
	     ['application/pdf', 'evince'],
	     ['application/x-dvi', 'xdvi'],
	     ['application/x-dvi', 'evince'],
	     ['application/postscript', 'evince'],
	     ['application/gzpostscript', 'evince'],
	     ['image/vnd.djvu', 'djview'],
	     ['image/vnd.djvu', 'evince'],
	     ['text/html', 'mozilla'],
	     ['text/html', 'konqueror'],
	     ])

