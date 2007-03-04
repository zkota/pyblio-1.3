# unit test for userformat
# -*- coding: latin-1 -*-

import unittest, sys

sys.path.append ('..')

from Legacy import Fields, userformat



class author_editor_format_test (unittest.TestCase):
   

    def test01 (self):
        ag = Fields.AuthorGroup()

        ag.append (Fields.Author ("Bruce Rind"))
        item = {'author': ag}
        r =  userformat.author_editor_format (item)
        self.assertEqual (r, 'Rind, B.')

        ag.append (Fields.Author ("Otto Forster"))
        r =  userformat.author_editor_format (item)
        self.assertEqual (r, 'Rind/Forster')

        ag.append (Fields.Author ("Nicolas Bourbaki"))
        r =  userformat.author_editor_format (item)
        self.assertEqual (r, 'Rind/Forster/Bourbaki')

        ag.append (Fields.Author ("L�onid Kameneff"))
        r =  userformat.author_editor_format (item)
        self.assertEqual (r, 'Rind, B. et al.')


    def test02 (self):
        
        ag = Fields.AuthorGroup()

        ag.append (Fields.Author ("Fran�oise Sagan"))
        item = {'author': ag, 'title': 'Bonjour tristesse'}
        r = userformat.author_title_format (item)
        self.assertEqual (r, 'Sagan, F.: Bonjour tristesse')

    def test03 (self):

	ag = Fields.AuthorGroup ()

	ag.append (Fields.Author ("J�ger, Herbert"))
        item = {'author': ag, 'title': 'Bonjour tristesse'}
        r = userformat.author_title_format (item)
	self.assertEqual (r, 'J�ger, H.: Bonjour tristesse')

if __name__ == '__main__':
    unittest.main ()
                   


