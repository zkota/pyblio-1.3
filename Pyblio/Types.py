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

import string, copy
from Pyblio import Config, Fields


def get_entry (entry, has_default = 1):
    ''' Returns an entry description given its name '''

    entries = Config.get ("base/entries").data

    if entries.has_key (entry):
	return entries [entry]

    if has_default:
	return EntryDescription (entry)

    return None


def get_field (field):
    ''' return a field description given its name '''
    
    fields = Config.get ("base/fields").data

    if fields.has_key (field):
        return fields [field]

    return FieldDescription (field)


class FieldDescription:
    ''' Available informations for a given field type '''

    def __init__ (self, name, type = Fields.Text):
	self.name = name
	self.type = type
	return

    def __deepcopy__ (self, memo):
        return FieldDescription (self.name, self.type)


    def __cmp__ (self, other):
        return cmp (self.name, other.name)

    
    def __str__ (self):
	return "`%s' field" % self.name


class EntryDescription:
    ''' Informations on a given entry '''

    def __init__ (self, name):
	self.name       = name

	self.__dict__ ['mandatory'] = []
	self.__dict__ ['optional']  = []
	return


    def __cmp__ (self, other):
        return cmp (string.lower (self.name), string.lower (other.name))

    
    def __str__ (self):
	return "`%s' entry" % self.name


    def __getattr__ (self, attr):
	if attr == 'fields':
	    return self.mandatory + self.optional

	raise AttributeError, 'no such attribute: %s' % attr

    def __setattr__ (self, attr, value):

	if attr == 'mandatory' or attr == 'optional':
	    self.__dict__ [attr] = value
	    self.__dict__ ['lcfields'] = {}

	    for f in self.fields:
		self.__dict__ ['lcfields'] [string.lower (f.name)] = f

	    return

	self.__dict__ [attr] = value
	return
        

