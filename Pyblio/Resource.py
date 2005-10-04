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

    from Pyblio.GnomeUI import Utils    
    try:
	import gnomevfs
    except ImportError:
	import gnome.vfs as gnomevfs

    uri = Fields.URL (stringuri)
    scheme, location, path, parameters, query, fragment  = uri.url
    fileuri = uri.get_url ()
    
    if uri.invalid or uri.inexact:
	message = Utils.Callback (
	    _("Warning: This URL is marked as Invalid or Approximate: %s\n Continue?") % fileuri)
	if not message.answer (): return

    if document:
	document.statusbar.set_status (_("Determining Mime Type..."))

    try:
	mimetype =  gnomevfs.get_mime_type (fileuri)
    except RuntimeError, mesg:
	Utils.error_dialog (_("For item %s cannot determine mime type") % entry.key.key, 
			    _("URL in question is: %s\nYou should check the url or path given for errors.\nDetails: %s")
			    % (fileuri, mesg))
	if document:
	    document.statusbar.pop ()
	return
    
    if document:
 	document.statusbar.set_status (_("Accessing resource..."))

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
	    mimetype =  gnomevfs.get_mime_type (filename)
	except RuntimeError, mesg:
	    Utils.error_dialog (_("IOError for item %s: cannot unzip.")	% item.key.key,
				_("URL: %s\nDetails: %s")
				% (filename, mesg))
	    if document:
		document.statusbar.pop ()
	    return

    viewers = [item [1] for item in
	       Config.get (config_viewers).data if item [0] == mimetype]
    
    if viewers:
	cmd = viewers [0]
	command = userexit.resource_viewer_setup (
	    Director, item, key, cmd, filename, uri, mimetype
	    ) or "%s %s&" %(cmd, filename)

	if document:
	    document.statusbar.set_status (_("Starting application..."))
	os.system (command)
    else:
	Utils.error_dialog (_("Failure for item %s") % item.key.key,
			    _("No viewer found in Config resource/viewers\nURL: %s") % fileuri)
    if document:
 	document.statusbar.pop ()

    return 
    

# Local Variables:
# py-master-file: "ut_resource.py"
# coding: "latin-1"
# End:
