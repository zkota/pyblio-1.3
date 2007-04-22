#! @python_path@
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

version  = "@version@"
progname = "@package@"

data_pybdir = "@datapyb@"
localedir   = "@localedir@"

import sys

sys.path.insert (0, data_pybdir)
sys.path.insert (0, '.')

import locale
locale.setlocale (locale.LC_ALL, '')

import gettext
gettext.install (progname, localedir, unicode = True)

charset = locale.getlocale () [1] or 'ascii'

def print_version ():
	print (_("This is %s, version %s") % (progname, version)).encode (charset)

def copyright ():
	print 'Copyright (C) 1998-2004 Frederic GOBRY'
	print _("This is free software with ABSOLUTELY NO WARRANTY.").encode (charset)
	print _("For details, type `warranty'.").encode (charset)

def warranty ():
	print_version ()
	print 'Copyright (C) 1998-2004 Frederic GOBRY'
	
	print _("This is free software with ABSOLUTELY NO WARRANTY.").encode (charset)
	print """
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, write to the Free Software
Foundation, 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
"""
	
import os
import getopt, string

sys.ps1 = 'python > '

optlist, args = getopt.getopt (sys.argv [1:],
			       'qf:nvh',
			       ['quiet',
				'file=',
				'version',
				'help'])

sys.argv = sys.argv [0:1] + args
try:
	sys.argv.remove ('--')
except ValueError: pass

quiet = 0

try:             os.stat ("pybrc.py")
except os.error: sources = [ os.path.join (data_pybdir, "pybrc.py") ]
else:  	         sources = [ "pybrc.py" ]

sources.append (os.path.expanduser('~/.pybrc.py'))
load_config = 1

for opt, value in optlist:
	if opt == '-q' or opt == '--quiet':
		quiet = 1
		continue
	
	if opt == '-n':
		sources = []
		load_config = 0
		continue

	if opt == '-f' or opt == '--file':
		try:
			os.stat (value)
		except os.error:
			print (_("%s: error: can't open file `%s'") \
			      % (progname, value)).encode (charset)
			sys.exit (1)
		
		sources.append (value)
		continue

	if opt == '-v' or opt == '--version':
		print_version ()
		sys.exit (0)

	if opt == '-h' or opt == '--help':
		print_version ()
		print (_("For help, run %s and type `help' at the prompt") 
		       % progname).encode (charset)
		sys.exit (0)
		
# ---------- Initialisation

if not quiet:
	print_version ()
	copyright ()
	print _("Useful commands:\n	help     to get some help\n	quit     to quit\n").encode (charset)

# ---------- Load default schemas, set logging
from Pyblio import Registry
Registry.parse_default()

if False:
	from Pyblio import init_logging
	import logging

	init_logging()
	logging.getLogger('pyblio').setLevel(logging.DEBUG)

# ---------- Lire les fichiers de conf

user_global = {'__builtins__' : __builtins__,
	       '__name__'     : progname,
	       }

user_local  = {}


# Fichiers standards
for filename in sources:
	try:
		os.stat (filename)
	except os.error:
		pass
	else:
		execfile (filename, user_global)

if load_config:
	from Legacy import Config
	Config.load_user ()

# Fichiers passes en argument au programme
if len (args) > 0 :
	filename = args [0]
	try:
		os.stat (filename)
	except os.error:
		print (_("%s: error: can't open file `%s'") % (progname, filename)).encode (charset)
		sys.exit (1)
	else:
		execfile (filename, user_global)

	# Quand on a tout lu, le programme est fini !
	sys.exit (0)

import re, traceback
import code
import Legacy.Help
import string

try:
	import readline
except ImportError:
	pass

# ---------- Initialisations du parser
simplecom = re.compile ("^\s*(!|help|exit|quit|warranty)\s+(.*)$")
emptycomm = re.compile ("^\s*(#.*)?$")

full_line = ""
finished  = 0
prompt    = ">> "
inner = 0


while not finished:
	
	try:
		line = raw_input (prompt)
	except EOFError:
		finished = 1
		continue
	except	KeyboardInterrupt:
		print
		full_line = ""
		prompt = ">> "
		inner = 0
		continue

		
	what = simplecom.match (line + " ")
	
	if not inner and emptycomm.match (line) <> None:
		continue
	
	if what <> None:
		command = what.group (1)
		if command == "help":
			Legacy.Help.help (string.strip (what.group (2)))
			continue
		elif command == "quit" or command == "exit":
			finished = 1
			continue
		elif command == "warranty":
			warranty ()
			continue
		elif command == "!":
			os.system (what.group (2))
			continue
	else:
		full_line = full_line + "\n" + line

	try:
		user = code.compile_command (full_line);
		
		if user == None and line <> "":
			prompt = "..."
			inner = 1
		else:
			exec (user, user_global)
			full_line = ""
			prompt = ">> "
			inner = 0
			    
	except:
		etype, value, tb = sys.exc_info ()
		traceback.print_exception (etype, value, tb)

		full_line = ""
		prompt = ">> "
		inner = 0
	

# save history
