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

''' Parser for XML definitions of the bibliographic output '''

from Legacy import Open, Autoload

from xml import sax
from xml.sax.saxutils import escape, quoteattr

import string, re

_map = string.maketrans ('\t', ' ')
_cpt = re.compile ('\s+')
_rnl = re.compile ('\n\s*\n+')
_dnl = re.compile ('\n')

_lines = re.compile ('\d+-+\d+')

class BibStyle:
    def __init__ (self):
        self.data = []
        self.meth = {}
        return

    def output (self, entry, fmt, key = None):
        fmt.start (key, entry)
        had_text = 0
        for item in self.data:
            had_text = item.output (entry, fmt, None, self.meth, had_text)
        fmt.end ()
        return

    
class InField:
    def __init__ (self, field, neg = 0):
        self.field = field
        self.neg   = neg
        self.data  = []
        return

    def output (self, entry, fmt, style = None, meth = {}, had_text = 1):
        if not self.neg and not entry.has_key (self.field):
            return had_text
        if self.neg and entry.has_key (self.field):
            return had_text

        for item in self.data:
            had_text = item.output (entry, fmt, style, meth, had_text)
            
        return had_text

    
class InEntry:
    def __init__ (self, field, neg = 0):
        self.entry = field
        self.neg   = neg
        self.data  = []
        return

    def output (self, entry, fmt, style = None, meth = {}, had_text = 1):
        if not self.neg and \
           string.lower (entry.type.name) != self.entry:
            return had_text
        if self.neg and \
           string.lower (entry.type.name) == self.entry:
            return had_text
        
        for item in self.data:
            had_text = item.output (entry, fmt, style, meth, had_text)
            
        return had_text


class Text:
    def __init__ (self, text = '', style = None):
        self.style = style
        self.text  = text
        return

    def output (self, entry, fmt, style = None, meth = {}, had_text = 1):
        text = re.sub (_rnl, ' ', self.text)
        text = string.translate (text, _map)
        text = re.sub (_dnl, '',  text)
        text = re.sub (_cpt, ' ', text)
        
        fmt.write (text, style)
        return (text != ' ' and text != '') or had_text

    
class Singular:
    def __init__ (self, field, neg = 0):
        self.field = field
        self.neg   = neg
        self.data  = []
        return


    def output (self, entry, fmt, style = None, meth = {}, had_text = 1):
        if not self.neg and not entry.has_key (self.field):
            return had_text

        length = 0
        field  = entry [self.field]
        try:
            length = len (field)
        except AttributeError:
            if _lines.match (str (field)):
                length = 2

        if length > 1 and not self.neg: return had_text
        if length < 2 and self.neg: return had_text

        for item in self.data:
            had_text = item.output (entry, fmt, style, meth, had_text)
        return had_text
    
    
class Content:
    def __init__ (self, field):
        self.field = field
        return

    def output (self, entry, fmt, style = None, meth = {}, had_text = 1):
        if not entry.has_key (self.field): return had_text

        field = entry [self.field]

        if meth.has_key (self.field):
            text = meth [self.field] (field, fmt.coding)
        else:
            text = field.format (fmt.coding)
            
        fmt.write (text, style)
        return 1


class Style:
    def __init__ (self, style):
        self.style = style
        self.data  = []
        return

    def output (self, entry, fmt, style = None, meth = {}, had_text = 1):
        for item in self.data:
            had_text = item.output (entry, fmt, self.style, meth, had_text)
            
        return had_text


class Separator:
    def __init__ (self):
        self.data = []
        return

    def output (self, entry, fmt, style = None, meth = {}, had_text = 1):
        if not had_text: return 0

        for item in self.data:
            item.output (entry, fmt, style, meth, had_text)
        
        fmt.separator ()
        return 0


class Config:
    def __init__ (self, att):
        self.att   = att
        self.data  = ''
        return


class Module:
    def __init__ (self, att):
        self.module = att
        self.data   = []
        return


    
