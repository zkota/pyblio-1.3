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


from types import *
from Pyblio import Autoload, Fields, Help, Exceptions

import urlparse, urllib, traceback, os, sys, tempfile, string, gettext

_ = gettext.gettext


def url_to_local (url):

    (file, headers) = urllib.urlretrieve (str (url))
    return file


Help.register ('bibopen', """
Syntax: database = bibopen (source)

bibopen  tries several  method  to open  `source'  as a  bibliographic
entry. `source'  can be  a simple file  or even  an URL. FTP  and HTTP
files are automatically fetched. One can even create a specific method
for client/server access for example.

One can apply the following commands on the output of bibopen :

    - database.keys () : lists the available entries
    - database ['key'] : returns a given entry
    - del database ['key'] : removes an entry from the file
    - database.where (...) : searches the base (see also `searching')
""")


def get_by_name (entity, method):
    ''' returns a specific field of the given entity '''

    meth = Autoload.get_by_name ("format", entity)

    if meth and meth.data.has_key (method):
	return meth.data [method]

    return None

def get_by_regexp (entity, method):
    ''' returns a specific field of the given entity '''

    meth = Autoload.get_by_regexp ("format", entity)

    if meth and meth.data.has_key (method):
	return meth.data [method]

    return None


def bibopen (entity, how = None):
    ''' Generic function to open a bibliographic database '''

    def simple_try (url, how):
	base = None

	if how == None:
	    listedmethods = Autoload.available ("format")

	    for method in listedmethods:
		opener = get_by_name (method, 'open')
		if opener:
		    base = opener (url, 1)
		    if base is not None:
			return base
	    return None

	opener = get_by_name (how, 'open')

	if opener:
	    base = opener (url, 0)
	else:
	    raise Exceptions.FormatError (_("method `%s' provides no opener") % how)

	return base

    # Consider the reference as an URL
    url = Fields.URL (entity)

    if url.url [0] == 'file' and not os.path.exists (url.url [2]):
	raise Exceptions.FileError (_("File `%s' does not exist") % str (url))

    # eventually load a new module
    if how is None:
	handler = Autoload.get_by_regexp ("format", str (url))
	if handler:
	    how = handler.name

    base = simple_try (url, how)

    if base is None:
	raise Exceptions.FormatError (_("don't know how to open `%s'") % entity)

    return base


def bibiter (entity, how = None):
    ''' Generic function to iterate on a bibliographic database '''

    def simple_try (url, how):
	base = None

	if how == None:
	    listedmethods = Autoload.available ('format')

	    for method in listedmethods:
		opener = get_by_name (method, 'iter')
		if opener:
		    base = opener (url, 1)
		    if base is not None:
			return base
	    return None

	opener = get_by_name (how, 'iter')

	if opener:
	    base = opener (url, 0)
	else:
	    raise Exceptions.FormatError (_("method `%s' provides no iterator") % how)

	return base

    # Consider the reference as an URL
    url = Fields.URL (entity)

    if url.url [0] == 'file' and not os.path.exists (url.url [2]):
	raise Exceptions.FileError (_("File `%s' does not exist") % str (url))

    # eventually load a new module
    if how is None:
	handler = Autoload.get_by_regexp ('format', str (url))
	if handler:
	    how = handler.name

    base = simple_try (url, how)

    if base is None:
	raise Exceptions.FormatError (_("don't know how to open `%s'") % entity)

    return base


Help.register ('bibwrite', """
Syntax: bibwrite (iterator, output, how)

This function sends an entry description to the specified output
(stdout by default), formatted as specified by the third argument. By
default, this formatting is the same as the one used by `more'.
""")


def bibwrite (iter, out = None, how = None):
    ''' writes a descriptions of a list of entries '''

    # default output
    out = out or sys.stdout

    if how == None:
	entry = iter.first ()
	while entry:
	    out.write (str (entry) + "\n")
	    entry = iter.next ()

	return

    writer = get_by_name (how, 'write')

    if writer is None:
	raise IOError, "type `%s' does not specify write method" % how

    writer (iter, out)
    return


Help.register ('bibnew', """
Syntax: bib = bibnew (name, type)

Creates a new bibliographic database of a given type.
""")

def bibnew (name, type = None):

    opener = get_by_name (type, 'new')

    if opener is None:
	if os.path.exists (name):
	    raise IOError, "file `%s' exists" % name

	file = open (name, 'w')
	file.close ()

	return bibopen (name, type)

    # Consider the reference as an URL
    url = list (urlparse.urlparse (name))

    if url [0] == '':
	# Consider we handle a local file
	url [0] = 'file'
	url [2] = os.path.expanduser (url [2])

    return opener (url)
