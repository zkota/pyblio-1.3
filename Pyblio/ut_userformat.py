# unit test for userformat


import unittest, sys

sys.path.append ('..')

from Pyblio import Fields, userformat



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

        ag.append (Fields.Author ("Léonid Kameneff"))
        r =  userformat.author_editor_format (item)
        self.assertEqual (r, 'Rind, B. et al.')


    def test02 (self):
        
        ag = Fields.AuthorGroup()

        ag.append (Fields.Author ("Françoise Sagan"))
        item = {'author': ag, 'title': 'Bonjour tristesse'}
        r = userformat.author_title_format (item)
        print r
        self.assertEqual (r, 'Sagan, F.: Bonjour tristesse')

        

if __name__ == '__main__':
    unittest.main ()
                   