class XMLBib (sax.handler.ContentHandler):

    
    def __init__ (self, url):

        # each hash value contains a 2-uplet (opener, closer)
        
        self.format = None
        self.top    = []
        self.data   = []
        self.config = []

        self.methods = {}
        
        fh = open (Open.url_to_local (url))

        parser = sax.make_parser ()
        parser.setFeature (sax.handler.feature_validation, False)
        parser.setContentHandler (self)
        
        parser.parse (fh)
        fh.close ()
        
        return

    def configure (self):
        fmeth = {}
        
        module = None
        for mod in self.config:
            module = Autoload.get_by_name ('style', mod.module).data
            if module is None:
                raise RuntimeError, "unknown module `%s'" % mod.module

            for item in mod.data:
                if item.att.has_key ('method'):
                    meth = item.att ['method']
                    if module.has_key (item.data):
                        self.methods [meth] = module [item.data]
                    continue
                
                if item.att.has_key ('field'):
                    field = item.att ['field']
                    if module.has_key (item.data):
                        fmeth [field] = module [item.data]
                    continue

        self.format.meth = fmeth
        return

    def setDocumentLocator (self, locator):
        self.locator = locator
        return

    def _error (self, msg):
        raise sax.SAXParseException (msg, None, self.locator)


    def _attr (self, attr, attrs):
        try:
            val = attrs [attr]
        except KeyError:
            self._error (_("missing '%s' attribute") % attr)

        return val

    def startElement (self, name, attrs):

        try:
            meth = self.elements [name]

        except KeyError:
            self._error (_("invalid opening tag: %s") % name)

        meth [0] (self, attrs)
        return

    def endElement (self, name):
        try:
            meth = self.elements [name]

        except KeyError:
            self._error (_("invalid closing tag: %s") % name)

        meth [1] (self)
        return

    def characters (self, data):
        if len (self.data) == 0:
            return

        data = data.encode ('utf-8')

        if self.data [-1]: self.data [-1] (data)
        return

    # --------------------------------------------------

    def open_bibstyle (self, att):
        self.top.append (BibStyle ())
        return

    
    def close_bibstyle (self):
        self.format = self.top [-1]
        del self.top [-1]
        return


    def data_infield (self, data):
        self.top [-1].data.append (Text (data))
        return

    
    def open_infield (self, att):
        if not att.has_key ('name'):
            raise RuntimeError, "InField has no name attribute"

        field = InField (att ['name'], 0)
        self.top.append  (field)
        self.data.append (self.data_infield)
        return

    
    def generic_close (self):
        top = self.top [-1]

        del self.top [-1]
        del self.data [-1]
        
        self.top [-1].data.append (top)
        return

    
    def open_notinfield (self, att):
        if not att.has_key ('name'):
            raise RuntimeError, "NotInField has no name attribute"

        field = InField (att ['name'], 1)
        self.top.append (field)
        self.data.append (self.data_infield)
        return

    
    def open_content (self, att):
        if att.has_key ('name'):
            name = att ['name']
        else:
            # search the stack
            stack = self.top
            name  = None
            while stack:
                top   = stack [-1]
                stack = stack [:-1]
                if hasattr (top, 'field'):
                    name = top.field
                    break
            
            if name is None:
                raise RuntimeError, "no name defined for Content"

        self.top.append (Content (name))
        self.data.append (None)
        return
    

    def open_inentry (self, att):
        if not att.has_key ('name'):
            raise RuntimeError, "InEntry has no name attribute"

        field = InEntry (att ['name'], 0)
        self.top.append (field)
        self.data.append (self.data_infield)
        return
    
    
    def open_notinentry (self, att):
        if not att.has_key ('name'):
            raise RuntimeError, "InEntry has no name attribute"

        field = InEntry (att ['name'], 1)
        self.top.append (field)
        self.data.append (self.data_infield)
        return

    
    def open_style (self, att):
        if not att.has_key ('name'):
            raise RuntimeError, "Style has no name attribute"

        self.top.append (Style (att ['name']))
        self.data.append (self.data_infield)
        return


    def open_separator (self, att):
        self.top.append (Separator ())
        self.data.append (self.data_infield)
        return


    def data_config (self, data):
        self.top [-1].data = string.strip (data)
        return

    
    def open_config (self, att):
        self.top.append (Config (att))
        self.data.append (self.data_config)
        return


    def open_module (self, att):
        if not att.has_key ('name'):
            raise RuntimeError, "Module has no name attribute"

        self.top.append (Module (att ['name']))
        self.data.append (None)
        return


    def close_module (self):
        top = self.top [-1]

        del self.top [-1]
        del self.data [-1]
        
        self.config.append (top)
        return
    

    def open_singular (self, att):
        if att.has_key ('name'):
            name = att ['name']
        else:
            # search the stack
            stack = self.top
            name  = None
            while stack:
                top   = stack [-1]
                stack = stack [:-1]
                if hasattr (top, 'field'):
                    name = top.field
                    break
            
            if name is None:
                raise RuntimeError, "no name defined for Singular"

        self.top.append (Singular (name, 0))
        self.data.append (self.data_infield)
        return
        

    def open_plural (self, att):
        if att.has_key ('name'):
            name = att ['name']
        else:
            # search the stack
            stack = self.top
            name  = None
            while stack:
                top   = stack [-1]
                stack = stack [:-1]
                if hasattr (top, 'field'):
                    name = top.field
                    break
            
            if name is None:
                raise RuntimeError, "no name defined for Plural"

        self.top.append (Singular (name, 1))
        self.data.append (self.data_infield)
        return
        

        
    def handle_doctype (self, tag, pubid, syslit, data):
        if string.lower (tag) != 'bibstyle':
            raise RuntimeError, "this is not a BibStyle XML file !"
        return
    
    
    elements = {
        'bibstyle'    : (open_bibstyle, close_bibstyle),
        'infield'     : (open_infield,  generic_close),
        'notinfield'  : (open_notinfield, generic_close),
        'inentry'     : (open_inentry, generic_close),
        'notinentry'  : (open_notinentry, generic_close),
        'content'     : (open_content, generic_close),
        'style'       : (open_style, generic_close),
        'separator'   : (open_separator, generic_close),
        'define'      : (open_config, generic_close),
        'module'      : (open_module, close_module),
        'singular'    : (open_singular, generic_close),
        'plural'      : (open_plural, generic_close),
        }

    attributes = {
        'infield'    : { 'name' : None },
        'notinfield' : { 'name' : None },
        'inentry'    : { 'name' : None },
        'notinentry' : { 'name' : None },
        'style'      : { 'name' : None },
        'content'    : { 'name' : None },
        'module'     : { 'name' : None },
        'singular'   : { 'name' : None },
        'plural'     : { 'name' : None },
        'define'     : { 'method' : None,
                         'field'  : None },
        'separator'  : {},
        }
