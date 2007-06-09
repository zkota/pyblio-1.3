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

''' Main Module holding all the documents '''

import copy, os, stat

from Legacy.GnomeUI import Document, Utils
from Legacy import Base, Config

from gtk import *

class Pybliographic:
    ''' Main class holding all the documents and performing
    general tasks '''

    def __init__ (self):
        self.documents = []
        self.opened    = []
        
        histsize = Config.get ('gnome/history').data

        for i in range (1, histsize + 1):
            file = Utils.config.get_string  ('/apps/pyblio/history/file%d' % i) or ''
            fmat = Utils.config.get_string  ('/apps/pyblio/history/type%d' % i) or ''

            if not file: continue
            
            if not fmat: fmat = None
            self.opened.append ((file, fmat))

        return


    def new_document (self, * arg):
        db  = Base.DataBase (None)
        doc = Document.Document (db)

        # register several callbacks
        doc.Subscribe ('new-document',     self.new_document)
        doc.Subscribe ('open-in-new',      self.open_document)
        doc.Subscribe ('open-document',    self.cb_open_document)
        doc.Subscribe ('close-document',   self.close_document)
        doc.Subscribe ('exit-application', self.exit_application)
        doc.update_history (self.opened)
        
        self.documents.append (doc)
        return doc

    def cb_open_document (self, doc):
        ''' a document has been opened '''

        file = str (doc.data.key)
        fmat = doc.data.id
        
        #FIXME.
        #history.recently_used (file, 'application/x-bibtex',
        #                      'pybliographic', 'Bibliography')
                              
        try:
            self.opened.remove ((file, fmat))
        except ValueError:
            pass
        
        self.opened.insert (0, (file, fmat))

        # warn all the documents
        for doc in self.documents:
            doc.update_history (self.opened)

        # get the modification date...
        if doc.data.key and doc.data.key.url [0] == 'file':
            file = doc.data.key.url [2]
            doc.modification_date = os.stat (file) [stat.ST_MTIME]
        
        return

    
    def open_document (self, url, how = None, no_name=False):
        doc = self.new_document ()
        doc.open_document(url, how, no_name)
            
        return doc

    
    def close_document (self, document, maybe_exit = False):
        ''' close one specified document '''
        
        if not document.close_document_request ():
            return

        if len (self.documents) == 1 and maybe_exit:
            self.exit_application (self.documents [0])
            return
        
        document.w.destroy ()
        self.documents.remove (document)
        
        if not self.documents: self.new_document ()
        return


    def exit_application (self, document):
        document.update_configuration ()

        i = 1
        for file in self.opened [0:Config.get ('gnome/history').data]:
            name = file [0]
            fmat = file [1] or ''
            
            Utils.config.set_string ('/apps/pyblio/history/file%d' % i, name)
            Utils.config.set_string ('/apps/pyblio/history/type%d' % i, fmat)
            i = i + 1
        
        doclist = copy.copy (self.documents)
        
        for doc in doclist:
            if not doc.close_document_request ():
                return
            
            doc.w.destroy ()
            self.documents.remove (doc)

        from twisted.internet import reactor
        reactor.stop()
        return
    
