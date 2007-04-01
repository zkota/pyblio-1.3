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

import os, sys

from Legacy.GnomeUI.Pybliographic import Pybliographic
from Legacy.Fields import URL

from Legacy.GnomeUI import ui_version

print ui_version

main = Pybliographic ()
pyblio_path = os.environ.get ('PYBLIOGRAPHER_DATABASE', '')


if len (sys.argv) > 2:
    for file in sys.argv [2:]:
        url = URL (file)
        
        main.open_document (str (url))
elif pyblio_path:
    main.open_document (str (URL (pyblio_path)))
else:
    main.new_document ()

from twisted.internet import reactor
reactor.run()

## import gtk
## gtk.main ()
