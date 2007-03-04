# unit test for Utils


import unittest, sys

sys.path.append ('..')

from Legacy import Utils, userformat



class compress_page_range_test (unittest.TestCase):

    data = [("1-9", '1', '9'),
            ("200-201", '200', '1'),
            ("300-500", '300', '500'),
            ("3000-3049", '3000', '49'),
        ]

    def test01 (self):

        for i in self.data:
            p, r = i[0], i[1:]
            self.assertEqual (Utils.compress_page_range(p,False), r)

        

if __name__ == '__main__':
    unittest.main ()
                   


