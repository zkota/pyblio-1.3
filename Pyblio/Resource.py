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
 Pyblio.Resource -- handle (electronic) resourcces

     View:          start an application to display a rresource 
 -- 

"""

config_fields = 'resource/viewable-fields'
config_viewers = 'resource/viewers'

CHOOSER_ACTIONS = ('enter/edit', 'select', 'select-directory',
               'download', 'move/copy' )

import os, sys, urllib, urlparse

from Pyblio import Config, Fields, userexit

def is_interactive ():
    return sys.modules.has_key ('gtk')


class ResourceDirector (object):
    """ Under construction ;-)   """

Director = ResourceDirector ()


def is_viewable (item):
    if userexit.resource_viewer_select (Director, item):
	return True
    for i in Config.get (config_fields).data:
	if item.has_key (i):
	    return True

def get_viewables (item, priority=[]):
    """Return a list of possible viewable resources for an item"""
    R = userexit.resource_viewer_select (Director, item)
    if R: return R
    viewables = Config.get (config_fields).data 
    return [ (key, item[key], item [key].get_url ()) for key
	     in priority + viewables if item.has_key (key)]

def StartViewer (entry, key, stringuri, parent=None, document=None):

    if not is_interactive (): 	return

    from Pyblio.GnomeUI import Compat, Utils    


    uri = Fields.URL (stringuri)
    scheme, location, path, parameters, query, fragment  = uri.url
    fileuri = uri.get_url ()
    
    if uri.invalid or uri.inexact:
	message = Utils.Callback (
	    _("Warning: This URL is marked as Invalid or Approximate: %s\nContinue?") % fileuri)
	if not message.answer (): return

    if document:
	document.statusbar.set_status (_("Determining Mime Type ... "))

    try:
	mimetype =  Compat.get_mime_type (fileuri)
    except RuntimeError, mesg:
	Utils.error_dialog(_("Cannot determine mime type for item %s ") % entry.key.key, 
			   _("URL in question is: %s\n"
			   "You should check the url or path given for errors.\n"
			   "Details: %s")
			   % (fileuri, mesg))
	if document:
	    document.statusbar.pop ()
	return

    mimetype1 = mimetype.split ('/', 1) [0]

    if document:
 	document.statusbar.set_status (_("Accessing resource ..."))

    if scheme == 'file' and not location:
	filename = path
	
    elif mimetype in ['text/html', 'text/plain']:
	filename = fileuri

    else:
	filename, headers = urllib.urlretrieve (fileuri)
	
    if mimetype == 'application/x-gzip':
	try:
	    tempname = os.tmpnam ()
	    os.system ("gzip -d < %s >%s" %(filename, tempname))
	    filename = tempname
	    mimetype =  Compat.get_mime_type (filename)
	except RuntimeError, mesg:
	    Utils.error_dialog (_("IOError for item %s: cannot uncompress resource.")
				% entry.key.key, _("URL: %s\nDetails: %s")
				% (filename, mesg))
	    if document:
		document.statusbar.pop ()
	    return

    viewers = [
	item [1] for item in
	Config.get (config_viewers).data if item [0] == mimetype] or [
	item [1] for item in
	Config.get (config_viewers).data if item [0].endswith ('/*') and
	item [0] [:-2] == mimetype1]

    if viewers:
	cmd = viewers [0]
	command = userexit.resource_viewer_setup (
	    Director, entry, key, cmd, filename, uri, mimetype
	    ) or "%s %s&" %(cmd, filename)

	if document:
	    document.statusbar.set_status (_("Starting application ..."))
	os.system (command)
    else:
	Utils.error_dialog (_("No application to view resource"),
			    _("For mime type %s, no entry found in \n"
			    "configuration option resource/viewers.\n"
			    "Please consider adding one.\n"
			    "URL: %s") % (mimetype, fileuri))
    if document:
 	document.statusbar.pop ()

    return 
    

# Local Variables:
# py-master-file: "ut_resource.py"
# coding: "latin-1"
# End:
