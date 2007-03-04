# This file is part of pybliographer
#  
# Original author of Ovid reader: Travis Oliphant <Oliphant.Travis@mayo.edu>
#
# Copyright (C) 1998-2004 Frederic GOBRY
# Email : gobry@pybliographer.org
# 	   
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2 
# of the License, or (at your option) any later version.
#   
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details. 
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
# 
# 

""" Parser for files having an Ovid-like structure """

import sys, re, string

from Legacy import Base, Exceptions, Fields, Iterator, Types, Utils

SimpleField  = 0
AuthorField  = 1
SourceField  = 2
KeywordField = 3

separator_re = re.compile (r'<\d+>$')

compact_dot  = re.compile (r'\.(\s*\.)+')

long_month = {
    'Jan': 1,  'Feb': 2,  'Mar': 3,
    'Apr': 4,  'May': 5,  'Jun': 6,
    'Jul': 7,  'Aug': 8,  'Sep': 9,
    'Oct': 10, 'Nov': 11, 'Dec': 12
    }

# create list from month dict
month_name = range (0, 12)

for key in long_month.keys ():
    month_name [long_month [key] - 1] = key



def make_anti_mapping (mapping):
    m = {}
    for i, j in mapping.items():
        m[j[0]] = (i, j[1])
    return m

class OvidLike (Iterator.Iterator):
    source_rx  = r"""(?P<journal>.*?)\.\ +
        (?P<volume>\w+)?
        (?P<inseries>(\ PG\.\ +))?
        (?:\((?P<number>.*)\))?
        (?::?(?P<pages>.*?(?:-+.*?)?)
        (?:;\ *(?P<other>.*))?)
        (?:[,\.]\ *(?P<year>\d\d\d\d))\ *
        (?P<month>.*)
        \.\s*\Z"""

    source_re = re.compile  (source_rx, flags=re.VERBOSE)

    def __init__ (self, file, mapping, deftype):
        self.file    = file
        self.deftype = deftype
        self.mapping = {}
        for i, j in mapping.iteritems():
            self.mapping[i.lower()] = j
        return

    def first (self):
        # rewind the file
        self.file.seek (0)

        # skip blank and <\d+> line
        while 1:
            line = self.file.readline ()
            if line == '': return None

            line = string.strip (line)
            if line == '': continue
            
            if separator_re.match (line): break
            print 'Ignored Prelude Line:', line
        
        return self.next ()

    
    def next (self):
        dict = {}
        
        # read entry till next blank line
        text  = []
        field = ''
        while 1:
            line = self.file.readline ()
            if line == '': break
            line = string.rstrip (line)

            # starting with a blank ?
            if line == '' or   line [0] == ' ':
                # ...then we continue the current text
                text.append (string.lstrip (line))
                continue

            # new entry ?
            if separator_re.match (line): break

            # else, this is a new field
            if field:
                # save the previous one if needed
                dict [field] = '\n'.join(text)
                text = []

            # store the name of this new field
            field = string.lower (line)

        # don't waste the last field content
        if field:
            dict [field] = '\n'.join(text)

        # did we parse a field ?
        if len (dict) == 0: return None

        # create the entry content
        entry = Base.Entry (type = self.deftype)

        for key in dict.keys ():
            if not self.mapping.has_key (key):
                #print "warning: unused key `%s'" % key
                continue

            (name, type) = self.mapping [key]
            text_type = Types.get_field (name).type

            # parse a simple text field
            if type == SimpleField:
                entry [name] = text_type (string.strip (dict [key]))

            elif type == KeywordField:
                text = string.strip (dict [key])
                if entry.has_key (name):
                    text = str (entry [name]) + '\n  ' + text
                    
                entry [name] = text_type (text)

            # parse an author field
            elif type == AuthorField:
                entry [name] = self.parse_author (dict[key])
                continue

            # parse a source field
            elif type == SourceField:
                dict_key = ' '.join(dict[key].split('\n'))
                m = self.source_re.match (dict_key.strip())
                if m:
                    year, month, day = None, None, None
                    j, v, s, n, p, o, y, d = m.group(
                        'journal', 'volume', 'inseries', 'number',
                        'pages', 'other', 'year', 'month')

                    if s:                ### article in a monograph series
                        entry['booktitle'] = Fields.Text (j)
                        if d:
                            entry['beigabevermerk'] = Fields.LongText (d)
                        entry.type = Types.get_entry('incollection')

                    elif j:
                        entry ['journal'] = Fields.Text (j)
                        if d and not d.isspace():
                            dates = d.split ()                    
                            try:
                                month = long_month [dates[0]]
                            except KeyError:
                                pass
