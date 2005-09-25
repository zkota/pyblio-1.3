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

# Extension module for BibTeX files

import _bibtex
import os, sys, tempfile, pwd, time, traceback, re, string, copy

from types import *
from Pyblio.Fields import *
from Pyblio import Base, Config, Autoload, Types
from Pyblio import Open, Key, Utils, Iterator, Exceptions

# this database is shared between all the unpickled entries
_unpickle_db = _bibtex.open_string ("<unpickled>", '', 0);

_base_fieldtype = {
    Text        : 0,
    LongText    : 0,
    Date        : 3,
    AuthorGroup : 1,
    URL         : 4,
    Reference   : 4,
    }

_text_fieldtype = Config.get ('bibtex+/capitalize').data

def _fieldtype (field):
    if field.type is not Text:
        return _base_fieldtype [field.type]

    name = string.lower (field.name)
    
    if not _text_fieldtype.has_key (name):
        return 0
    
    if _text_fieldtype [name]:
        return 2

    return 0


extended_date = re.compile ('^[\{"]?\s*(\d+)\s*[\}"]?\s*#\s*(\w+)$')


class BibTextField (Text):
    ''' This class overrides the basic Text class and provides
    a specific method to write the entries as latex code '''

    def __init__ (self, text, native):
	Text.__init__ (self, text)
	self.native = native
	return

    def format (self, fmt):

	if string.lower (fmt) == 'latex':
	    return self.native

	return Text.format (self, fmt)


class BibLongTextField (LongText):
    ''' This class overrides the basic LongText class and provides
    a specific method to write the entries as latex code '''

    def __init__ (self, text, native):
	LongText.__init__ (self, text)
	self.native = native
	return

    def format (self, fmt):

	if string.lower (fmt) == 'latex':
	    return self.native

	return LongText.format (self, fmt)


