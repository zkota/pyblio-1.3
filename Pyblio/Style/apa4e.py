# This file is part of pybliographer
# 
# Copyright (C) 1998-2003 Frederic GOBRY
# Email : gobry@idiap.ch
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
# apa4e.py based on:
# $Id: apa4e.py,v 1.1.2.2 2003/08/06 09:09:55 fredgo Exp $

# Virtually same as Generic.py with small changes
# Darrell Rudmann, rudmann@uiuc.edu
''' APA 4ed XML bibliographic style handler '''

import string

from Pyblio.Style import Parser
from Pyblio import Autoload, recode


def author_desc (group, coding, initials = 0, reverse = 0):
    """ Create a nice string describing a group of authors.

    	coding   : name of the output coding (as requested for recode)
        initials : if = 1, uses initials instead of complete first names
        reverse  :
        	-1 use First Last format
        	0  use Last, First, excepted for the first entry
        	1  use Last, First for all the authors, not only the first
    """
    
    l = len (group)
            
    fulltext = ""
    
    for i in range (0, l):
        (honorific, first, last, lineage) = group [i].format (coding)

        if initials:
            first = group [i].initials (coding)

        text = ""

        if reverse == 1 or (i == 0 and reverse == 0):
            if last:    text = text + last
            if lineage: text = text + ", " + lineage
            if first:   text = text + ", " + first
        else:
            if first:   text = first + " "
            if last:    text = text + last
            if lineage: text = text + ", " + lineage

        if text:
            if i < l - 2:
                text = text + ", "
            elif i == l - 2:
		# DSR: Use amperstand instead of "and"
                text = text + ", & "

        fulltext = fulltext + text

    # avoid a dot at the end of the author list
    if fulltext [-1] == '.':
        fulltext = fulltext [0:-1]
    
    return fulltext


def string_key (entry, fmt, table):
    
    """ Generates an alphabetical key for an entry. fmt is the
    output coding """

    rc = recode.recode ("latin1.." + fmt)

    if   entry.has_key ('author'): aut = entry ['author']
    elif entry.has_key ('editor'): aut = entry ['editor']
    else:                          aut = ()

    if len (aut) > 0:
        if len (aut) > 1:
            key = ''
            for a in aut:
                honorific, first, last, lineage = a.format (fmt)
                key = key + string.join (map (lambda x:
                                              x [0], string.split (last, ' ')), '')
                if len (key) >= 3:
                    if len (aut) > 3:
                        key = key + '+'
                    break
        else:
            honorific, first, last, lineage = aut [0].format (fmt)
            parts = string.split (last, ' ')

            if len (parts) == 1:
                key = parts [0][0:3]
            else:
                key = string.join (map (lambda x: x [0], parts), '')

    else:
        key = rc (entry.key.key [0:3])

    if entry.has_key ('date'):
        year = entry ['date'].format (fmt) [0]

        if year:
            key = key + year [2:]

    if table.has_key (key) or table.has_key (key + 'a'):

        if table.has_key (key):
            # rename the old entry
            new = key + 'a'

            table [new] = table [key]
            del table [key]

        base = key
        suff = ord ('b')
        key  = base + chr (suff)

        while table.has_key (key):
            suff = suff + 1
            key  = base + chr (suff)

    return key


def numeric_key (entry, fmt, table):
    count = 1
    while table.has_key (str (count)):
        count = count + 1

    return str (count)


def create_string_key (database, keys, fmt):
    table = {}
    for key in keys:
        s = string_key (database [key], fmt, table)
        table [s] = key

    skeys = table.keys ()
    skeys.sort ()

    return table, skeys


def create_numeric_key (database, keys, fmt):
    table = {}
    skeys = []
    for key in keys:
        s = numeric_key (database [key], fmt, table)
        table [s] = key
        skeys.append (s)
        
    return table, skeys


def standard_date (entry, coding):
    (text, month, day) = entry.format (coding)

    if month: text = "%s/%s" % (month, text)
    if day  : text = "%s/%s" % (day, text)

    return text


def last_first_full_authors (entry, coding):
    return author_desc (entry, coding, 0, 1)

def first_last_full_authors (entry, coding):
    return author_desc (entry, coding, 0, -1)

def full_authors (entry, coding):
    return author_desc (entry, coding, 0, 0)


def initials_authors (entry, coding):
    return author_desc (entry, coding, 1, 0)

def first_last_initials_authors (entry, coding):
    return author_desc (entry, coding, 1, -1)

def last_first_initials_authors (entry, coding):
    return author_desc (entry, coding, 1, 1)

# Line below changed
Autoload.register ('style', 'apa4e', {
    'first_last_full_authors'     : first_last_full_authors,
    'last_first_full_authors'     : last_first_full_authors,
    'full_authors'     : full_authors,
    'first_last_initials_authors' : first_last_initials_authors,
    'last_first_initials_authors' : last_first_initials_authors,
    'initials_authors' : initials_authors,
    'string_keys'      : create_string_key,
    'numeric_keys'     : create_numeric_key,
    'european_date'    : standard_date,
    })
