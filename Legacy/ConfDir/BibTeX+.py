import string
from Legacy import Config, Fields

def _get_text_ent ():
    return map (lambda x: string.lower (x.name),
                filter (lambda x: x.type is Fields.Text,
                        Config.get ('base/fields').data.values ()))

Config.define ('bibtex+/braces',
               """ A boolean specifying if pybliographic should use
               braces (instead of quotes) to limit entries """,
               Config.Boolean ())

Config.define ('bibtex+/capitalize', """ A flag indicating if
pybliographer should handle automatic capitalization in the bibtex
output """, vtype = Config.Dict (Config.Element (_get_text_ent),
                                 Config.Boolean ()))

Config.define ('bibtex+/override', """ A boolean indicating if the
macro definitions provided here should override the ones given in a
file """, Config.Boolean ())

Config.define ('bibtex+/dateformat', """ A template used for date formatting """,
               Config.String ())


Config.set ('bibtex+/braces', 1)

Config.set ('bibtex+/capitalize', {
    'title'     : 1,
    'booktitle' : 1,
    })
               
Config.set ('bibtex+/override', 0)

Config.set ('bibtex+/dateformat', "{%(day)d } # %(month)s")

