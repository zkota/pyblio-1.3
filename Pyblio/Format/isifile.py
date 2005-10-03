#This file is part of Pybliographer
# 
# Copyright (C) 1998-2004 Peter Schulte-Stracke
# Email : mail@schulte-stracke.de
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

try: _
except NameError:
    def _ (str)\
	: return str

import getpass, re, rfc822, string, time, types

from Pyblio import Autoload, Base, Fields, Iterator, Open, Types, Utils
login_name = getpass.getuser()

key_map = {
    'AB' : ('abstract', ' '),
    'AU' : ('author', '  '),
    'CR' : ('citedref', ' ; '),
    'C1' : ('authoraddress', ' ; '),
    'DE' : ('keywords', ' '),
    'ED' : ('editor', ' '),
    'IS' : ('number', ' ; '),
    'LA' : ('language', ' ; '),
    'PA' : ('address', ' ; '),
    'PD' : ('month', ' ; '),
    'PU' : ('publisher', ' ; '),
    'PY' : ('date', ' ; '),
    'SE' : ('series', ' '),
    'SN' : ('issn', ' ; '),
    'SO' : ('journal', ' ; '),
    'TI' : ('title', ' '),
    'UT' : ('sourceid', ' ; '),
    'VL' : ('volume', ' ; ')}


xheader  = re.compile('^(\w\w|\w\w+:)( (.*))$')
header   = re.compile('^(\w\w)( (.*))$')
contin   = re.compile('^   (.*)$') 
sporadic = re.compile('^isifile-(..)$')

field_map = None

def reverse_mapping(map):
    remap = {}
    for key in map.keys():
        remap[map[key][0]] = key
    return remap


output = None                  # set by 

def output_write(key, text):
    # A text is either a string or a list:
    if type(text) == types.ListType:
        output.write ('%2s %s\n' %(key, text[0]))
        for t in text[1:]:
            output.write ('   %s\n' %(t))
    elif str(text):    
        output.write ('%2s %s\n' % (key, Utils.format(
            str (text), 70, 0, 3)))
pagenum  = re.compile('(\d) p\.')
keywds   = re.compile('(.*)\[ISI:\] *(.*);;(.*)')

class IsifileIterator(Iterator.Iterator):
    ''' This class exports two functions: first and next,
    each of which returns an bibliographic entry from the input file.
    In addition is saves extraneous text (pre- and postamble).'''

    def __init__(self, file):
        self.file = file
        self.extraneous = []
        self.isifileformat = None
        self.isifileinfo = None
        
    def first(self):
        self.file.seek(0)
        return self.next()

    def next (self):
        
        lines = {}
        in_table = {}
        file_notes, file_time, file_version, file_format = ('','','','')

        while 1:
            line = self.file.readline()
            if line == '': return lines # what does that mean ??
            head = xheader.match(line)
            if not head :
                pass
            elif head.group(1) == 'Date:':
                file_time = time.strftime(
                    "%Y-%m-%d %H:%M", rfc822.parsedate(head.group(2)))
            elif head.group(1) == 'Notes:':
                file_notes = string.strip(head.group(2))
            elif head.group(1) == 'FN':
                file_format = head.group(2)
            elif head.group(1) == 'VR':
                file_version = head.group(2)
            elif len(head.group(1)) == 2 :
                break
            else :
                pass
            self.extraneous.append(line)

        self.isifileformat = self.isifileformat or "Isifile format %s(%s)" % (
            file_format, file_version)
        self.isifileinfo = self.isifileinfo or "ISI %s (%s) %s" %(
            file_time, file_notes, login_name)

        
        while 1:
            if line == 'ER':break
            if head :
                key = head.group(1)
                if key == 'ER': break
                val = head.group(3)
                if lines.has_key(key):
                    lines[key].append(val)
                else:
                    lines[key] = [val]
            else:
                cont = contin.match(line)
                if cont :
                    val = cont.group(1)
                    lines[key].append(val)
                else: break
            line = self.file.readline()
            if line == '': break # error situation
            head = header.match (line)

        
        key = 'PT'
        if lines.has_key(key):
            if string.strip(lines[key][0])[0] == 'J':
                del lines [key]
            else:
                print 'Warning: Unknown type of entry (%s) -- may need editing.' %(
                    lines[key])
        
        type = Types.get_entry ('article')
            

	for key in ( 'AU', 'ED'):
	    if lines.has_key(key):
		field = Types.get_field('author')
		group = Fields.AuthorGroup()
		for item in lines[key]:
		    if string.strip(item) =='[Anon]' :
			auth = [item]
		    else:        
			name, firstn = string.split (item, ',')
			auth = ["%s, " % name]
			for i in string.strip (firstn):
			    auth.append ("%s. " % i)
		    group.append (Fields.Author("".join(auth)))
		if key == 'AU':
		    in_table['author'] = group
		elif key == 'ED':
		    in_table['editor'] = group
		del lines[key]                  

        key, key1, key2 = 'PG', 'BP', 'EP'
        if lines.has_key(key1) and lines.has_key(key2):
            if len(lines[key1]) == len(lines[key2]):
                pages = []
                for i in range(len(lines[key1])):
                    firstpg = lines[key1] [i]
                    lastpg  = lines[key2] [i]                      
                    pages.append(('%s -- %s' % (firstpg, lastpg)))
                in_table['pages'] = Fields.Text (string.join(pages, '; '))
                del lines[key1]; del lines[key2]
            else: print 'inconsistent BP, EP fields found'
         
        if lines.has_key(key):
            in_table['size'] = Fields.Text ('%s p.' %(lines[key][0]))
            del lines[key]
            

        key = 'PY'
        if lines.has_key(key):
            val = lines[key][0]
            in_table['date'] = Fields.Date(val)
            del lines[key]

        key = 'ID'
        if lines. has_key(key):
            val = "[ISI:] %s ;;" %(string.lower(string.join(lines[key], ' ')))
            if lines.has_key('DE'):
                lines['DE'].append ('; ' + val)
            else :
                lines['DE'] = [val]
            del lines[key]

        # journal titles come in various forms
       
        if lines.has_key ('SO'):
            uc_title =  ' '.join(lines['SO'])
            in_table ['journal'] = Fields.Text (uc_title)
            if lines.has_key('JI'):
                uc_title = re.split(r"([- .,/]+)", uc_title)
                ca_title = re.split(r"[- .,/]+", ' '.join(lines['JI']))
                i , Title = 0, []
                for word in uc_title:
                    Word = string.capitalize(word)
                    if word == ca_title [i]:
                        Title.append (word)
                        i += 1
                    elif Word.startswith(ca_title[i]):
                        Title.append(Word)
                        i += 1
                    else:
                        Title.append(string.lower(word))
                del lines['JI']
                in_table['journal'] =  Fields.Text ("".join(Title))
            del lines['SO']



        for key in lines.keys():
            mapped_key, joiner = key_map.get(
                key, ('isifile-%s' %(key.lower()), ' ; '))
            text_type = Types.get_field (mapped_key).type
            in_table [mapped_key] = text_type (joiner.join(lines[key]))

        return Base.Entry ( None, type, in_table)

