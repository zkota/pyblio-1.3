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


"""
Handling of on-demand loading of python extensions.

To register a module to be autoloaded,
call:

  preregister (group, name, module, regexp = None, info = None):

This is done especially in pybrc.py. The group define the family of
feature this module provides. The name is the specific module display
name, and module is the effective name of the python module.

Then, when an application calls a Autoload.get_by...() function, the
actual module is imported if it was not loaded before. Upon import,
the module is expected to call Autoload.register to define which entry
point it provides.
"""

import os, string, re, gettext, sys

_ = gettext.gettext

class Loader:
    ''' An object containing the description of a loadable object '''
    
    def __init__ (self, name, regexp, module,
                  info = None, data = None):
        self.name   = name
        
        if regexp:
            self.regexp = re.compile (regexp)
        else:
            self.regexp = None
            
        self.module = module
        self.info   = info
        self.data   = data
        
        self.loaded = 0
        return

    def load (self, key = None):

        if self.regexp and key:
            if not self.regexp.search (key):
                return 0

        if self.loaded: return 1

        # ok, load the module
        try:
            exec ('import ' + self.module)
        except ImportError, err:

            import locale
            charset = locale.getlocale () [1]
            
            print (_("warning: can't import %s: %s") %
                   (self.module, str (err))).encode (charset)
            return 0
        
        self.is_loaded ()
        return 1


    def is_loaded (self):
        self.loaded = 1
        return


__loaders = {}

def preregister (group, name, module, regexp = None, info = None):
    ''' Register a module for autoloading.

      - group: generic feature group this module belongs to (format, output,...)

      - name: actual display name of the module

      - module: logical python module that must be imported

      - regexp: a regexp that helps selecting, for instance, handlers
        for a given file type.

      - info: ?

    '''

    # get info from the given group
    if __loaders.has_key (group):
        gp = __loaders [group]
    else:
        gp = {}
        __loaders [group] = gp

    lc = string.lower (name)
    # are we preregistering an existing key ?
    if gp.has_key (lc):
        return gp [lc]
    
    lo = Loader (name, regexp, module, info)
    gp [lc] = lo
    
    return lo


def register (group, name, data = None):
    ''' Register when the module is actually loaded '''

    mod = get_by_name (group, name, 0) or preregister (group, name, None)
    mod.is_loaded ()
    mod.data = data
    
    return


def get_by_regexp (group, key):
    ''' Returns a loaded module according to a key that it must match '''

    if not __loaders.has_key (group):
        return None
    
    gp = __loaders [group]
    
    for l in gp.values ():
        if l.load (key):
            return l
    
    return None


def get_by_name (group, name, load = 1):
    ''' Returns a loaded module according to its name '''
    
    if not __loaders.has_key (group):
        return None

    gp = __loaders [group]
    lc = string.lower (name)
    
    if gp.has_key (lc):
        l = gp [lc]
        if not load or l.load ():
            return l

    return None


def available (group):
    ''' Returns the list of available modules in a group '''
    
    return map (lambda x: x.name, __loaders [group].values ())


def groups ():
    ''' Returns a list of the groups '''
    return __loaders.keys ()
