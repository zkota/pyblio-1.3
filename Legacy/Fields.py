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

from Legacy import Exceptions, Key

import copy, os, re, recode, string, time, types, urlparse

year_match = re.compile ('(\d\d\d\d)')

formatter_cache = {}

def get_formatter (format):
    ''' This function is used to get a recode formatter in an
    efficient way '''
    
    format = string.lower (format)
    
    if formatter_cache.has_key (format):
        ft = formatter_cache [format]
    else:
        ft = recode.recode ('latin1..' + format)
        formatter_cache [format] = ft

    return ft


class Author:
    ''' Fine description of an author '''

    def __init__ (self, copy = None, strict = 0):
        ''' Initialize an author from a string or an other Author '''

        if type (copy) is types.StringType:
            # manually split the author into subfields.
            self.honorific = None
            self.lineage   = None

            blocs = string.split (copy, ',')
            
            if len (blocs) == 1:
                if strict:
                    # strict parsing, the whole block is the last name
                    self.last  = blocs [0]
                    self.first = None
                else:
                    # lazy parsing, last name is after lowercase or is last word
                    words = map (string.strip, string.split (blocs [0]))
                    i = 0
                    while i < len (words) - 1:
                        if words [i] == string.lower (words [i]): break
                        i = i + 1
                    
                    self.first = string.join (words [:i], ' ')
                    self.last  = string.join (words [i:], ' ')
                    
            elif len (blocs) == 2:
                self.last  = string.strip (blocs [0])
                self.first = string.strip (blocs [1])
                
            elif len (blocs) == 3:
                self.last    = string.strip (blocs [0])
                self.lineage = string.strip (blocs [1])
                self.first   = string.strip (blocs [2])

            else:
                self.last  = copy
                self.first = None

            # cleanup
            if self.last == '':    self.last    = None
            if self.first == '':   self.first   = None
            if self.lineage == '': self.lineage = None
                        
        else:
            if copy:
                def clean_entry (f):
                    if f is not None:
                        f = string.strip (f)
                        if f == '': f = None

                    return f
               
                copy = map (clean_entry, copy)
                self.honorific = copy [0]
                self.first     = copy [1]
                self.last      = copy [2]
                self.lineage   = copy [3]
            else:
                self.honorific = None
                self.first     = None
                self.last      = None
                self.lineage   = None

        self.text = None
        return


    def format (self, fmt = 'latin1'):
        ''' Returns the fields in a given format '''
        
        ft = get_formatter (fmt)
        
        return (ft (self.honorific), ft (self.first),
                ft (self.last), ft (self.lineage))

    
    def __str__ (self):
        ''' Returns textual representation '''

        if not self.text:
            text = ''
            if self.honorific: text = text + ' ' + self.honorific
            if self.last:      text = text + ' ' + self.last
            if self.lineage:   text = text + ', ' + self.lineage
            if self.first:     text = text + ', ' + self.first
            self.text = text [1:]
            
        return self.text


    def __repr__ (self):
        return 'Author ((%s, %s, %s, %s))' % (`self.honorific`, `self.first`,
                                              `self.last`, `self.lineage`)


    def match (self, regex):
        ''' '''
        return regex.search (str (self))


    def initials (self, format = None):
        ''' Extract initials from a first name '''

        total = []

        if self.first is None: return ''
        
        for atom in string.split (self.first, ' '):
            list = []
            
            for word in string.split (atom, '-'):
                list.append (word [0] + '.')
                
            total.append (string.join (list, '-'))
            
        text = string.join (total, ' ')
        if format:
            ft = get_formatter (format)
            text = ft (text)

        return text

    def __cmp__ (self, other):
        ''' field comparison '''
        
        r = cmp (self.last, other.last)
        if r != 0: return r

        r = cmp (self.first, other.first)
        if r != 0: return r

        r = cmp (self.lineage, other.lineage)
        if r != 0: return r
        
        r = cmp (self.honorific, other.honorific)
        if r != 0: return r

        return 0


