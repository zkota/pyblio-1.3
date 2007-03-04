from Legacy import Config, Types
from Legacy.Format.OvidLike import SimpleField, AuthorField, SourceField, KeywordField

def _get_elements ():
    return     [SimpleField, AuthorField, SourceField, KeywordField]

Config.define ('ovid/deftype', """ Default type for an Ovid entry """,
               Config.Element (lambda Config = Config:
                               Config.get ('base/entries').data.values ()))

Config.set ('ovid/deftype',
            Config.get ('base/entries').data ['article'])

## Config.define ('ovid/sourceregexp',
##                """A regexp used to parse the source and abbreviated
##                source input fields. This is a raw and verbose Python
##                regular expression""",
##                Config.String())

## Config.set ('ovid/sourceregexp',
##     r"""
##     (?P<journal>.*)\.\ +
##     (?P<volume>\d+)
##     (?:\((?P<number>.*)\))?
##     (?::(?P<pages>.*?(?:-+.*?)?)
##     (?:;\ *(?P<other>.*))?)
##     (?:,\ *(?P<year>\d\d\d\d))\ *
##     (?P<month>.*)
##     \.\Z
##     """)

Config.define ('ovid/mapping', 
               """ A mapping between the Ovid field name and
the current field and type. The key is the Ovid field (lower
cases), and the values are tuples of the form (<pyblio field
name>, <entry type>)""", Config.Dict (Config.String(),
                                      Config.Tuple (
    (Config.String(),
    Config.Element (_get_elements )))))


Config.set ('ovid/mapping', {
    'Abbreviated Source'
                    : ('abbrevsrc',   SimpleField),
    'Abstract'      : ('abstract',    SimpleField),
    'Accession Number'
                    : ('accession',   SimpleField),
    'Author'        : ('author',      AuthorField),
    'Author Keywords'
                    : ('author-keywords',
                       KeywordField),
    'Authors'       : ('author',      AuthorField),
    'CAS Registry/EC Number' 
                    : ('casec',       SimpleField),
    'CC Categories' : ('cccat',       SimpleField),
    'Classification Codes'
                    : ('classificationCodes',
                                      SimpleField),
    'Country of Publication'
                    : ('country',     SimpleField),
    'Document Delivery'
                    : ('docdeliv',    SimpleField),
    'Entry Date'    : ('sourceid4',   SimpleField),
    'Institution'   : ('institution', SimpleField),
    'ISSN'          : ('issn',        SimpleField),
    'Journal Subset': ('nlmsubset',   SimpleField),
    'Key Phrase Identifiers'
                    : ('keyphrase',   SimpleField),
    'Keywords+'     : ('keywords',    KeywordField),
    'KeyWords Plus' : ('keywordsplus',    KeywordField),
    'Language'      : ('language',    SimpleField),
    'Mesh Subject Headings'
                    : ('mesh',        KeywordField),
    'NLM Journal Code'
                    : ('nlmjournal',  SimpleField),
    'Publication Notes'
                    : ('note',        SimpleField),
    'Publication Type'
                    : ('profile',     SimpleField),
    'Record Owner'  : ('sourceid1',   SimpleField),
    'Revision Date' : ('sourceid3',   SimpleField),
    'Source'        : ('journal',     SourceField),
    'Subject Headings'
                    : ('subjectHdgs', SimpleField),
    'Subset'        : ('subset',      SimpleField), 
    'Title'         : ('title',       SimpleField),
    'Treatment'     : ('treatment',   SimpleField),
    'Unique Identifier'
                    : ('sourceid0',   SimpleField),
    'Update Date'   : ('sourceid2',   SimpleField), 
    })

