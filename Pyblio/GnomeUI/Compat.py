# This file is part of pybliographer
# 
# Copyright (C) 2005 Peter Schulte-Stracke
# Email : mail@schulte-stracke.de
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

"""
Compatability module 

 


"""

try:
    from gnome.ui import gnome_error_dialog_parented
except ImportError:
    from gnome.ui import error_dialog_parented as gnome_error_dialog_parented

error_dialog_parented = gnome_error_dialog_parented


try:
    import gnomevfs
except ImportError:
    import gnome.vfs as gnomevfs

get_mime_type = gnomevfs.get_mime_type



# Local Variables:
# coding: "latin-1"
# py-master-file: "ut_compat.py"
# End:
