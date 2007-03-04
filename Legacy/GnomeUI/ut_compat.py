# unit test for Utils


import unittest, sys


import locale
locale.setlocale (locale.LC_ALL, '')

import gettext
gettext.install ('pybliographer', '/usr/local/share/locale', unicode = True)

sys.path.append ('../..')


from Legacy.GnomeUI import Compat



class compat_test (unittest.TestCase):



    def test01 (self):

	print Compat.error_dialog_parented
	print Compat.gnome_error_dialog_parented

        print Compat.get_mime_type

if __name__ == '__main__':
    unittest.main ()
                   


