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
 

Class fileschooserbutton implements a widget similar to
      File Chooser Button from gtk: it calls a
      File Chooser Dialog to allow entering and editing an URL.

Class filechooserdialog subclasses gtk.FileChooserDialog and
      adds some fields to enter additional information for an URL.

      
     -- 


"""
RESPONSE_COPY = 1
RESPONSE_VIEW = 2

import gobject, gtk, gtk.gdk, pango, sys

from  Pyblio import Fields, Resource


def get_icon_theme (widget):

    if gtk.widget_has_screen (widget):
	return gtk.icon_theme_get_for_screen (gtk.widget_get_screen (widget))
    return gtk.icon_theme_get_default ();


class filechooserbutton (gtk.Button):
    def __init__ (self, URL=None, action='enter/edit', parent=None):
	gtk.Button.__init__ (self)

	g_error = gobject.GError ()
	self.parent_widget = parent 
	self.url = URL or Fields.URL ()
	self.newuri = None
	assert isinstance (URL, Fields.URL)
	self.action = action
	assert action in Resource.CHOOSER_ACTIONS, "Invalid file chooser action"
	
	self.connect ("clicked", self.cb_clicked)
	self.box = gtk.HBox (False, 4)
	self.add (self.box)
	self.image = gtk.Image ()
	pixbuf = self.render_icon (gtk.STOCK_NEW,
				   gtk.ICON_SIZE_MENU)
	self.image.set_from_pixbuf (pixbuf)
	self.box.pack_start (self.image, False, False, 0)
	self.label = gtk.Label (self.url.get_url () or _('Enter/Select an URL'))
	self.label.set_ellipsize (pango.ELLIPSIZE_START)
	self.label.set_alignment (0.0, 0.5)
	self.box.pack_start (self.label)
	self.sep = gtk.VSeparator ()
	self.box.pack_start (self.sep, False, False, 0)
	self.icon = gtk.image_new_from_stock (gtk.STOCK_SAVE, gtk.ICON_SIZE_MENU)
	self.box.pack_start (self.icon, False, False, 0)

	self.title = "Enter/Edit URL"
	self.dialog = None
	self.current_name = None
	self.show_all ()

    def set_title (self, tit):
	self.title = tit
	if self.dialog:
	    self.dialog.set_title (tit)

    def set_label (self, lab):

	self.label.set_text (lab)
	
    def cb_clicked (self, *args):
	
	self.dialog = filechooserdialog  (self.url, self.title)
	self.dialog.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
	
	self.dialog.set_transient_for (
	    self.parent_widget or self.get_toplevel ())
	response, self.newuri = self.dialog.run ()
	print 'NEW URI:', response, self.newuri
	self.dialog.destroy ()
	
	if response == gtk.RESPONSE_OK:
	    pass
	elif response == RESPONSE_VIEW:
	    print 'RESPONSE VIEW'
	    # Resource.StartViewer (
	elif response == RESPONSE_COPY:
	    print 'RESPONSE COPY'
	else:
	    pass
	return 

    def get_url  (self):

	return self.newuri


class filechooserdialog (gtk.FileChooserDialog):
    
    def __init__ (self, url, title):

	gtk.FileChooserDialog.__init__ (
	    self, title,  None, gtk.FILE_CHOOSER_ACTION_SAVE,
	    backend="gnomevfs")
	tips = gtk.Tooltips ()

	self.set_local_only (False)

	self.URI = url
	self.uri = self.URI.get_url ()

	self.select_uri (self.uri)
##	self.set_current_folder (self.uri)
##	self.set_current_name (self.uri)

	accelerator = gtk.AccelGroup ()
	self.add_accel_group (accelerator)

	b = self.add_button (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT)
	b.add_accelerator ('clicked', accelerator, gtk.keysyms.Escape, 0, 0)

	b = self.add_button (gtk.STOCK_OK, gtk.RESPONSE_OK)
	b.add_accelerator ('clicked', accelerator, gtk.keysyms.Return, 0, 0)

	b = self.add_button (gtk.STOCK_COPY, RESPONSE_COPY)
	b.add_accelerator ('clicked', accelerator, gtk.keysyms.c, gtk.gdk.CONTROL_MASK, 0)

	b = self.add_button (gtk.STOCK_FIND, RESPONSE_VIEW)
	b.add_accelerator ('clicked', accelerator, gtk.keysyms.v, gtk.gdk.CONTROL_MASK, 0)

	# added widgets
	vbox = gtk.VBox ()
	hbox = gtk.HBox ()
	vbox.pack_start (hbox)
	hbox.set_spacing (6)
	hbox.set_border_width (6)

	self.invalid_w = gtk.ToggleButton (_('Invalid'))
	hbox.pack_start (self.invalid_w, expand=False)
	tips.set_tip (self.invalid_w, "Set this to indicate an invalid URL",
			  "An invalid url may not usually be used, "
			  "but be kept for historical purposes.")
	self.invalid_w.set_active (self.URI.invalid or False)

	self.inexact_w = gtk.ToggleButton (_('Inexact'))
	hbox.pack_start (self.inexact_w, expand=False)
	tips.set_tip (self.inexact_w, "Indicates an URL that is not the resource proper",
			  "An inexact URL usually requires manual intervention.")
	self.inexact_w.set_active (self.URI.inexact or False)

	hbox.pack_start (gtk.Label (_(' Date accessed:')), False)
	self.date_w = gtk.Entry ()
	hbox.pack_start (self.date_w)
	tips.set_tip (self.date_w, "The date (and time) the resource has been accessed.",
			  "This information is often required"
			  " by bibliographical standards.")
	self.date_w.set_text (self.URI.date or '')
	
	hbox = gtk.HBox ()
	vbox.pack_start (hbox)
	hbox.set_spacing (6)
	hbox.set_border_width (6)
	hbox.pack_start (gtk.Label (_('Note:')), False)
	self.note_w = gtk.Entry ()
	hbox.pack_start (self.note_w)	
	tips.set_tip (self.note_w, "A note e.g. about the resource or its accessability.",
		      "Information that might help the user")
	self.note_w.set_text (self.URI.note or '')
	
	self.set_extra_widget (vbox)
	self.show_all ()
	
    def run (self):
	response = gtk.FileChooserDialog.run (self)
	uri = self.get_uri ()
	invalid = self.invalid_w.get_active ()
	inexact = self.inexact_w.get_active ()
	date = self.date_w.get_text ()
	note = self.note_w.get_text ()
	#print 'DIALOG RUN:', uri, invalid, inexact, date, note


	return response, Fields.URL (
	    uri, invalid=invalid, inexact=inexact,
	    date=date, note=note)



# Local Variables:
# coding: "latin-1"
# py-master-file: "ut_common.py"
# End:
