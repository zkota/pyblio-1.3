from Pyblio import Config

Config.define ('refer/mapping',
               """ A hash table containing field names
               correspondances. The boolean flag specifies if the
               mapping should be reversible. """,
               vtype = Config.Dict (Config.String (),
                                    Config.Tuple ((Config.String (),
                                                   Config.Boolean ()))))

Config.set ('refer/mapping', {
    'U' : ('url', 1),
    'A' : ('author', 1),
    'Q' : ('author', 0),
    'T' : ('title', 1),
    'S' : ('series', 1),
    'J' : ('journal', 1),
    'B' : ('booktitle', 1),
    'R' : ('type', 1),
    'V' : ('volume', 1),
    'N' : ('number', 1),
    'E' : ('editor', 1),
    'D' : ('date', 1),
    'P' : ('pages', 1),
    'I' : ('publisher', 1),
    'C' : ('address', 1),
    'K' : ('keywords', 1),
    'X' : ('abstract', 1),
    'W' : ('location', 1),
    'F' : ('label', 1),
    'O' : ('note', 1),
    })
