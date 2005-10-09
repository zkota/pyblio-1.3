#    -*- coding: iso8859-1 -*-


import cStringIO, os, sys, unittest

sys.path.append (os.path.abspath('../..'))
print os.path.abspath('../..')



from Pyblio.Format import isifile
from Pyblio import Base, Config, Fields



example_1 = """AU Bogin, B
TI Evolutionary hypotheses for human childhood
SO YEARBOOK OF PHYSICAL ANTHROPOLOGY, VOL 40 - 1997
BP 63
EP 89
CR AIELLO LC, 1995, CURR ANTHROPOL, V36, P199
UT ISI:000071836900003
SE YEARBOOK OF PHYSICAL ANTHROPOLOGY
SN 0096-848X
J9 YEARB PHYS ANTHROPOL
PT S
VL 40
NR 115
PY 1997
AB The origins of human childhood have fascinated scholars from many
GA BK33K
%% * pages *  63 -- 89
%% * size *  27 p.
ER
"""
example_2 = """AU X, ABC
   Y, D
   Z, EFGH
ER
"""
example_3 = """ED X, ABC
   Y, D
   Z, EFGH
ER
"""

class ReaderCase (unittest.TestCase):

    def setUp (self):

        Config.parse_directory (os.path.abspath('../ConfDir'))
        Config.load_user ()
	print 'CONFIGURATION'
	print 50*'-'
	for i in Config.domains ():
	    print i, Config.keys_in_domain (i)
	print 'END', 50*'-'
        self.db = Base.DataBase ('//localhost/Internal')
        self.output = cStringIO.StringIO()

        
    def test01(self):
	"""Test that all fields are Instances, as
	opposed to strings"""

	inpt = cStringIO.StringIO (example_1)
	rdr = isifile.IsifileIterator (inpt)
	e = rdr.first ()
	while e:
	    print e
	    for k in e.keys():
		self.assert_(
		    isinstance (e [k],
				(Fields.AuthorGroup, Fields.Date, Fields.Text,
				 Fields.LongText, Fields.URL, Fields.Reference)),
		    "Invalid Field %s(%s) = %s" % (
		    k, e [k].__class__,  e [k]))
	    e = rdr.next()

    def test02 (self):
	"""Test that Initials are formatted correctly.
	According to Bibtex specs, they must be separated
	by period, space ('. ')."""
	comparison = {'X': 'A. B. C.',
		      'Y': 'D.',
		      'Z': 'E. F. G. H.'}
	    
	inpt = cStringIO.StringIO (example_2)
	rdr = isifile.IsifileIterator (inpt)
	e = rdr.first ()
	while e:
	    print e
	    for auth in e['author']:
		print auth
		self.assertEqual (
		    auth.first, comparison [auth.last])
	    e = rdr.next ()

    def test03 (self):
	"""Test that Editors are accepted."""
	
	comparison = {'X': 'A. B. C.',
		      'Y': 'D.',
		      'Z': 'E. F. G. H.'}
	    
	inpt = cStringIO.StringIO (example_3)
	rdr = isifile.IsifileIterator (inpt)
	e = rdr.first ()
	while e:
	    print e
	    for auth in e['editor']:
		print auth
		self.assertEqual (
		    auth.first, comparison [auth.last])
	    e = rdr.next ()


    def test03 (self):
	"""Test that Editors are accepted."""
	
	comparison = {'X': 'A. B. C.',
		      'Y': 'D.',
		      'Z': 'E. F. G. H.'}
	    
	inpt = cStringIO.StringIO (example_3)
	rdr = isifile.IsifileIterator (inpt)
	e = rdr.first ()
	while e:
	    print e
	    for auth in e['editor']:
		print auth
		self.assertEqual (
		    auth.first, comparison [auth.last])
	    e = rdr.next ()


    def test03 (self):
	"""Test that Editors are accepted."""
	
	comparison = {'X': 'A. B. C.',
		      'Y': 'D.',
		      'Z': 'E. F. G. H.'}
	    
	inpt = cStringIO.StringIO (example_3)
	rdr = isifile.IsifileIterator (inpt)
	e = rdr.first ()
	self.assertEqual (e.has_key ('editor'), True)
	while e:
	    print e
	    for auth in e['editor']:
		print auth
		self.assertEqual (
		    auth.first, comparison [auth.last])
	    e = rdr.next ()


def suite():
    theSuite = unittest.TestSuite()

    theSuite.addTest(unittest.makeSuite(ReaderCase))

    return theSuite

def main ():
    unittest.main (defaultTest='suite' )
    

if __name__ == '__main__':
    
    main()



### Local Variables:
### Mode: python
### encoding: iso-8859-1    
### End:


    




















