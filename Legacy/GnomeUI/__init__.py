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

# Perform the first initialisation of Gnome, so that the options
# passed to the script are not passed to Gnome

import sys, string

files    = sys.argv [2:]
sys.argv = sys.argv [:2] + ['--'] + files

# correctly identify the program
import pygtk
pygtk.require ('2.0')

import gnome, gtk
import gnome.ui

from Legacy import version as pyblio_version
from Pyblio import version as core_version

prg = gnome.init ('pyblio', pyblio_version.version)
prg.set_property (gnome.PARAM_APP_DATADIR, pyblio_version.datadir)

def _vnum (t):
    return string.join (map (str, t), '.')

ui_version = _("This is Pyblio %s [Python %s, Pyblio-Core %s, Gtk %s, PyGTK %s]") % (
    pyblio_version.version, _vnum (sys.version_info [:3]), core_version,
    _vnum (gtk.gtk_version), _vnum (gtk.pygtk_version))
    
# clean up our garbage
sys.argv = sys.argv [:2] + files
del sys, files

import gtk.glade
gtk.glade.bindtextdomain ("pyblio", pyblio_version.localedir)

# this needs to be done before any import of the reactor
from twisted.internet import gtk2reactor
gtk2reactor.install()
