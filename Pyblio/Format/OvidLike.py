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

from Pyblio import Iterator, Base, Fields, Exceptions, Utils

SimpleField  = 0
AuthorField  = 1
SourceField  = 2
KeywordField = 3

separator_re = re.compile (r'<\d+>$')
source_re    = re.compile (r'(\w+)?\(([^\)]+)\):(\d+-\d+)')
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


class OvidLike (Iterator.Iterator):

    def __init__ (self, file, mapping, deftype):
        self.file    = file
        self.deftype = deftype
        self.mapping = mapping
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
            
            raise Exceptions.ParserError (["bad file format"])
        
        return self.next ()

    
    def next (self):
        dict = {}
        
        # read entry till next blank line
        text  = ''
        field = ''
        while 1:
            line = self.file.readline ()
            if line == '': break

            line = string.rstrip (line)

            if line == '': continue
            
            # starting with a blank ?
            if line [0] == ' ':
                # ...then we continue the current text
                text = text + ' ' + string.lstrip (line)
                continue

            # new entry ?
            if separator_re.match (line): break

            # else, this is a new field
            if field:
                # save the previous one if needed
                dict [field] = text
                text = ''

            # store the name of this new field
            field = string.lower (line)

        # don't waste the last field content
        if field:
            dict [field] = text

        # did we parse a field ?
        if len (dict) == 0: return None
        
        # create the entry content
        entry = Base.Entry (type = self.deftype)

        for key in dict.keys ():
            if not self.mapping.has_key (key):
                print "warning: unused key `%s'" % key
                continue

            (name, type) = self.mapping [key]

            # parse a simple text field
            if type == SimpleField:
                entry [name] = Fields.Text (string.strip (dict [key]))
                continue

            if type == KeywordField:
                text = string.strip (dict [key])
                if entry.has_key (name):
                    text = str (entry [name]) + '  ' + text
                    
                entry [name] = Fields.Text (text)
                continue

            # parse an author field
            if type == AuthorField:
                ag = Fields.AuthorGroup ()

                for names in string.split (dict [key], '  '):
                    la = string.split (names)

                    last = la [0]
                    if len (la) > 1:
                        first = la [1]
                    else:
                        first = None

                    auth = Fields.Author ((None, first, last, None))
                    ag.append (auth)

                    # authors may be separated by just a single space if more
                    # than one line of authors appears in ovid file
                    if len (la) > 3:
                        last = la [-2]
                        first = la [-1]
                        auth = Fields.Author ((None, first, last, None))
                        ag.append (auth)

                entry [name] = ag
                continue

            # parse a source field
            if type == SourceField:
                # separate fields by ,
                fields = string.split(dict [key], ',')

                if len (fields) == 1:
                    print "warning: can't parse source"
                    continue

                journalName = string.strip(fields [0])
                # extract volume, number, pages, ...
                for i in range(1, len(fields)):
                    fs = string.strip(fields[i])
                    if fs[0:4] == 'vol.':
                        entry ['volume'] = Fields.Text (fs[4:])
                    elif fs[0:3] == "no.":
                        entry ['number'] = Fields.Text (fs[3:])
                    elif fs[0:3] == "pp.":
                        fss = string.split(fs,'.')
                        entry ['pages'] = Fields.Text(fss[1])
                        journalName = journalName + ","\
                                      + string.join(fss[2:], '.')
                        # the date field precedes pages
                        fss = string.split(fields[i-1])
                        # we have to work from the end since there may be
                        # characters unrelated to the date at the start of the
                        # field
                        try:
                            year = int(fss[-1])
                        except:
                            year  = None
                            print "warning: cannot parse year"
                            print "offending line:", dict[key]
                        try:
                            month = long_month [fss[-2][:3]]
                        except:
                            month = None
                        try:
                            day = int(fss[-3])
                        except:
                            day   = None
                        entry ['date'] = Fields.Date((year, month, day))
                    else:
                        # additional information we do not want to loose
                        journalName = journalName + ", " + fs
                        
                # the journal name and additional information
                entry [name [0]] = Fields.Text (journalName)
                continue

            raise TypeError, "unknown field type `%d'" % type
        
        return entry


def writer (iter, output, mapping):

    counter = 1
    entry   = iter.first ()

    while entry:
        output.write ('<%d>\n' % counter)
        counter = counter + 1

        for key in mapping.keys ():
            (name, type) = mapping [key]
            key = string.capwords (key)

            if type == SimpleField:
                if not entry.has_key (name): continue
                output.write (key + '\n')

                output.write (Utils.format (str (entry [name]),
                                            75, 2, 2) + '\n')
                continue

            if type == AuthorField:
                if not entry.has_key (name): continue
                output.write (key + '\n')

                auths = map (lambda auth: '%s %s' % (auth.last or '', auth.first or ''),
                             entry [name])

                output.write ('  ' + string.join (auths, '  ') + '\n')
                continue

            if type == SourceField:
                # do we have one of those fields ?
                if not (entry.has_key (name [0]) or
                        entry.has_key (name [1]) or
                        entry.has_key (name [2]) or
                        entry.has_key (name [3]) or
                        entry.has_key (name [4])): continue
                output.write (key + '\n')

                text = ''
                if entry.has_key (name [0]):
                    # put the title
                    text = text + str (entry [name [0]]) + '. '

                has_source = 0
                vals = ['', '', '']
                for i in range (0, 3):
                    if entry.has_key (name [i + 1]):
                        has_source = 1
                        vals [i] = str (entry [name [i + 1]])

                if has_source:
                    text = text + '%s(%s):%s' % tuple (vals)

                if entry.has_key (name [4]):
                    if has_source:
                        text = text + ', '

                    date = entry [name [4]]
                    text = text + str (date.year)
                    if date.month:
                        text = text + ' ' + month_name [date.month - 1]
                    if date.day:
                        text = text + ' ' + str (date.day)

                # final dot.
                if text: text = text + '.'

                # correct the number of dots...
                text = compact_dot.sub ('.', text)
                
                output.write (Utils.format (text,
                                            75, 2, 2) + '\n')
                
        entry = iter.next ()
        if entry: output.write ('\n')

    return
