from Pyblio import Config, Types
from Pyblio.Format.OvidLike import SimpleField, AuthorField, SourceField, KeywordField

def _get_elements ():
    return     [SimpleField, AuthorField, SourceField, KeywordField]

Config.define ('ovid/deftype', """ Default type for an Ovid entry """,
               Config.Element (lambda Config = Config:
                               Config.get ('base/entries').data.values ()))

Config.set ('ovid/deftype',
            Config.get ('base/entries').data ['article'])

Config.define ('ovid/sourceregexp',
               """A regexp used to parse the source and abbreviated
               source input fields. This is a raw and verbose Python
               regular expression""",
               Config.String())

Config.set ('ovid/sourceregexp',
    r"""
    (?P<journal>.*)\.\ +
    (?P<volume>\d+)
    (?:\((?P<number>.*)\))?
    (?::(?P<pages>.*?(?:-+.*?)?)
    (?:;\ *(?P<other>.*))?)
    (?:,\ *(?P<year>\d\d\d\d))\ *
    (?P<month>.*)
    \.\Z
    """)

Config.define ('ovid/mapping', 
               """ A mapping between the Ovid field name and
the current field and type. The key is the Ovid field (lower
cases), and the values are tuples of the form (<pyblio field
name>, <entry type>)""", Config.Dict (Config.String(),
                                      Config.Tuple (
    (Config.String(),
    Config.Element (_get_elements )))))


Config.set ('ovid/mapping', {
    'abbreviated source'
                    : ('abbrevsrc',   SimpleField),
    'abstract'      : ('abstract',    SimpleField),
    'accession number'
                    : ('accession',   SimpleField),
    'author'        : ('author',      AuthorField),
    'author keywords'
                    : ('keywords',    KeywordField),
    'authors'       : ('author',      AuthorField),
    'cas registry/ec number' 
                    : ('casec',       SimpleField),
    'cc categories' : ('cccat',       SimpleField),
    'classification codes'
                    : ('classificationCodes',
                                      SimpleField),
    'country of publication'
                    : ('country',     SimpleField),
    'document delivery'
                    : ('docdeliv',    SimpleField),
    'entry date'    : ('sourceid4',   SimpleField),
    'institution'   : ('institution', SimpleField),
    'issn'          : ('issn',        SimpleField),
    'journal subset': ('nlmsubset',   SimpleField),
    'key phrase identifiers'
                    : ('keywords',    SimpleField),
    'keywords+'     : ('keywords',    KeywordField),
    'keywords plus' : ('keywords',    KeywordField),
    'language'      : ('language',    SimpleField),
    'mesh subject headings'
                    : ('mesh',        SimpleField),
    'nlm journal code'
                    : ('nlmjournal',  SimpleField),
    'publication notes'
                    : ('note',        SimpleField),
    'publication type'
                    : ('type',        SimpleField),
    'record owner'  : ('sourceid1',   SimpleField),
    'revision date' : ('sourceid3',   SimpleField),
    'source'        : ('journal',     SourceField),
    'subject headings'
                    : ('subjectHdgs', SimpleField),
    'subset'        : ('subset',      SimpleField), 
    'title'         : ('title',       SimpleField),
    'treatment'     : ('treatment',   SimpleField),
    'unique identifier'
                    : ('sourceid0',   SimpleField),
    'update date'   : ('sourceid2',   SimpleField), 
    })

