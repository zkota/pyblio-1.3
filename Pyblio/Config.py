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

import atexit, cPickle, os, string, sys, types

try: _
except NameError:
    def _(str) \
	: return str
    

pickle = cPickle
del cPickle

''' System for Configuration handling '''

class ConfigItem:

    def __init__ (self, name, description, vtype = None, hook = None, user = None):
        self.name        = name
        self.description = description

        # type definition
        self.type     = vtype
        
        # callback definition
        self.hook     = hook
        self.userdata = user

        self.data = None
        return

    def set (self, value):

        if self.type:
            if not self.type.match (value):
                raise ValueError (
                    _("value of `%s' should be of type %s") % (
                    self.name, str (self.type)))
            
        # eventually call the hook
        if self.hook:
            if not self.hook (self, value, self.userdata):
                raise ValueError, "value refused by hook"

        self.data = value
        return

    def get (self):
        return self.data
    

class Storage:

    def __init__ (self):
        self.items = {}
        self.sources = {}
        return


    def eventually_resolve (self, key):

        if self.items.has_key (key): return
        domain = string.split (key, '/') [0]
##	print 'DOMAIN:', domain
        if self.sources.has_key (domain):
            file = self.sources [domain]
##	    print 'READ:', self.sources [domain]
            del self.sources [domain]
            execfile (file, globals (), globals ())

        return


    def domains (self):
        # get all domains from the keys
        doms = map (lambda key: string.split (key, '/') [0], keys ())
        
        # simplify the list
        hsht = {}
        def fill_hash (key, hsht = hsht): hsht [key] = 1
        map (fill_hash, doms + self.sources.keys ())

        return hsht.keys ()

    def keys_in_domain (self, domain):
        self.eventually_resolve (domain)

        # simplify the list
        def test_dom (key, dom = domain):
            f = string.split (key, '/')
            if f [0] == dom:
                return 1
            return 0
    
        return filter (test_dom, keys ())
        
    def keys (self):
        return self.items.keys ()

    
    def has_key (self, key):
        self.eventually_resolve (key)
        return self.items.has_key (key)


    def __getitem__ (self, key):

        self.eventually_resolve (key)
        return self.items [key]
        

    def __setitem__ (self, key, value):
        self.items [key] = value
        return

    def parse_dir (self, dir):
        files = map (lambda x, dir = dir: \
                     os.path.join (dir, x), os.listdir (dir))

        for filename in files:
            if filename [-3:] == '.py':
                domain = string.lower (os.path.split (filename [:-3]) [1])
                self.sources [domain] = filename
        return

        
ConfigItems = Storage ()

def define (key, description, vtype = None, hook = None, user = None):
##    print '>>>>>>> DEFINE', key, description#, vtype, hook, user
    if ConfigItems.has_key (key):
        raise KeyError, "key `%s' already defined" % key

    ConfigItems [key] = ConfigItem (key, description, vtype, hook, user)
    return


def set (key, value):
    try:
        ConfigItems [key].set (value)
    except KeyError:
        sys.stderr.write (
            "pybliographer: warning: configuration key `%s' is undefined\n"
            % key)
    return

_changes = {}

def set_and_save  (key, value):
    set (key, value)
##    print 'SET AND SAVE:', key, value
    global _changes
    _changes [key] = value
    
def forget_changes ():
    global _changes
    _changes = {}

def get (key):
    return ConfigItems [key]


def keys ():
    return ConfigItems.keys ()


def has_key (key):
    return ConfigItems.has_key (key)


def domains ():
    return ConfigItems.domains ()


def keys_in_domain (domain):
    return ConfigItems.keys_in_domain (domain)


def parse_directory (dir):
    ConfigItems.parse_dir (dir)
    return


class PrimaryType:
    ''' Base class for simple types '''
    def match (self, value):
        return type (value) is self.type

    
    
class String (PrimaryType):
    def __init__ (self):
        self.type = types.StringType
        return

    def __str__ (self):
        return _("String")


class Boolean (PrimaryType):
    def __init__ (self):
        self.type = types.IntType
        return

    def __str__ (self):
        return _("Boolean")


class Integer (PrimaryType):
    def __init__ (self, min = None, max = None):
        self.type = types.IntType
        self.min  = min
        self.max  = max
        return

    def match (self, value):
        if not PrimaryType.match (self, value): return 0
        if self.min and value < self.min: return 0
        if self.max and value > self.max: return 0

        return 1

    def __str__ (self):
        if self.min is None and self.max is None:
            return _("Integer")
        if self.min is None:
            return _("Integer under %d") % self.max
        if self.max is None:
            return _("Integer over %d") % self.min

        return _("Integer between %d and %d") % (self.min, self.max)
    

class Element:
    def __init__ (self, elements):
        self.get = elements
        return

    def match (self, value):
        return self.get ().count (value)

    def __str__ (self):
        return _("Element in `%s'") % str (self.get ())

    
class Tuple:
    ''' A tuple composed of different subtypes '''
    
    def __init__ (self, subtypes):
        self.subtypes = subtypes
        return

    def match (self, value):
        i = 0
        for sub in self.subtypes:
            if not sub.match (value [i]):
                return 0
            i = i + 1
        
        return 1

    def __str__ (self):
        return _("Tuple (%s)") % \
               string.join (map (str, self.subtypes), ', ')
    

class List:
    ''' An enumeration of items of the same type '''

    def __init__ (self, subtype):
        self.subtype = subtype
        return

    def match (self, value):
        try:
            for v in value:
                if not self.subtype.match (v):
                    return 0
        except TypeError:
            return 0
        return 1

    def __str__ (self):
        return _("List (%s)") % str (self.subtype)
    

class Dict:
    ''' A dictionnary '''

    def __init__ (self, key, value):
        self.key   = key
        self.value = value
        return

    def match (self, value):
        try:
            for k in value.keys ():
                if not self.key.match (k):
                    return 0
                if not self.value.match (value [k]):
                    return 0
        except AttributeError, error:
            print error
            return 0
        
        return 1

    def __str__ (self):
        return _("Dictionary (%s, %s)") % (str (self.key),
                                           str (self.value))



def load_user ():
    # load the saved items
    try:
        file = open (os.path.expanduser ('~/.pybrc.conf'), 'r')
    except IOError: return

    changed = pickle.load (file)
    file.close ()

    for item in changed.keys ():
        ConfigItems.eventually_resolve (item)
        set (item, changed [item])
        
    return
        
def save_user (changed):

    if not changed:
        return
    # read what has to be saved again
    try:
        file = open (os.path.expanduser ('~/.pybrc.conf'), 'r')
        previous = pickle.load (file)
        file.close ()
    except IOError: previous = {}
    previous.update(changed)
    
    file = open (os.path.expanduser ('~/.pybrc.conf'), 'w')
    pickle.dump (previous, file)
    file.close ()
    return


#   TERMINATION ROUTINE

atexit.register(save_user, _changes)