class Isifile (Base.DataBase):
    '''Read a Isifile format database from an URL.'''
    id = 'Isifile'
    
    properties = {
        'change_id'   : 0,
        'change_type' : 0
        }

    def __init__ (self, url):
        Base.DataBase.__init__ (self, url)

        iter = iterator (url, 0)
        entry = iter.first ()
        self.preamble = iter.extraneous
        while entry:
            self.add (entry)
            entry = iter.next ()
        self.postamble = iter.extraneous    
        return


re_page = re.compile (r'\s*-+\s*')

def writer (iter, output_stream, preamble=None, postamble = None):
    '''Write data given by an iterator, as well as an
    optional pre- and postamble, onto an output stream.'''

    remaining = {}
    text = []
    global field_map, output
    output = output_stream
    field_map = field_map or reverse_mapping(key_map)
    if preamble: output.writelines(preamble)
    output_write('FN', 'ISI Export Format')
    output_write('VR', '1.0')
    entry = iter.first()
    while entry:
        
        remaining = {}
        remaining_extra = {}
        
        for fld in entry.keys():
            if field_map.has_key(fld):
                remaining[fld] = field_map[fld]
            else:
                m = sporadic.match(fld)
                if m:
                    remaining[fld] = string.upper(m.group(1))
                else:
                    remaining [fld] = '%% * ' + fld + ' * '
                    remaining_extra [fld] = '%% * ' + fld + ' * '
        
        if not entry.has_key('isifile-pt'):
            output_write('PT','J')

        if entry.has_key ('author'):
            authors = []
            for author in entry['author']:
                initials = author.initials()
                initials = re.sub('\. *','', initials)
                authors.append( '%s, %s' % (author.last, initials))
            del remaining ['author']    
            output_write('AU', authors)    

        fld = 'title'
        if entry.has_key(fld):
            output_write('TI',str(entry[fld]))
            del remaining[fld]

        fld = 'journal'
        if entry.has_key(fld):
            output_write('SO',string.upper(str(entry[fld])))
            del remaining[fld]
        fld = 'pages'
        if entry.has_key (fld):
            for pair in string.split (str(entry[fld]), ' ; '):
                beginpg, endpg = re_page.split(pair)
                output_write('BP', beginpg)
                output_write('EP', endpg)
            del remaining[fld]
            

        fld = 'size'
        if entry.has_key(fld) :
            m = pagenum.match(str(entry[fld]))
            if m :
                output_write('PG', m.group(1))
            del remaining[fld]

        fld = 'month'
        if entry.has_key(fld):
            output_write('PD',string.upper(str(entry[fld])))
            del remaining[fld]

        fld = 'citedref'
        if entry.has_key(fld):
            output_write('CR',string.split(str(entry[fld]), ' ; '))
            del remaining[fld]

        fld = 'keywords'
        if entry.has_key(fld):
            val = str(entry[fld])
            m = keywds.match (val)
            if m:
                output_write('ID', string.upper(m.group(2)))
                val = m.group(1) + m.group(3)
            output_write ('DE', val)     
            del remaining[fld]
        for field in remaining.keys():
            if remaining_extra.has_key (field): continue
            output_write (remaining[field], entry [field])
        for field in remaining_extra.keys():
            output_write (remaining_extra [field], entry [field])
        output.write('ER\n')     
        entry = iter.next()
        if entry: output.write('\n')
    if postamble: output.writelines(postamble)
    

def opener (url, check):

        base = None
        if (not check) or (url.url [2] [-4:] == '.isi'):
                base = Isifile (url)
        return base


def iterator (url, check):
        ''' This methods returns an iterator that will parse the
        database on the fly (useful for merging or to parse broken
        databases '''

        if check and url.url [2] [-4:] != '.isi': return
        
        return IsifileIterator (open (Open.url_to_local (url), 'r'))

Autoload.register ('format', 'Isifile', {'open': opener,
                                         'write': writer,
                                         'iter': iterator})



### Local Variables:
### Mode: python
### py-master-file : "ut_Isi.py"
### End:

