# Site configuration

from Pyblio import Autoload, Config, version

from Pyblio.TextUI import *

# ==================================================

import string, os

# define autoloaded formats

Autoload.preregister ('format', 'BibTeX',  'Pyblio.Format.BibTeX',  '.*\.bib')
Autoload.preregister ('format', 'Ovid',    'Pyblio.Format.Ovid',    '.*\.ovid')
Autoload.preregister ('format', 'Medline', 'Pyblio.Format.Medline', '.*\.med')
Autoload.preregister ('format', 'Refer',   'Pyblio.Format.Refer',   '.*\.refer')
Autoload.preregister ('format', 'ISIFile', 'Pyblio.Format.isifile', '.*\.isi')


# define styles and outputs

Autoload.preregister ('style', 'Generic', 'Pyblio.Style.Generic')
Autoload.preregister ('style', 'apa4e',   'Pyblio.Style.apa4e')
Autoload.preregister ('style', 'abbrv',   'Pyblio.Style.abbrv')

Autoload.preregister ('output', 'Text',    'Pyblio.Output.text')
Autoload.preregister ('output', 'Raw',     'Pyblio.Output.raw')
Autoload.preregister ('output', 'HTML',    'Pyblio.Output.html')
Autoload.preregister ('output', 'LaTeX',   'Pyblio.Output.LaTeX')
Autoload.preregister ('output', 'Textnum', 'Pyblio.Output.textnum')
Autoload.preregister ('output', 'Textau',  'Pyblio.Output.textau')

# define key formats

Autoload.preregister ('key', 'Default', 'Pyblio.Utils')

# Parse the configuration directory

rootconfig = os.path.join ('Pyblio', 'ConfDir')

if not os.path.isdir (rootconfig):
    rootconfig = os.path.join (version.pybdir, 'Pyblio', 'ConfDir')
    
if os.path.isdir (rootconfig):
    Config.parse_directory (rootconfig)

