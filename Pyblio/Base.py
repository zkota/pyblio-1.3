# This file is part of pybliographer
# 
# Copyright (C) 1998-2003 Frederic GOBRY
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

''' This Module contains the base classes one might want to inherit
from in order to provide a new database format '''


from string import *
import re, copy, os
import Pyblio.Help
from types import *

from Pyblio import Config, Open, Utils, Key, Iterator, Selection, Autoload

import gettext
_ = gettext.gettext



class Entry:
    '''
    A database entry. It behaves like a dictionnary, which
    returns an instance of Description for each key. For example,
    entry [\'author\'] is expected to return a Types.AuthorGroup
    instance.

    Each entry class must define an unique ID, which is used
    during conversions.

    The entry.key is an instance of Key, and has to be unique over
    the whole application.

    The entry.type is an instance of Types.EntryDescription. It
    links the field names with their type.
    '''

    id = 'VirtualEntry'

    def __init__ (self, key = None, type = None, dict = None):
	self.type = type
	self.dict = dict or {}
	self.key  = key
	return


    def keys (self):
	''' returns all the keys for this entry '''
	return self.dict.keys ()


    def has_key (self, key):
	if self.dict.has_key (key): return 1
	return 0


    def field_and_loss (self, key):
	''' return field with indication of convertion loss '''
	return self.dict [key], 0


    def __getitem__ (self, key):
	''' return text representation of a field '''

	return self.field_and_loss (key) [0]


    def __setitem__ (self, name, value):
	self.dict [name] = value
	return

	
    def __delitem__ (self, name):
	del self.dict [name]
	return


    def __add__ (self, other):
	''' Merges two entries, key by key '''

	ret = Entry (self.key, self.type, {})

	# Prendre ses propres entrees
	for f in self.keys ():
	    ret [f] = self [f]

	# et ajouter celles qu'on n'a pas
	for f in other.keys ():
	    if not self.has_key (f):
		ret [f] = other [f]

	return ret


    def __repr__ (self):
	''' Internal representation '''

	return 'Entry (%s, %s, %s)' % (`self.key`, `self.type`, `self.dict`)


    def __str__ (self):
	''' Nice standard entry  '''

	tp = self.type.name
	fields = self.type.fields

	text = '%s [%s]\n' % (tp, self.key.key)
	text = text + ('-' * 70) + '\n'

	dico = self.keys ()

	for f in fields:
	    name = f.name
	    lcname = lower (name)

	    if not self.has_key (lcname): continue

	    text = text + '  %-14s ' % name
	    text = text + Utils.format (str (self [lcname]),
					75, 17, 17) [17:]
	    text = text + '\n'

	    try:
		dico.remove (lcname)
	    except ValueError:
		raise ValueError, \
		      'multiple definitions of field `%s\' in `%s\'' \
		      % (name, tp)

	for f in dico:
	    text = text + '  %-14s ' % f
	    text = text + Utils.format (str (self [f]),
				  75, 17, 17) [17:]
	    text = text + '\n'

	return text


class DataBase:

    ''' This class represents a full bibliographic database.  It
    also looks like a dictionnary, each key being an instance of
    class Key. '''

    properties = {}

    id = 'VirtualDB'

    def __init__ (self, url):
	''' Open the database referenced by the URL '''
	self.key = url

	self.dict = {}
	return


    def has_property (self, prop):
	''' indicates if the database has a given property '''

	if self.properties.has_key (prop):
	    return self.properties [prop]

	return 1


    def add (self, entry):
	''' Adds an (eventually) anonymous entry '''

        if entry.key is None:
            # call a key generator
            keytype   = Config.get ('base/keyformat').data
            entry.key = Autoload.get_by_name ('key', keytype).data (entry, self)
        else:
            entry.key.base = self.key
            
            if self.has_key (entry.key):
                prefix = entry.key.key
                suffix = ord ('a')

                while 1:
                    key = Key.Key (self, prefix + '-' + chr (suffix))
                    if not self.has_key (key): break
                    
                    suffix = suffix + 1

                entry.key = key
            
	self [entry.key] = entry
	return entry


    def new_entry (self, type):
        ''' Creates a new entry of the native type of the database '''
        return Entry (None, type)
    

    def keys (self):
	''' Returns a list of all the keys available for the database '''

	return self.dict.keys ()


    def has_key (self, key):
	''' Tests for a given key '''

	return self.dict.has_key (key)


    def would_have_key (self, key):
        ''' Test for a key that would be set on the database '''

        return self.has_key (Key.Key (self, key.key))

    
    def __getitem__ (self, key):
	''' Returns the Entry object associated with the key '''

	return self.dict [key]


    def __setitem__ (self, key, value):
	''' Sets a key Entry '''

        key.base  = self.key
        value.key = key
	self.dict [key] = value
	return


    def __delitem__ (self, key):
	''' Removes an Entry from the database, by its key '''

	del self.dict [key]
	return


    def __len__ (self):
	''' Number of entries in the database '''

	return len (self.keys ())

    def __str__ (self):
	''' Database representation '''

	return '<generic bibliographic database (' + `len (self)` + \
	       ' entries)>'


    def __repr__ (self):
	''' Database representation '''
	
	return 'DataBase (%s)' % `self.key`


    def iterator (self):
	''' Returns an iterator for that database '''
	return Iterator.DBIterator (self)


    def update (self, sorting = None):
	''' Updates the Entries stored in the database '''
	
	if self.key.url [0] != 'file':
	    raise IOError, "can't update the remote database `%s'" % self.key

	name = self.key.url [2]

        # create a temporary file for the new version
        tmp = os.path.join (os.path.dirname (name),
                            '.#' + os.path.basename (name))
        
        tmpfile = open (tmp, 'w')

        iterator = Selection.Selection (sort = sorting).iterator (self.iterator ())
	Open.bibwrite (iterator, out = tmpfile, how = self.id)
        
	tmpfile.close ()
        
	# if we succeeded, backup file
	os.rename (name, name + '.bak')
	# ...and bring new version online
        os.rename (tmp, name)
        return

