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

# Perform the first initialisation of Gnome, so that the options passed to the script
# are not passed to Gnome

import sys

sys.argv = sys.argv [:2] + ['--'] + sys.argv [2:]

# correctly identify the program
import pygtk
pygtk.require ('2.0')

import gnome
import gnome.ui

from Pyblio import version

gnome.init ('Pybliographer', version.version)

# clean up our garbage
sys.argv = sys.argv [:2] + sys.argv [3:]

del sys

import gtk.glade

gtk.glade.bindtextdomain ("pybliographer", version.localedir)
