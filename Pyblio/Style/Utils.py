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

from Pyblio.Style import Parser
from Pyblio import Fields, Autoload

def generate (style_url, format, database, keys, output):
    
    fmt = format (output)
    p = Parser.XMLBib (style_url)
    p.configure ()

    (table, keys) = p.methods ['keys'] (database, keys, fmt.coding)

    fmt.start_group ('')
    for key in keys:
        entry = database [table [key]]
        p.format.output (entry, fmt, key)
    
    fmt.end_group ()
    return
