# This file is part of pybliographer
#  
# Original author of Ovid reader: Travis Oliphant <Oliphant.Travis@mayo.edu>
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
# $Id: Ovid.py,v 1.7.2.1 2003/08/06 09:09:52 fredgo Exp $

""" Extension module for Ovid files """

from Pyblio.Format import OvidLike
from Pyblio import Base, Open, Config, Types, Autoload

import string

class Ovid (Base.DataBase):

    id = 'Ovid'
    
    properties = {
        'change_id'   : 0,
        'change_type' : 0
        }

    def __init__ (self, url):
        Base.DataBase.__init__ (self, url)

        iter = iterator (url, 0)

        entry = iter.first ()
        while entry:
            self.add (entry)

            entry = iter.next ()

        return

    
def opener (url, check):
	
    base = None
	
    if (not check) or (url.url [2] [-5:] == '.ovid'):
        base = Ovid (url)
		
    return base


def iterator (url, check):
    ''' This methods returns an iterator that will parse the
    database on the fly (useful for merging or to parse broken
    databases '''

    if check and url.url [2] [-5:] != '.ovid': return

    file = open (Open.url_to_local (url))
    
    type = Config.get ('ovid/deftype').data
    
    return  OvidLike.OvidLike (file, Config.get ('ovid/mapping').data,
                               type)


def writer (iter, output):
    
    mapping = Config.get ('ovid/mapping').data
    OvidLike.writer (iter, output, mapping)

    return

        
Autoload.register ('format', 'Ovid', {'open'  : opener,
                                      'write' : writer,
                                      'iter'  : iterator})


