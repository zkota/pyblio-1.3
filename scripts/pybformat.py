# -*- python -*-
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
# $Id: pybformat.py,v 1.3.2.3 2003/08/06 09:09:57 fredgo Exp $

import string, sys, os, getopt, gettext

_ = gettext.gettext

from Pyblio.Output import latexutils

from Pyblio import Base, Autoload
from Pyblio.Style import Utils

def usage ():
    sys.stderr.write (_("usage: pybformat [bibtexfiles...]\n"))
    return

def error (text, exit = 1):
    sys.stderr.write (_("pybformat: error: %s\n") % text)
    if exit:
        sys.exit (1)
    return

def warning (text, exit = 0):
    sys.stderr.write (_("pybformat: warning: %s\n") % text)
    if exit:
        sys.exit (1)
    return

optlist, args = getopt.getopt (sys.argv [2:],
			       'H:F:o:l:vhs:f:',
			       ['header=',
				'footer=',
                                'output=',
                                'list=',
                                'style=',
                                'format=',
				'version',
				'help'])

header  = None
footer  = None
outfile = sys.stdout
format  = 'text'
style   = 'Alpha'

for opt, value in optlist:
    if opt == '-H' or opt == '--header':
        header = value
        continue
    
    if opt == '-F' or opt == '--footer':
        footer = value
        continue

    if opt == '-o' or opt == '--output':
        try:
            outfile = open (value, 'w')
        except IOError, err:
            error ("can't open `%s': %s" % (value, err))
        continue

    if opt == '-l' or opt == '--list':
        try:
            list = Autoload.available (value)
        except KeyError:
            error ("unknown list `%s'" % value)
            
        if list:
            print "pybformat: available values for `%s':" % value
            print "  " + string.join (list, ", ")
            sys.exit (0)
        else:
            warning ("empty value list `%s'" % value)
            sys.exit (0)
            
    if opt == '-h' or opt == '--help':
        usage ()
        sys.exit (0)
        continue

    if opt == '-s' or opt == '--style':
        style = value
        continue

    
    if opt == '-f' or opt == '--format':
        format = value
        continue
    

    if opt == '-v' or opt == '--version':
        usage ()
        sys.exit (0)
        continue


# test input arguments
if len (args) < 1:
    # user gave wrong arguments...
    usage ()
    error ("too few arguments")

files  = args

# get the specified style and the output
output = Autoload.get_by_name ('output', format)
if output is None:
    error ("unknown output format `%s'" % format)

url = None
style = os.path.splitext (style) [0]
if os.path.exists (style + '.xml'):
    url = Fields.URL (style + '.xml')
else:
    from Pyblio import version
    full = os.path.join (version.prefix, 'Styles', style)
    full = full + '.xml'
    if os.path.exists (full): url = Fields.URL (full)

if not url:
    error (_("can't find style `%s'") % style)


sys.stderr.write ("pybformat: using style `%s', format `%s'\n" \
                  % (style, output.name))

formatter = output.data

# first, write the header
if header:
    try:
        h = open (header, 'r')
        line = '\n'
        while line:
            line = h.readline ()
            if line:
                outfile.write (line)
        h.close ()
    except IOError, err:
        error ("can't open header `%s': %s" % (header, err))

# write the data
for file in files:

    try:
        db = bibopen (file)
    except IOError, err:
        error ("can't open database: %s" % file)

    Utils.generate (url, formatter, db, db.keys (), outfile)
    
# last, write the footer
if footer:
    try:
        h = open (footer, 'r')
        line = '\n'
        while line:
            line = h.readline ()
            if line:
                outfile.write (line)
        h.close ()
    except IOError, err:
        error ("can't open footer `%s': %s" % (header, err))

        
outfile.close ()