class Entry (Base.Entry):
    ''' This class holds a BibTeX entry and keeps a reference on
    its parser '''

    id = 'BibTeX'

    def __init__ (self, key, fieldtype, content, parser, line):
	Base.Entry.__init__ (self, key, fieldtype, content)

	self.__text = {}
	self.parser = parser
        self.line   = line
        
	# Check for date fields
	datefields = Config.get ('bibtex/datefield').data
	convert    = Config.get ('bibtex/months').data

	for field in datefields.keys ():
	    (yearfield, monthfield) = datefields [field]
	    
	    # check if this entry provides a date field
	    if not self.has_key (yearfield): continue

            day   = None
	    month = None
            try:
                year = int (self [yearfield].text)
            except ValueError:
                break
            
	    del self [yearfield]

	    if self.has_key (monthfield):
		mt = _bibtex.get_native (self.dict [monthfield])

		if convert.has_key (mt):
		    month = convert [mt]
		    del self [monthfield]
                else:
                    df = extended_date.match (mt)
                    if df:
                        (gd, gm) = (df.group (1), df.group (2))
                        if convert.has_key (gm):
                            month = convert [gm]
                            try:
                                day   = int (gd)
                            except ValueError:
                                pass
                            
                            del self [monthfield]

	    self [field] = Date ((year, month, day))
	return


    def __delitem__ (self, key):
	# First, eventually remove from cache
	if self.__text.has_key (key):
	    del self.__text [key]

	del self.dict [key]
	return


    def set_native (self, key, value):
        if self.__text.has_key (key):
            del self.__text [key]

        try:
            self.dict [key] = _bibtex.set_native (value, 0)
        except IOError, err:
            raise Exceptions.ParserError ([str (err)])
        return

    
    def __setitem__ (self, key, value):

	# First, set the cache for free
	self.__text [key] = (value, 0)

        if isinstance (value, Date): return
        
        # then, convert as bibtex.
        if isinstance (value, Reference):
            value = string.join (map (lambda item: item.key, value.list), ', ')
            
	self.dict [key] = _bibtex.reverse (_fieldtype (Types.get_field (key)),
                                           Config.get ('bibtex+/braces').data,
                                           value)
	return


    def has_key (self, key):
        return self.__text.has_key (key) or self.dict.has_key (key)


    def keys (self):
        keys = {}

        def set_key (x, keys = keys):
            keys [x] = 1
            return
        
        map (set_key, self.__text.keys ())
        map (set_key, self.dict.keys ())

        return keys.keys ()

    
    def __deepcopy__ (self, memo):
        # copy the native fields
        content = {}
        for field in self.dict.keys ():
            value = _bibtex.copy_field (self.dict [field])
            content [field] = value

        entry = Entry (copy.deepcopy (self.key, memo),
                       copy.deepcopy (self.type, memo),
                       content,
                       self.parser, self.line)

        # add the cached fields
        for field in self.__text.keys ():
            if entry.has_key (field): continue
            entry [field] = self [field]

        return entry


    def __getstate__ (self):
        # transform the entry in a non-bibtex entry (as we don't keep
        # the specific information anyway, like @String,...)
        content = {}
        for field in self.keys ():
            content [field] = self [field]

        return Base.Entry (self.key, self.type, content)


    def __setstate__ (self, state):
        self.dict   = {}
        self.type   = state.type
        self.key    = state.key
        self.__text = state.dict
        self.parser = _unpickle_db
        self.line   = 0
        
        for field in state.keys ():
            self [field] = state [field]
        return

    
    def get_latex (self, key):
	''' Returns latex part '''

	return _bibtex.get_latex (self.parser,
                                  self.dict [key],
                                  _fieldtype (Types.get_field (key)))


    def field_and_loss (self, key):

	# look in the cache first
	if self.__text.has_key (key):
	    return self.__text [key]

	obj = self.dict [key]

	# search its declared type

	fieldtype = Types.get_field (key)
	ret  = _bibtex.expand (self.parser, obj,
                               _fieldtype (fieldtype))

        fieldtype = fieldtype.type
        
	if fieldtype == AuthorGroup:
	    # Author
	    val = AuthorGroup ()
	    for aut in ret [3]:
		val.append (Author (aut))

	elif fieldtype == Date:
	    # Date
	    val = Date ((ret [3], None, None))

	elif fieldtype == LongText:
	    # Annotation text
	    val = BibLongTextField (ret [2], self.get_latex (key))

	elif fieldtype == Text:
	    # Any other text
	    val = BibTextField (ret [2], self.get_latex (key))

        elif fieldtype == Reference:
            # a reference on the same database
            val = Reference (ret [2], self.key.base)
            
        else:
            # specific fields, like URL
            val = fieldtype (ret [2])
            
	self.__text [key] = (val, ret [1])

	return (val, ret [1])



class BibtexIterator (Iterator.Iterator):

    def __init__ (self, db, parser):
	self.db     = db
	self.parser = parser
	return

    def first (self):
	_bibtex.first (self.parser)
	return self.next ()

    def next (self):
        try:
            retval = _bibtex.next (self.parser)
        except IOError, error:
            raise Exceptions.ParserError ((str (error),))
        
	if retval == None: return None

	name, fieldtype, offset, line, object = retval

        if name:
            key = Key.Key (self.db, name)
        else:
            key = None
        
	fieldtype  = Types.get_entry (fieldtype)
	entry = Entry (key, fieldtype, object, self.parser, line)

	return entry
	
		
