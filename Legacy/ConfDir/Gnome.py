from Legacy import Config

def columns_checker (obj, value, userdata):
    """Only allow column names that display correctly.
    Return True if OK."""
##  print '>>>>>>>>>>>>>>>>>>>>', obj, value, userdata
    return len (value) > 0

    
Config.define ('gnome/columns', """ A list of the fields displayed
on the main screen of the interface """,
               Config.List (Config.String ()))

Config.define ('gnome/tooltips', """ A boolean indicating if
tooltips are enabled """, Config.Boolean ())

Config.define ('gnome/native-as-default', """ Should we edit the
entries in their native format by default ? """, Config.Boolean ())

Config.define ('gnome/old-confirmation-dialog',
	       """ Should we use the old dialog when closing, and ask for permission to skip saving? """, Config.Boolean ())

Config.define ('gnome/searched', """ List of searchable fields """,
               Config.List (Config.String ()))

Config.define ('gnome/history', """ Size of the history file """,
               Config.Integer (min = 1))

Config.define ('gnome/paste-key', """ Paste key instead of entry content """,
               Config.Boolean ())

# --------------------------------------------------

Config.set ('gnome/searched', ['Author', 'Title', 'Abstract', 'Date'])

Config.set ('gnome/tooltips', 1)

Config.set ('gnome/native-as-default', 0)

Config.set ('gnome/old-confirmation-dialog', 0)

Config.set ('gnome/columns', ('Author', 'Date', 'Title'))

Config.set ('gnome/history', 10)

Config.set ('gnome/paste-key', 1)