##                                 import warnings
##                                 warnings.filterwarnings ('once',
##                                                          message='date',
##                                                          module='OvidLike')
##                                 warnings.warn (
##                                     'OVID: %s is not representable in date '
##                                     'field %s' %(dates[0], d), stacklevel=2)
                            if len(dates) > 1:
                                day = int (dates[1])

                    if v:
                        entry ['volume'] = Fields.Text (v)

                    if n:
                        entry ['number'] = Fields.Text (n)

                    if p:
                        entry ['pages'] = Fields.Text (p)

                    if o:
                        entry ['other-note'] = Fields.Text(o)

                    if y:
                        year = int(y)

                    entry ['date'] = Fields.Date((year, month, day))
                else:
                    print '>>> Error: Source field  does not parse correctly:'
                    print dict_key
                    print entry
                continue
        
        return entry

    def parse_author (self, text):
                        
        ag = Fields.AuthorGroup ()
        rx = re.compile ('\.(?:$|\s+)')
        ry = re.compile ('(.)')

        for name in rx.split (text):
            if not name: continue
            la = name.split ()
            
            if len (la) == 1:
                last, first = la[0], None
            else:
                last = ' '.join(la[:-1])
                first = la[-1]
                first = ry.sub (r'\1. ', first)
                         
            auth = Fields.Author (copy=(None, first, last, None))
            ag.append (auth)

        return ag
    
##             last = la [0]
##             if len (la) > 1:
##                 first = la [1]
##             else:
##                 first = None
##             # authors may be separated by just a single space if more
##             # than one line of authors appears in ovid file
##             if len (la) > 3:
##                 last = la [-2]
##                 first = la [-1]
##                 auth = Fields.Author ((None, first, last, None))
##                 ag.append (auth)


def writer (iter, output, mapping):

    counter = 1
    entry   = iter.first ()
    m = make_anti_mapping (mapping)
    while entry:
        write_entry (output, entry, counter, m)
        counter = counter + 1
        entry = iter.next ()
        if entry: output.write ('\n')

def write_entry (output, entry, counter, mapping):
    output.write ('<%d>\n' % counter)

    keys = entry.keys()

    write_source_field (output, entry, keys)
     
    for key in keys:
        (name, typ) = mapping.get(key, (None, None))
        if name == None or typ == SourceField: continue

        output.write (name)
        output.write('\n')
        
        if typ == SimpleField:
            write_simple_field (output, entry[key])

        elif typ == AuthorField:
            write_author_field (output, entry[key])

        elif typ == SourceField: print 'sourcefield: %s' %(entry[key])
#             write_source_field (output, entry, keys)

        elif typ == KeywordField:
            if key == 'mesh':
                offset = 4
            else:
                offset = 2
            write_simple_field (output, entry[key], offset)

    
def write_simple_field (output, value, offset=2):
    off = offset * ' '
    lines = str(value).split('\n')
    for l in lines:
        output.write(off)
        output.write (l)
        output.write ('\n')


def write_keyword_field (output, value):
    lines = str(value).split('\n')
    for line in lines:
        output.write('    ')
        output.write(line)
        output.write('\n')


def write_author_field (output, value):
    auths = [ '%s %s' % (auth.last or '', auth.first or '')
              for auth in value]
    output.write ('  ')
    output.write ('  '.join (auths))
    output.write ('\n')


def write_source_field (output, entry, keys):
    t = []

    output.write('Source\n')
    
    if entry.type == Types.get_entry(
        'incollection') or entry.has_key ('booktitle'):
        t = [str(entry.get ('booktitle')).strip()]
        
        if entry.has_key ('volume'):
            t.append (".  %s " % (entry ['volume']))
        if entry.has_key ('number'):
            t.append ("(%s)" %  (entry ['number']))

        if entry.has_key ('pages'):
            p = str (entry ['pages'])
            #p = Utils.compress_page_range (p)
            t.append ("PG. %s." %(p))

        if entry.has_key('date'):
            date  = entry['date']
            t.append (" %s" % (date.year))
        if entry.has_key ('beigabeevermerk'):
            t.append (str(entry.get('beigabevermerk')))
    else: 

        t.append ("%s. " %(entry ['journal']))

        if entry.has_key ('volume'):
            t.append ("%s" % (entry ['volume']))

        if entry.has_key ('number'):
            t.append ("(%s)" %  (entry ['number']))

        if entry.has_key ('pages'):
            p = str (entry ['pages'])
            #p = Utils.compress_page_range (p)
            t.append (":%s" %(p))

        if entry.has_key ('other-note'):
            t.append ("; %s" %(entry ['other-note']))

        if entry.has_key('date'):
            date  = entry['date']

            t.append (", %s" % (date.year))

            if date.month:
                t.append (" %s" % (month_name [date.month - 1]))
            if date.day:
                t.append (" %s" %(date.day))
        

    # final dot.
    t.append (".")
    text = ''.join (t)

    # correct the number of dots...
    #text = compact_dot.sub ('.', text)
    output.write('  ')
    output.write (text)
    output.write ('\n')






### Local Variables:
### Mode: python
### py-master-file : "ut_Ovidlike.py"
### End:

