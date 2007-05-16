# Site configuration

from Legacy import Autoload, Config, version

from Legacy.TextUI import *

# ==================================================

import string, os

# define autoloaded formats

Autoload.preregister ('format', 'BibTeX',  'Legacy.Format.BibTeX',  '.*\.bib')
Autoload.preregister ('format', 'Ovid',    'Legacy.Format.Ovid',    '.*\.ovid')
Autoload.preregister ('format', 'Medline', 'Legacy.Format.Medline', '.*\.med')
Autoload.preregister ('format', 'Refer',   'Legacy.Format.Refer',   '.*\.refer')
Autoload.preregister ('format', 'ISIFile', 'Legacy.Format.isifile', '.*\.isi')


# define styles and outputs

Autoload.preregister ('style', 'Generic', 'Legacy.Style.Generic')
Autoload.preregister ('style', 'apa4e',   'Legacy.Style.apa4e')
Autoload.preregister ('style', 'abbrv',   'Legacy.Style.abbrv')

Autoload.preregister ('output', 'Text',    'Legacy.Output.text')
Autoload.preregister ('output', 'Raw',     'Legacy.Output.raw')
Autoload.preregister ('output', 'HTML',    'Legacy.Output.html')
Autoload.preregister ('output', 'LaTeX',   'Legacy.Output.LaTeX')
Autoload.preregister ('output', 'Textnum', 'Legacy.Output.textnum')
Autoload.preregister ('output', 'Textau',  'Legacy.Output.textau')

# define key formats

Autoload.preregister('key', 'Default', 'Legacy.Utils')

# Parse the configuration directory

rootconfig = os.path.join ('Legacy', 'ConfDir')

if not os.path.isdir (rootconfig):
    rootconfig = os.path.join (version.pybdir, 'Legacy', 'ConfDir')
    
if os.path.isdir (rootconfig):
    Config.parse_directory (rootconfig)

