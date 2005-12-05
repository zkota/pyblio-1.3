#    -*- coding: iso8859-1 -*-


import cStringIO, os, sys, unittest

import locale
locale.setlocale (locale.LC_ALL, '')

import gettext
gettext.install ('pybliographer', '/usr/local/share/locale', unicode = True)

sys.path.append (os.path.abspath('../..'))

from Pyblio import Base, Config, Fields

Config.parse_directory (os.path.abspath('../ConfDir'))
Config.load_user ()

from Pyblio.Format import Medline




example_1 = """PMID- 15985842
OWN - NLM
STAT- MEDLINE
DA  - 20050629
DCOM- 20050805
PUBM- Print
IS  - 0022-3018
VI  - 193
IP  - 7
DP  - 2005 Jul
TI  - Childhood sexual abuse and adult defensive functioning.
PG  - 473-9
AB  - Differences in defensive functioning between those who reported a history
      of childhood sexual abuse (CSA) and those who did not was examined in a
      functioning and psychological problems in adulthood.
AD  - Victims of Violence Program, Harvard Medical School, the Cambridge Health
      Alliance, Somerville, MA, USA. kcallahan@challiance.org
FAU - Callahan, Kelley L
AU  - Callahan KL
FAU - Hilsenroth, Mark J
AU  - Hilsenroth MJ
LA  - eng
PT  - Journal Article
PL  - United States
TA  - J Nerv Ment Dis
JID - 0375402
SB  - AIM
SB  - IM
MH  - Adaptation, Psychological
MH  - Adult
MH  - Child Abuse, Sexual/*psychology
MH  - Conflict (Psychology)
MH  - *Defense MH  - Inhibition (Psychology)
MH  - Life Change Events
MH  - Male
MH  - Mental Disorders/*diagnosis/etiology/psychology
MH  - Models, Psychological
MH  - Projection
MH  - Survivors/psychology
EDAT- 2005/06/30 09:00
MHDA- 2005/08/06 09:00
AID - 00005053-200507000-00007 [pii]
PST - ppublish
SO  - J Nerv Ment Dis 2005 Jul;193(7):473-9.

PMID- 15982145
OWN - NLM
STAT- MEDLINE
DA  - 20050628
DCOM- 20050915
PUBM- Print
IS  - 0022-006X
VI  - 73
IP  - 3
DP  - 2005 Jun
TI  - Victimization over the life span: a comparison of lesbian, gay, bisexual,
      and heterosexual siblings.
PG  - 477-87
AB  - Lifetime victimization was examined in a primarily European American
      sample that comprised 557 lesbian/gay, 163 bisexual, and 525 heterosexual
      greater among men than among women.
CI  - (c) 2005 APA, all rights reserved.
AD  - Department of Psychology, University of Washington, Seattle, WA 98195,
      USA. kbalsam@u.washington.edu
FAU - Balsam, Kimberly F
AU  - Balsam KF
FAU - Rothblum, Esther D
AU  - Rothblum ED
FAU - Beauchaine, Theodore P
AU  - Beauchaine TP
LA  - eng
PT  - Journal Article
PL  - United States
TA  - J Consult Clin Psychol
JID - 0136553
SB  - IM
MH  - Adolescent
MH  - Adult
MH  - Aged
MH  - Bisexuality/*statistics &amp; numerical data
MH  - Child
MH  - Child Abuse/statistics &amp; numerical data
MH  - Crime Victims/*statistics &amp; numerical data
MH  - Female
MH  - Heterosexuality/*statistics &amp; numerical data
MH  - Homosexuality, Female/*statistics &amp; numerical data
MH  - Homosexuality, Male/*statistics &amp; numerical data
MH  - Humans
MH  - *Life Change Events
MH  - Male
MH  - Middle Aged
MH  - Parent-Child Relations
MH  - Questionnaires
MH  - Research Support, Non-U.S. Gov't
MH  - Sex Distribution
MH  - Siblings/*psychology
EDAT- 2005/06/29 09:00
MHDA- 2005/09/16 09:00
AID - 2005-06517-010 [pii]
AID - 10.1037/0022-006X.73.3.477 [doi]
PST - ppublish
SO  - J Consult Clin Psychol 2005 Jun;73(3):477-87.
"""

example_2 = """FAU - Holmes, William C
AU  - Holmes WC
FAU - Sammel, Mary D
AU  - Sammel MD
FAU - van Wijk, Anton
AU  - van Wijk A
FAU - Loeber, Rolf
AU  - Loeber R
FAU - Vermeiren, Robert
AU  - Vermeiren R
FAU - Pardini, Dustin
AU  - Pardini D
"""

example_3 = """ED  - Holmes WC
ED  - Sammel MD
ED  - van Wijk A
ED  - Loeber R
ED  - Vermeiren R
ED  - Pardini D
"""

comparison = {'Holmes': 'W. C.',
	      'Sammel': 'M. D.',
	      'van Wijk': 'A.',
	      'Loeber': 'R.',
	      'Vermeiren': 'R.',
	      'Pardini': 'D.'}



class ReaderCase (unittest.TestCase):

    def setUp (self):

        self.db = Base.DataBase ('//localhost/Internal')
        self.output = cStringIO.StringIO()

        
    def test01(self):
	"""Test that all fields are Instances, as
	opposed to strings"""

	inpt = cStringIO.StringIO (example_1)
	rdr = Medline.MedlineIterator (inpt)
	e = rdr.first ()
	while e:
##	    print e
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
	    
	inpt = cStringIO.StringIO (example_2)
	rdr = Medline.MedlineIterator (inpt)
	e = rdr.first ()
	while e:
##	    print e
	    for auth in e['author']:
		print auth
		self.assertEqual (
		    auth.first, comparison [auth.last])
	    e = rdr.next ()

    def test03 (self):
	"""Test that Editors are accepted."""
	############ UNUSED ##############
	inpt = cStringIO.StringIO (example_3)
	rdr = Medline.MedlineIterator (inpt)
	e = rdr.first ()
	while e:
##	    print e
	    for auth in e.get('editor', []): #(sic)
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
