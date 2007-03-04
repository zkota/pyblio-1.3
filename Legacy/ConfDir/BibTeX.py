from Legacy import Config

# ==================================================

Config.define ('bibtex/keep-preamble',
	       """A boolean requesting that a @preamble in the
	       BibTeX file be kept""",
	       Config.Boolean ())

Config.define ('bibtex/strict',
               """ A boolean indicating the strictness of the parsing """,
               Config.Boolean ())

Config.define ('bibtex/macros', """ A dictionnary defining the BibTeX
macros (@String{} macros). Each entry of the dictionnary is a 2-uple :
the first field is the expansion of the macro, the second is a boolean
indicating if this macro definition has to be saved in the .bib files """,
               Config.Dict (Config.String (),
                            Config.Tuple ((Config.String (), Config.Boolean ()))))

Config.define ('bibtex/datefield', """ A hash table linking a `real'
date field to the two bibtex fields that compose it """)

Config.define ('bibtex/months', """ A hash table linking month names to their
values """)

# ==================================================

Config.set ('bibtex/keep-preamble', 1)

Config.set ('bibtex/strict', 0)


Config.set ('bibtex/macros',
            {'jan' : ("January", 0),
             'feb' : ("February", 0),
             'mar' : ("March", 0),
             'apr' : ("April", 0),
             'may' : ("May", 0),
             'jun' : ("June", 0),
             'jul' : ("July", 0),
             'aug' : ("August", 0),
             'sep' : ("September", 0),
             'oct' : ("October", 0),
             'nov' : ("November", 0),
             'dec' : ("December", 0),
             })


Config.set ('bibtex/datefield', {
    'date'  : ('year', 'month'),
    })

Config.set ('bibtex/months', {
    'jan' : 1,
    'feb' : 2,
    'mar' : 3,
    'apr' : 4,
    'may' : 5,
    'jun' : 6,
    'jul' : 7,
    'aug' : 8,
    'sep' : 9,
    'oct' : 10,
    'nov' : 11,
    'dec' : 12,
    })
    
