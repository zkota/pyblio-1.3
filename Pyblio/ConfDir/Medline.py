from Pyblio import Config

Config.define ('medline/mapping',
               """ A hash table containing field names correspondances """,
               Config.Dict (Config.String (), Config.String ()))

Config.set ('medline/mapping', {
    'UI' : 'medlineref',
    'AU' : 'author',
    'DP' : 'date',
    'TI' : 'title',
    'LA' : 'language',
    'MH' : 'keywords',
    'AD' : 'affiliation',
    'AB' : 'abstract',
    'AD' : 'authoraddress',
    'TA' : 'journal',
    'CY' : 'country',
    'PG' : 'pages',
    'IP' : 'number',
    'VI' : 'volume',
    })