class DataBase (Base.DataBase):

    id = 'BibTeX'

    def __init__ (self, basename):
	''' Initialisation '''

	Base.DataBase.__init__ (self, basename)
	self.__parsefile__ ()
	return


    def __parsefile__ (self):
	self.dict   = {}

	# Ouvrir le fichier associe
	self.parser = _bibtex.open_file (Open.url_to_local (self.key),
					 Config.get ('bibtex/strict').data)

	# Incorporer les definitions de l'utilisateur
	if not Config.get ('bibtex+/override').data:
	    user = Config.get ('bibtex/macros').data
	    valid = re.compile ('^\w+$')

	    for k in user.keys ():
		if not valid.match (k):
		    raise TypeError, _("key `%s' is malformed") % k

		_bibtex.set_string (self.parser, k,
				    _bibtex.reverse (_base_fieldtype [Text],
                                                     Config.get ('bibtex+/braces').data,
						     user [k] [0]))

	finished = 0
	errors = []

	# Creer la base de cles
	iter  = BibtexIterator (self, self.parser)

        try:
            entry = iter.first ()

            if entry is not None:
                if entry.key is None:
                    self.add (entry)
                else:
                    if self.dict.has_key (entry.key):
                        errors.append (_("%s:%d: key `%s' already defined") % (
                            str (self.key), entry.line, entry.key.key))
                    else:
                        self.dict [entry.key] = entry
                
        except Exceptions.ParserError, err:
            errors.append (str (err))

	while 1:
            try:
                entry = iter.next ()
            except Exceptions.ParserError, err:
                errors.append (str (err))
                continue

            if entry is None: break

            if entry.key is None:
                self.add (entry)
            else:
                if self.dict.has_key (entry.key):
                    errors.append (_("%s:%d: key `%s' already defined") % (
                        str (self.key), entry.line, entry.key.key))
                else:
                    self.dict [entry.key] = entry

        
	if len (errors) > 0:
	    raise Exceptions.ParserError (errors)

	# Incorporer les definitions de l'utilisateur
	if Config.get ('bibtex+/override').data:
	    user  = Config.get ('bibtex/macros').data
	    valid = re.compile ('^\w+$')

	    for k in user.keys ():
		if not valid.match (k):
		    raise TypeError, _("key `%s' is malformed") % k

		_bibtex.set_string (self.parser, k,
				    _bibtex.reverse (_base_fieldtype [Text],
                                                     Config.get ('bibtex+/braces').data,
						     user [k] [0], 0))
	return



    def __str__ (self):
	''' '''
	return '<BibTeX database `%s\' (%d entries)>' % \
	       (self.key, len (self))


    def get_native (self, entry):
	''' Return the object in its native format '''

	stream = Utils.StringStream ()
	entry_write (entry, stream)

	return stream.text


    def create_native (self, value):
	''' Parse text in native format '''

	parser = _bibtex.open_string ("<set_native string>", value,
				      Config.get ('bibtex/strict').data)

	iter  = BibtexIterator (self, parser)

	entry = iter.first ()
	if entry:
	    # set the entry parser to the current one, so
	    # that we keep the current string definitions
	    entry.parser = self.parser

	return entry


    def new_entry (self, type):
        return Entry (None, type, {}, self.parser, 1)
    

# ==================================================

def _nativify (field, fieldtype):
    ''' private method to convert from field to native format '''

    obj = _bibtex.reverse (fieldtype, Config.get ('bibtex+/braces').data,
                           field, 1)
    return _bibtex.get_native (obj)


