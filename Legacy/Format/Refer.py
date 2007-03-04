# This file is part of pybliographer
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

# Extension module for Refer files

# Martin Wilck <martin@tropos.de> added support for citation label field.

from Legacy import Base, Types, Fields, Config, Autoload, Open, Iterator, Utils, Key

import re, string, sys

tag_re = re.compile ('%(.) (.*)')


class ReferDB (Base.DataBase):

    id = 'Refer'

    properties = {
        'change_id'   : 0,
        'change_type' : 0
        }
    
    def __init__ (self, url):
        Base.DataBase.__init__ (self, url)

        iter = iterator (url, 0)

        entry = iter.first ()
        while entry:
            self.add (entry)

            entry = iter.next ()

        return


class ReferIterator (Iterator.Iterator):

    def __init__ (self, file):
        self.file    = file
        self.mapping = Config.get ("refer/mapping").data
        return
    
    
    def first (self):
        # rewind the file
        self.file.seek (0)

        return self.next ()

    def next (self):
        data   = ''
        fields = {}
        type   = None
        label = None

        while 1:
	    line = self.file.readline ()
	    if line == '' and not fields:
                return None

            line = string.strip (line)
            
            if line == '' and fields:

                # store the current field
                if type:
                    if type == "label":
                        label = string.join (string.split (data), ' ')
                    elif fields.has_key (type):
                        fields [type].append (string.join (string.split (data), ' '))
                    else:
                        fields [type] = [string.join (string.split (data), ' ')]
                    

                # determine the real type
                while 1:
                    if fields.has_key ('journal'):
                        type = 'article'
                        break

                    if fields.has_key ('booktitle'):
                        type = 'inbook'
                        break

                    if fields.has_key ('volume') or fields.has_key ('number'):
                        type = 'inproceedings'
                        break

                    if fields.has_key ('publisher'):
                        type = 'book'
                        break

                    if fields.has_key ('author') and fields.has_key ('title'):
                        type = 'unpublished'
                        break
                    
                    type = 'misc'
                    break
                
                entry = Types.get_entry (type)

                for f in fields.keys ():
                    type = Types.get_field (f).type
                    
                    if type == Fields.AuthorGroup:
                        group = Fields.AuthorGroup ()
                        
                        for auth in fields [f]:
                            group.append (Fields.Author (auth))
                            
                        fields [f] = group
                        
                    else:
                        if len (fields [f]) > 1:
                            sys.stderr.write ("warning: field `%s' is defined more than once" % f)
                            continue
                        
                        fields [f] = type (fields [f] [0])
                        
                if label:
                    key = Key.Key (None, label)
                    return Base.Entry (key, entry, fields)
                else:
                    return Base.Entry (None, entry, fields)
                
            
            t = tag_re.match (line)
            # we matched a new field start
            if t:
                if type:
                    if type == "label":
                        label = string.join (string.split (data), ' ')
                    elif fields.has_key (type):
                        fields [type].append (string.join (string.split (data), ' '))
                    else:
                        fields [type] = [string.join (string.split (data), ' ')]
                    
                type = t.group (1)
                if not self.mapping.has_key (type):
                    print "warning: key `%s' has been skipped" % (type)
                    type = None
                    data = ''
                else:
                    # store the current field
                    type = self.mapping [type] [0]
                    data = t.group (2)
                    
                continue

            # in the general case, append the new text
            data = data + ' ' + line


def writer (iter, output, **argh):
    entry   = iter.first ()
    mapping = Config.get ("refer/mapping").data
    
    while entry:
        for key in mapping.keys ():

            # some fields are not to be used in output, as we
            # lost their content
            if not mapping [key] [1]: continue
            field = mapping [key] [0]

            if field == "label" and entry.key:
                output.write ('%' + key + ' ')
                output.write (Utils.format (str (entry.key.key), 75, 0, 0))
                output.write ('\n')
                continue
                
            elif entry.has_key (field):
                type = Types.get_field (field).type
                
                if type == Fields.AuthorGroup:
                    # one field per author
                    
                    for auth in entry [field]:
                        output.write ('%' + key + ' ')
                        output.write (Utils.format (str (auth), 75, 0, 0))
                        output.write ('\n')

                    continue

                # general case
                output.write ('%' + key + ' ')
                output.write (Utils.format (str (entry [field]), 75, 0, 0))
                output.write ('\n')

        entry = iter.next ()
        if entry: output.write ('\n')
    return


def iterator (url, check):
    if check and url.url [2] [-6:] != '.refer': return

    file = open (Open.url_to_local (url))

    return  ReferIterator (file)


def opener (url, check):
	
    base = None

    if (not check) or (url.url [2] [-6:] == '.refer'):
        base = ReferDB (url)
		
    return base
    
Autoload.register ('format', 'Refer',   {'open'  : opener,
                                         'write' : writer,
                                         'iter'  : iterator})