class AuthorGroup:
    ''' A group of Authors '''

    def __init__ (self, text = ''):
        self.authors = []
        return

    def __getitem__ (self, pos):
        return self.authors [pos]

    def __setitem__ (self, pos, val):
        self.authors [pos] = val
        self.val.touch ()
        return

    def __len__ (self):
        return len (self.authors)

    def append (self, value):
        self.authors.append (value)
        
    def __str__ (self):
        return string.join (map (str, self.authors), '; ')

    def __repr__ (self):
        return 'AuthorGroup (%s)' % `self.authors`

    def match (self, regex):
        return regex.search (string.join (map (str, self.authors), ' '))

    def __cmp__ (self, other):
        i = 0
        try:
            s = len (self), len (other)
        except TypeError:
            return 1
        
        m = max (s)
        
        while i < m:
            if i >= s [0]: return -1
            if i >= s [1]: return +1

            r = cmp (self [i], other [i])
            if r != 0: return r

            i = i + 1

        return 0
            

class Date:
    ''' Fine description of a date '''

    def __init__ (self, arg = (None, None, None)):

        if type (arg) is types.StringType:
            try:
                year  = int (arg)
            except ValueError:
                g = year_match.search (arg)
                if g:
                    year = int (g.group (1))
                else:
                    year = None
                
            month = None
            day   = None
        else:
            year, month, day = arg
        
        if year and year < 0:
            raise Exceptions.DateError (_("Illegal year value"))
        self.year = year
        
        if month and (month < 1 or month > 12):
            raise Exceptions.DateError (_("Illegal month value"))
        self.month = month
        
        if day and (day < 1 or day > 31):
            raise Exceptions.DateError (_("Illegal day value"))
        self.day = day

        self.text = None
        return


    def __cmp__ (self, other):

        s = self.year  or -1
        o = other.year or -1
        
        diff = s - o
        if diff: return diff

        s = self.month  or -1
        o = other.month or -1
        
        diff = s - o
        if diff: return diff

        s = self.day  or -1
        o = other.day or -1
        
        return s - o


    def __str__ (self):
        ''' Returns textual representation '''

        if not self.text:
            if self.year and self.month and self.day:
                self.text = '%d/%d/%d' % (self.day, self.month, self.year)

            elif self.year and self.month:
                self.text = '%d/%d' % (self.month, self.year)
            
            elif self.year:
                self.text = str (self.year)

            else:
                self.text = ''
                
        return self.text


    def format (self, fmt = 'latin1'):
        ''' Returns the fields in a given format '''
        ft = get_formatter (fmt)

        if self.year:
            year = ft (str (self.year))
        else: year = None

        if self.month:
            month = ft (str (self.month))
        else: month = None

        if self.day:
            day = ft (str (self.day))
        else: day = None

        return year, month, day

    
    def __repr__ (self):
        return 'Date (\'%s\')' % str (self)


    def match (self, regex):
        ''' '''
        return regex.search (str (self))

    def asInt (self):
        v = self.year * 10000
        if self.month:
            v += self.month * 100
        if self.day:
            v += self.day
        return v
    
class Text:
    ''' This class holds all the other fields (not an Author or a Date) '''

    def __init__ (self, text):
        self.text = text
        return


    def __str__ (self):
        return str (self.text)


    def __repr__ (self):
        return 'Text (%s)' % `self.text`


    def match (self, regex):
        '''   '''
        return regex.search (self.text)


    def __cmp__ (self, other):
        return cmp (self.text, str (other))


    def format (self, fmt = 'latin1'):
        ''' Returns the fields in a given format '''
        ft = get_formatter (fmt)

        return ft (self.text)


class LongText (Text) :
    """This subclass of text is used for long texts,
    i.e. notes and abstracts. """

    def __str__  (self):
        return self.text
    
    def __repr__ (self):
        return 'LongText (%s)' % `self.text`

    def __len__  (self):
        return len (self.text)

    def __getitem__ (self, key):
        return self.text[key]
    
   
