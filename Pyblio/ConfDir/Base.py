from Pyblio import Config, Types, Fields, Autoload

def _get_entries ():
    return Config.get ('base/entries').data.values ()

def _get_fields ():
    return Config.get ('base/fields').data.values ()

def _get_keytypes ():
    return Autoload.available ('key')

def _check_default (item, value, user):
    """ If the entries are updated, update the default type with the new entry """
    
    dfl = Config.get ('base/defaulttype').data
    if dfl is None: return 1

    value = value [string.lower (dfl.name)]
    
    if dfl == value:
        Config.set ('base/defaulttype', value)
        
    return 1


Config.define ('base/advertise', """ Specify wether or not the program should add a message
saying that the output files are generated by pybliographer """,
               vtype = Config.Boolean ())

Config.define ('base/autosave', """ Autosave files """,
               vtype = Config.Boolean ())

Config.define ('base/autosave interval', """ Time in minutes. It specifies the time interval between autosave operations. """,
               vtype = Config.Integer (min = 1))

Config.define ('base/backup', """ Create a backup copy of files before saving """,
               vtype = Config.Boolean ())

Config.define ('base/fields', """ Existing fields.  It's a hash table,
               with the field name (lower case) as key, and a instance
               of Types.FieldDescription as value. """)
               
Config.define ('base/entries', """ Existing entries.  It's a hash
               table, with the entry name (lower case) as key, and a
               instance of Types.EntryDescription as value. """,

               hook = _check_default)

Config.define ('base/defaulttype', """ Default type for a newly created entry """,
               vtype = Config.Element (_get_entries))

Config.define ('base/lyxpipe', """ Path to the LyX server """,
               vtype = Config.String ())

Config.define ('base/keyformat', """ Style of generated keys """,
               vtype = Config.Element (_get_keytypes))

# --------------------------------------------------

Config.set ('base/keyformat', 'Default')

# Available fields

fields = [ 'CrossRef', 'Key', 'Author', 'Address_1', 'Address_2',
           'Title', 'SpecificTitle', 'Journal', 'Special', 'Type', 'BookTitle',
           'Subject', 'Ownership', 'Series', 'Editor', 'Edition', 'Volume',
           'Number', 'Chapter', 'Pages', 'School', 'Organization', 'Location',
           'Dates', 'Institution', 'Publisher', 'Address', 'Format',
           'Date', 'NoSeries', 'ConfPlace', 'Cote', 'IEEECN', 'Annotate',
           'Quote', 'LoCN', 'ISBN', 'ISSN', 'Note', 'Language', 'HowPublished',
           'To_Appear', 'From', 'Received', 'Owner', 'Keywords', 'Abstract',
           'Remarks', 'URL', 'Beigabevermerk' ]

entries = {
    'Article' : (('author', 'title', 'journal', 'date'),
                 ('volume', 'number', 'pages', 'note')),
    
    'Book' : (('author', 'editor', 'title', 'publisher', 'date'),
              ( 'volume', 'number', 'series', 'address', 'edition',
                'note')),
    
    'Booklet' : (('title',),
                 ('author', 'howpublished', 'address', 'date',
                  'note')),
    
    'InBook' : (('author', 'editor', 'title', 'chapter', 'pages', 'publisher',
                 'date'),
                ('volume', 'number', 'series', 'type', 'address', 'edition',
                  'note')),
    
    'InCollection' : (('author', 'title', 'booktitle', 'publisher', 'date', ),
                      ('editor', 'volume', 'number', 'series', 'type',
                      'chapter', 'pages', 'address', 'edition', 'note',)),
    
    'InProceedings' : (('author', 'title', 'booktitle', 'date',),
                       ('editor', 'volume', 'number', 'series',
                       'pages', 'address', 'organization',
                       'publisher', 'note')),
    
    'Manual' : (('title',),
                ('author', 'organization', 'address', 'edition',
                 'date', 'note',)),
    
    'MastersThesis' : (('author', 'title', 'school', 'date',),
                       ('type', 'address', 'note',)),
    
    'Misc' : ((),
              ('author', 'title', 'howpublished', 'date', 'note',)),
    
    'PhdThesis' : (('author', 'title', 'school', 'date',),
                       ('type', 'address', 'note',)),
    
    'Proceedings' : (('title', 'date',),
                     ('editor', 'volume', 'number', 'series',
                     'address', 'publisher', 'note',
                      'organization',)),
    
    'TechReport' : (('author', 'title', 'institution', 'date',),
                    ('type', 'number', 'address', 'note',)),
    
    'Unpublished' : (('author', 'title', 'note',),
                     ('date',)),
    }


Config.set ('base/lyxpipe', '~/.lyx/lyxpipe')

# --------------------------------------------------

desc = {}
# create the hash table
for f in fields:
    desc [string.lower (f)] = Types.FieldDescription (f)
    
# Special fields

desc ['author'].type   = Fields.AuthorGroup
desc ['editor'].type   = Fields.AuthorGroup
desc ['date'].type     = Fields.Date
desc ['crossref'].type = Fields.Reference
desc ['url'].type      = Fields.URL

desc ['abstract'].type     = Fields.LongText
desc ['annotate'].type     = Fields.LongText
desc ['note'].type         = Fields.LongText
desc ['quote'].type        = Fields.LongText
desc ['remarks'].type      = Fields.LongText
#desc ['beigabevermerk'].type      = Fields.LongText


Config.set ('base/fields', desc)

# Entry types
def _set_entries (entries):
    desc = Config.get ('base/fields').data
    ent  = {}
    
    for e in entries.keys ():
        d = Types.EntryDescription (e)

        d.mandatory = \
                    map (lambda x, desc=desc: desc [x], entries [e] [0])
        d.optional  = \
                   map (lambda x, desc=desc: desc [x], entries [e] [1])

        ent [string.lower (e)] = d

    Config.set ('base/entries', ent)
    return

_set_entries (entries)

Config.set ('base/defaulttype',
            Config.get ('base/entries').data ['article'])

Config.set ('base/advertise', 1)

Config.set ('base/autosave', 0)

Config.set ('base/autosave interval', 10)

Config.set ('base/backup', 1)

