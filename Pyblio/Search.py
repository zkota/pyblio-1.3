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

''' In this module are defined the search operators that can be applied
in a Selection '''

from string import *
import re

# ----- Boolean tests -----

class Bool:
    ''' Base class for boolean tests '''

    def __init__ (self):
	self.neg = 0

    def __or__ (self, other):
	return OrConnect (self, other)

    def __and__ (self, other):
	return AndConnect (self, other)

    def __neg__ (self):
	self.neg = not self.neg
	return self


class Tester (Bool):
    '''
    A concrete test on a given field.

    field : name of the field being tested ('title', ...)
    value : regular expression it should match

    Example:

    t = Tester ('author', 'weigend')
    if t.match (entry): ...
    '''

    def __init__ (self, field, value):
	Bool.__init__ (self)
	self.__test = re.compile (value, re.IGNORECASE)

	self.field = lower (field)
	self.value = value
	return

    def match (self, entry):
	if self.neg:
	    # Negative test
	    if entry.has_key (self.field):
		field = entry [self.field]
		return field.match (self.__test) == None
	    else:
		return 1
	else:
	    if entry.has_key (self.field):
		field = entry [self.field]
		return field.match (self.__test) != None
	    else:
		return 0

    def __str__ (self):
	if self.neg:
	    return "%s !~ %s" % (self.field, self.value)
	else:
	    return "%s ~ %s" % (self.field, self.value)


class KeyTester (Bool):
    ''' Test against a key '''

    def __init__ (self, value):
	Bool.__init__ (self)
	self.__test = re.compile (value, re.IGNORECASE)

	self.value = value
	return

    def match (self, entry):
	if self.neg:
	    # Negative test
	    ret = self.__test.match (entry.key.key) is None
	else:
	    ret = self.__test.match (entry.key.key) is not None

	return ret

    def __str__ (self):
	if self.neg:
	    return "<Key> !~ %s" % (self.value)
	else:
	    return "<Key> ~ %s" % (self.value)


class TypeTester (Bool):
    ''' Test against an entry type '''


    def __init__ (self, value):
	Bool.__init__ (self)

	self.value = value
	return

    def match (self, entry):
	if self.neg:
	    # Negative test
	    return entry.type != self.value
	else:
	    return entry.type == self.value

    def __str__ (self):
	if self.neg:
	    return "<Type> != %s" % (self.value)
	else:
	    return "<Type> = %s" % (self.value)


class DateTester (Bool):
    ''' True if entry is older (younger if neg) than the
    one specified '''

    def __init__ (self, field, date):
	Bool.__init__ (self)
	self.field = field
	self.date = date
	return

    def match (self, entry):
	if not entry.has_key (self.field):
	    return 1

	field = entry [self.field]

	if self.neg:
	    return field >= self.date
	else:
	    return field <= self.date

    def __str__ (self):
	if self.neg:
	    return "%s >= %s" % (self.field, str (self.date))
	else:
	    return "%s <= %s" % (self.field, str (self.date))


class AnyTester (Bool):
    ''' Test against all the fields	'''

    def __init__ (self, value):
	Bool.__init__ (self)
	self.__test = re.compile (value, re.IGNORECASE)
	self.value = value
	return

    def match (self, entry):
	if self.neg:
	    # Negative test
	    for f in entry.keys ():
		field = entry [f]
		if field.match (self.__test) is not None:
		    return 0
	    return 1
	else:
	    # if any of the fields matches, the whole matches
	    for f in entry.keys ():
		field = entry [f]
		if field.match (self.__test) is not None:
		    return 1
	    return 0

    def __str__ (self):
	if self.neg:
	    return "<Any Field> !~ %s" % (self.value)
	else:
	    return "<Any Field> ~ %s" % (self.value)


class Connecter (Bool):
    ''' Virtual class connecting two tests '''

    def __init__ (self, left, right):
	Bool.__init__ (self)
	self.left = left
	self.right = right


class OrConnect (Connecter):
    ''' Connects two tests by a boolean OR.

    Example :
    t = OrConnect (Test ('title', 'time'), Test ('author', 'weigend'))

    ...but usually :

    t = Test ('title', 'time') | Test ('author', 'weigend')
    will create the same object. '''

    def match (self, entry):
	ret = (self.left.match (entry) or
	       self.right.match (entry)) 
	if self.neg:
	    ret = not ret

	return ret

    def __str__ (self):
	return "(%s) or (%s)" % (str (self.left), str (self.right))

class AndConnect (Connecter):
    ''' Connects two tests by a boolean AND	'''

    def match (self, entry):
	ret = (self.left.match (entry) and
		self.right.match (entry))  
	if self.neg:
	    ret = not ret

	return ret

    def __str__ (self):
	return "(%s) and (%s)" % (str (self.left), str (self.right))

