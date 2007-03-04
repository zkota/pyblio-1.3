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

import string
import sys

Topics = {}

# --------------------------------------------------
def register (topic, help):
	''' Register a new help topic '''
	
	Topics [topic] = help


	
# --------------------------------------------------
def help (argument):
	''' The help function, as called by the main program '''

	if argument == "":
		print "Type help <topic> for specific info. Topics are:\n"
		
		tcount = 0
		topics = Topics.keys ()
		topics.sort ()
		
		for topics in topics:
			sys.stdout.write (' ' + string.ljust (topics, 20))
			tcount = tcount + 1
			if tcount > 3:
				tcount = 0
				print
		if tcount > 0:
			print
				
	else:
		if Topics.has_key (argument):
			print '-' * 70
			print " Help topic : `%s'" % argument
			print '-' * 70

			print Topics [argument]
			print
		else:
			print "error: topic `%s' not documented" % argument
		
