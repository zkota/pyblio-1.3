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
# $Id: FieldsInfo.py,v 1.4.2.2 2003/08/06 09:09:53 fredgo Exp $

from Pyblio import Config
import string


def width (field):
    ''' return the graphical width of a field given its name '''
    
    ht = Config.get ('base/fields').data

    field = string.lower (field)
    
    if ht.has_key (field) and hasattr (ht [field], 'width'):
        return ht [field].width
    else:
        return Config.get ('gnomeui/default').data [0]


def justification (field):
    ''' returns the representative widget of a field '''
    
    ht = Config.get ('base/fields').data

    field = string.lower (field)
    
    if not ht.has_key (field):
        return Config.get ('gnomeui/default').data [1]
    
    if hasattr (ht [field], 'justification'):
        return ht [field].justification
    
    if hasattr (ht [field].type, 'justification'):
        return ht [field].type.justification

    return Config.get ('gnomeui/default').data [1]


def widget (field):
    ''' returns the representative widget of a field '''

    default = Config.get ('gnomeui/default').data [2]
    
    ht = Config.get ('base/fields').data
    
    field = string.lower (field)

    if not ht.has_key (field):
        return default
    
    if hasattr (ht [field], 'widget'):
        return ht [field].widget
    
    if hasattr (ht [field].type, 'widget'):
        return ht [field].type.widget

    return default
        
