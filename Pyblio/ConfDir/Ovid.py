from Pyblio import Config, Types
from Pyblio.Format.OvidLike import SimpleField, AuthorField, SourceField, KeywordField


Config.define ('ovid/deftype', """ Default type for an Ovid entry """,
               Config.Element (lambda Config = Config:
                               Config.get ('base/entries').data.values ()))

Config.set ('ovid/deftype',
            Config.get ('base/entries').data ['article'])


Config.define ('ovid/mapping',
               """  A mapping  between  the Ovid  field  name and  the
current field and  type. The key is the Ovid  field (lower cases), and
the values are tuples of  the form (<pyblio field name>, <entry type>)
""")

Config.set ('ovid/mapping', {
    'title'    : ('title',    SimpleField),
    'author'   : ('author',   AuthorField),
    'abstract' : ('abstract', SimpleField),
    'key phrase identifiers' : ('keywords', SimpleField),
    'subject headings' : ('subjectHeadings', SimpleField),
    'classification codes' : ('classificationCodes', SimpleField),
    'publication type' : ('type', SimpleField),
    'treatment'        : ('treatment', SimpleField),
    'source'           : (('journal', 'volume', 'number', 'pages', 'date'),
                          SourceField),
    'author keywords' : ('keywords', KeywordField),
    'keywords+'       : ('keywords', KeywordField),
    })