class URL:
    ''' Holder for URL data (for example, the location of a database) '''

    def __init__ (self, url, invalid=False,
		  inexact=False, date='', note=''):
	"""Accepts as first argument either a string (extended
	syntax, as parsed by parse_full), or a tuple as used by urllib."""
	
	self.invalid = invalid
	self.inexact = inexact
	self.date = date
	self.note = note
	
	try:
	    url = url.strip ()
	    self.parse_full (url)
	except AttributeError:
	    self.url = ['', '', '', '', '', '']

	    # N.B. six fields in lieu of five, because we
	    # are using (deprecated) URLPARSE in lieu of
	    # URLSPLIT --ptr.
	    
        if self.url [0] == '':
            # Consider we handle a local file
            self.url [0] = 'file'
            self.url [2] = os.path.expanduser (self.url [2])
            if not os.path.isabs (self.url [2]):
                self.url [2] = os.path.normpath (os.path.join (os.getcwd(), self.url [2]))

        return

    def set (self, other):
	self.url = other .url
	self.invalid = other.invalid
	self.inexact = other.inexact
	self.date = other.date
	self.note = other.note

    def full (self):
	a = (self.invalid and u'!') or u''
	b = (self.inexact and u'*') or u''
	d = (self.date and '|') or ''
	n = (self.note and '|') or ''
	return u"%s%s%s%s%s%s%s" %( a, b, self.get_url (),
				    d, self.date, n, self.note)

    rx = re.compile ("\s*(!?\*?)([^|]*)(:?\|([^|]*)(:?\|([^|]*))?)?")

    def parse_full (self, s):
	"""Parse string s encoding invalid and inexact flags and
	containig date and note subfields"""
	
	m = self.rx.match (s)
	if m:
	    ii, us, fil1, date, fil2, note = m.groups ()
	    self.invalid |= ii.startswith ('!')
	    self.inexact |= ii.endswith ('*')
	    self.url =  list (urlparse.urlparse (us))
	    self.date = date or self.date
	    self.note = note or self.note
	else:
	    print 'ERROR PARSING URL:', s
	    self.note = "ERROR PARSING THIS URL"
	
    def match (self, regex):
        ''' '''
        return regex.search (str (self))
        
    def __cmp__ (self, other):
        return cmp (self.url, other.url)

    def __hash__ (self):
        return hash (str (self))

    def __str__ (self):
        return self.full ()
    
    def __repr__ (self):
        return 'URL (%s)' % `urlparse.urlunparse (self.url)`

    def get_url (self):
	return urlparse.urlunparse (self.url)
	

class Reference:
    ''' Holder for a reference to a bibliographic entry (which can be
    a crossref, a link to related entries, ... '''

    def __init__ (self, keylist, database = None):
        
        if type (keylist) is types.StringType:
            self.list = map (lambda k, db = database: Key.Key (db, string.strip (k)),
                             string.split (keylist, ','))
        else:
            self.list = keylist
        return
    
    def __str__ (self):
        body = []
        # get the list of databases
        dbs = {}
        for refs in self.list:
            dbs [refs.base] = 1

        for db in dbs.keys ():
            keys = []
            for refs in self.list:
                if refs.base == db:
                    keys.append (refs.key)
            body.append ('(' + string.join (keys, ', ') + ') ' +
                         _("in %s") % db)
        
        return 'Reference on %s' % string.join (body, ', ')


    def __repr__ (self):
        return 'Reference (%s)' % `self.list`


    def match (self, regex):
        '''   '''
        for key in self.list:
            ret = regex.search (str (key))
            if ret: return ret
        return None


    def __cmp__ (self, other):
        return cmp (self.list, other.list)


    def format (self, fmt = 'latin1'):
        ''' Returns the fields in a given format '''
        ft = get_formatter (fmt)

        return map (ft, self.list)

