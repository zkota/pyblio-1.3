# -*- python -*-
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

# This script processes a text file with citations and creates a
# reference list according to the given style.
# Created by Zoltán Kóta. March, 2004.
'''Processing keys in a text file and appending a reference list'''

import string, os, re, copy, gettext, sys, getopt
from shutil import copyfile

from Pyblio import Base, Key, Autoload
from Pyblio.Style import Utils

_ = gettext.gettext

from Pyblio import pybtextvar

def usage ():
    print _("usage: pybtext [-o outputfile] [-s style] <textfile> <bibfiles...>")
    return

def error (msg):
    sys.stderr.write (_("pybtext: error: %s\n") % msg)
    sys.exit (1)
    return

def warning (msg, exit = 0):
    sys.stderr.write (_("pybtext: warning: %s\n") % msg)
    if exit:
        sys.exit (1)
    return


optlist, args = getopt.getopt (sys.argv [2:],
			       'o:s:',
			       ['output=',
                                'style='])

# test input arguments
if len (args) < 2:
    usage ()
    sys.exit (1)


# set defaults if no option
outfile = args [0] + '.pyb'
style   = 'Abbrev'

# get option values
for opt, value in optlist:
    if opt == '-o' or opt == '--output':
        outfile = value
        continue

    if opt == '-s' or opt == '--style':
        style = value
        continue


# get the specified style
url = None
style = os.path.splitext (style) [0]
if os.path.exists (style + '.xml'):
    url = Fields.URL (style + '.xml')
else:
    from Pyblio import version
    full = os.path.join (version.pybdir, 'Styles', style)
    full = full + '.xml'
    if os.path.exists (full): url = Fields.URL (full)

if not url:
    error (_("can't find style `%s'") % style)


spstyle = os.path.split (style) [1]


# adjust parameters to the chosen style
if spstyle == 'abbrvau':
    sep = '; '
    format = 'textau'

elif spstyle == 'abbrvnum':
    sep = ', '
    format = 'textnum'
else:
    sep = ', '
    format = 'text'


# get the specified output
output = Autoload.get_by_name ('output', format)

if output is None:
    error ("unknown output format `%s'" % format)



reffile = outfile + '.ref'

if os.path.exists(outfile):
    error ("File already exists: `%s'" % outfile)

if os.path.exists(reffile):
    error ("The file `%s' to be used for creating the reference list already exists." % reffile)

textfile = args [0]
bibfile = args [1:]


# regular expression to match in the text file
citation_re = re.compile ('\[([^\]]+)\]')


# this function extracts the citation keys from the text file
def list_entries (file):
    
    try:
        txt = open (textfile, 'r')
    except IOError, err:
        error ('%s: %s' % (textfile, err))
    
    citations = []

    # parse the whole file
    while 1:
        line = txt.readline ()

        if line == '': break

        line = string.strip (line)

        # we match new citations
        match = citation_re.findall (line)

        if match:

            for citationkey in match:

                # splitting multiple citations
                ckeys = string.split (citationkey, ',')

                for a in ckeys:
                    citations.append (a)


    txt.close ()
    return citations


# getting citation keys
entries = list_entries (textfile)

# is there something to do ?
if len (entries) == 0:
    error (_("no citation found"))


# ensure citation keys unicity preserving citation order
h = []
for e in entries:
    if h.count (e) >= 1:
        continue
    h.append (e)
entries = h

# storing citation order
order = copy.copy (entries)


sys.stderr.write ("pybtext: using style `%s', format `%s'\n" \
                  % (style, output.name))

formatter = output.data


# we have to create a new database to hold the entries found in the
# given databases

r = Base.DataBase (None)

# use the bibliographic databases in order of declaration
# to solve the references

for bib in bibfile:

    # open the database
    db = bibopen (bib)

    # as we are modifying the list of entries in this loop, we make a copy
    # of it in order to avoid strange behaviors
    orig = copy.copy (entries)

    # loop over the expected entries
    for e in orig:

        # create a key in the current database
        key = Key.Key (db, e)

        # does the database provide the key ?
        if db.has_key (key):
            
            # yes, add it to the reference
            r [key] = db [key]

            # and remove it from the list
            entries.remove (e)

    # if we found some entries in the current database...
    if len (r) > 0:
        pass

    # is it finished ?
    if len (entries) == 0: break


# check if we were able to solve all the citations
if len (entries) > 0:
    error (_("can't find the following entries: %s")
           % string.join (entries, ", "))


# creating an ordered list of database keys to pass through
keys = map (lambda x: Key.Key (r, x), order)


# creating the reference list
try:
    refs = open (reffile, 'w')
except IOError, err:
    error ("can't open `%s': %s" % (reffile, err))

refs.write ("\n\nReferences:\n")

Utils.generate (url, formatter, r, keys, refs)

refs.close ()


# getting the old-new key pairs
oldnew = pybtextvar.oldnew


# Now we check the textfile again to replace bibdb keys
# to the new keys if it is needed

if oldnew:

    try:
        txt = open (textfile, 'r')
    except IOError, err:
        error ('%s: %s' % (textfile, err))

    try:
        dest = open (outfile, 'a')
    except IOError, err:
        error ("can't open `%s': %s" % (outfile, err))

    citations = []
    
    # parse the textfile
    while 1:
        line = txt.readline ()

        if line == '': break

        # we match a new citation
        match = citation_re.findall (line)

        if match:

            for citationkey in match:

                # splitting multiple citations
                citations = string.split (citationkey, ',')

                old = '[' + citationkey + ']'
                new = ''
                for a in citations:
                    new = new + oldnew.get (a) + sep

                new = '[' + new [0:len (new) - 2] + ']'
                out = line.replace (old, new, 1)
                line = out
                citations = []

        dest.write (line)

    txt.close ()

else:
    try:
        copyfile (textfile, outfile)
    except:
        error ("can't create `%s'" % outfile)

    try:
        dest = open (outfile, 'a')
    except IOError, err:
        error ("can't open `%s': %s" % (outfile, err))


# appending the reference list
try:
    refs = open (reffile, 'r')
except IOError, err:
    error ('%s: %s' % (reffile, err))

while 1:
    line = refs.readline ()
    if line == '': break
    dest.write (line)
     
refs.close ()

dest.close ()

try:
    os.remove (reffile)
except:
    warning ("can't remove `%s'" % reffile)

print "Done"