def entry_write (entry, output):
    ''' Print a single entry as BiBTeX code '''

    native = isinstance (entry, Entry)

    tp = entry.type

    # write the type and key
    output.write ('@%s{%s,\n' % (tp.name, entry.key.key))

    # create a hash containing all the keys, to keep track
    # of those who have been already written
    dico = {}
    datefields = Config.get ('bibtex/datefield').data
    convert    = Config.get ('bibtex/months').data
    # we have to handle the special case of the dates
    # create the list of months
    monthlist  = range (0, 12)
    for key in convert.keys ():
        monthlist [convert [key] - 1] = key

    dateformat = Config.get ('bibtex+/dateformat').data
    
    if native:
	# loop over all the fields
	for field in entry.keys ():

	    if datefields.has_key (field):
		# we are processing a date...
		date = entry [field]

		dico [datefields [field] [0]] = str (date.year)
		if date.month:
                    month = monthlist [date.month - 1]
                    if date.day:
                        month = dateformat % {'day':    date.day,
                                              'month' : month}
                        
		    dico [datefields [field] [1]] = month
			 

	    else:
		# we are processing a normal entry
		dico [field] = _bibtex.get_native (entry.dict [field])

    else:
	for field in entry.keys ():
	    # convert the field in a bibtex form
	    if datefields.has_key (field):
		# we are processing a date...
		date = entry [field]

		dico [datefields [field] [0]] = str (date.year)
		if date.month:
                    month = monthlist [date.month - 1]
                    if date.day:
                        month = dateformat % {'day':    date.day,
                                              'month' : month}
                        
		    dico [datefields [field] [1]] = month
			 

	    else:
		# we are processing a normal entry
                value = entry [field]

                # eventually convert the crossref
                if isinstance (value, Reference):
                    value = string.join (map (lambda item: item.key, value.list), ', ')
                    
                fieldtype = _fieldtype (Types.get_field (field))

                dico [field] = _nativify (value, fieldtype)


    first = True
    
    # write according to the type order
    for f in tp.mandatory + tp.optional:

	# dico contains all the available fields
	field = string.lower (f.name)
	if not dico.has_key (field): continue

        if not first: output.write (',\n')
        else:         first = False
            
	output.write ('  %-14s = ' % f.name)
        output.write (Utils.format (dico [field],
                                    75, 19, 19) [19:])
	del dico [field]

    keys = dico.keys ()
    keys.sort ()
    
    for f in keys:
        if not first: output.write (',\n')
        else:         first = False
            
	output.write ('  %-14s = ' % f)
	output.write (Utils.format (dico [f],
				   75, 19, 19) [19:])

    output.write ('\n}\n\n')
    return


def writer (it, output):
    ''' Outputs all the items refered by the iterator <it> to the
    <stdout> stream '''

    # write header
    if Config.get ('base/advertise').data:
        output.write ('@comment{This file has been generated by Pybliographer}\n\n')

    # locate the entries that belong to a BibTeX database
    # and those who contain crossreferences
    field_table = Config.get ('base/fields').data
    crossref    = None
    
    for key in field_table.keys ():
        if field_table [key].type == Reference:
            crossref = key
            break
    
    header = {}
    refere = {}
    entry  = it.first ()
    while entry:
        if isinstance (entry, Entry):
	    header [entry.key.base] = entry
            
        if entry.has_key (crossref):
            refere [entry.key] = entry
            
	entry = it.next ()

    # write the string definitions corresponding to these entries
    if len (header) > 0:
	user = Config.get ('bibtex/macros').data

	for entry in header.values ():
	    # write the list of strings
	    dict = _bibtex.get_dict (entry.parser)
	    if len (dict.keys ()) == 0: continue

	    for k in dict.keys ():
		if not (user.has_key (k) and user [k][1] == 0):
		    output.write ('@String{ ')
		    value = _bibtex.get_native (dict [k])
		    output.write ('%s \t= %s' % (k, value))
		    output.write ('}\n')

	    output.write ('\n')

    # write the crossreferenced ones
    for entry in refere.values ():
        entry_write (entry, output)
    
    # write the entries with no cross references
    entry = it.first ()
    while entry:
        if not refere.has_key (entry.key):
            entry_write (entry, output)
	entry = it.next ()

    return


def opener (url, check):
    ''' This methods returns a new BibTeX database given a URL '''

    base = None

    if (not check) or url.url [2] [-4:] == '.bib':
	base = DataBase (url)

    return base


def iterator (url, check):
    ''' This methods returns an iterator that will parse the
    database on the fly (useful for merging or to parse broken
    databases '''

    if check and url.url [2] [-4:] != '.bib': return None

    # Ouvrir le fichier associe
    parser = _bibtex.open_file (Open.url_to_local (url),
				Config.get ('bibtex/strict').data)

    # create a database to generate correct keys
    db = Base.DataBase (url)

    return BibtexIterator (db, parser)


Autoload.register ('format', 'BibTeX', {'open'  : opener,
					'write' : writer,
					'iter'  : iterator})

