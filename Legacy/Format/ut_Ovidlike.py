#    -*- coding: 'iso8859-1' -*-
data = ["""Authors
  Muller S.  Garda P.  Muller JD.  Cansi Y.
Title
  Seismic events discrimination by neuro-fuzzy merging of
  signal and catalogue features
Source
  Physics & Chemistry of the Earth Part A-Solid Earth & Geodesy. 24(3):201-206,
  1999.
Abstract
  This article presents an original method for the classification of low
  """,
        """Authors
  Morozova EA.  Morozov IB.  Smithson SB.  Solodilov LN.
Title
  Heterogeneity of the uppermost mantle beneath Russian Eurasia from the
  ultra-long-range profile QUARTZ
Source
  Journal of Geophysical Research-Solid Earth. 104(B9):20329-20348, 1999 Sep
  10.
Abstract
  The 3850-km long Deep Seismic Sounding profile QUARTZ
  [References: 71]""",
        """Authors
  Grimm RE.  Lynn HB.  Bates CR.  Phillips DR.  Simons KM.  Beckham WE.
Title
  Detection and analysis of naturally fractured gas reservoirs: Multiazimuth
  seismic surveys in the Wind River basin, Wyoming
Source
  Geophysics. 64(4):1277-1292, 1999 Jul-Aug.
Abstract
  Multiazimuth binning of 3-D P-wave reflection data is a relatively simple but
  identify regions of high fracture density and gas yield. [References: 40]""",
        """Authors
  Leonard G.  Villagran M.  Joswig M.  Bartal Y.  Rabinowitz N.  Saya A.
Title
  Seismic source classification in Israel by signal imaging
  and rule-based coincidence evaluation
Source
  Bulletin of the Seismological Society of America. 89(4):960-969, 1999 Aug.
Abstract
  We tested the applicability of the sonogram detector and a rule-based
  Comprehensive Test Ban Treaty. [References: 20]
  """,
        """Authors
  Elie F.  Hayakawa M.  Parrot M.  Pincon JL.  Lefeuvre F.
Title
  Neural network system for the analysis of transient
  phenomena on board the DEMETER micro-satellite
Source
  IEICE Transactions on Fundamentals of Electronics Communications & Computer
  Sciences. E82A(8):1575-1581, 1999 Aug.
Abstract
  In 2001, the DEMETER micro-satellite will be launched to perform Detection of
  from the AUREOL-3 satellite is exposed. [References: 14]
  """,
        """Authors
  de Stefano A.  Sabia D.  Sabia L.
Title
  Probabilistic neural networks for seismic
  damage mechanisms prediction
Source
  Earthquake Engineering & Structural Dynamics. 28(8):807-821, 1999 Aug.
Abstract
  The procedure commonly employed to assess the seismic
  [References: 13]
  """,
        """Authors
  Nath SK.  Chakraborty S.  Singh SK.  Ganguly N.
Title
  Velocity inversion in cross-hole seismic tomography by
  counter-propagation neural network, genetic algorithm and
  evolutionary programming techniques
Source
  Geophysical Journal International. 138(1):108-124, 1999 Jul.
Abstract
  The disadvantages of conventional seismic tomographic ray
  """,
        """Authors
  Patane D.  Ferrari F.
Title
  ASDP: a PC-based program using a multi-algorithm approach for automatic
  detection and location of local earthquakes
Source
  Physics of the Earth & Planetary Interiors. 113(1-4 Special Issue SI):57-74,
  1999 Jun.
Abstract
  A few automated data acquisition and processing systems operate on
  Science B.V. All rights reserved. [References: 47]
""",
        """Authors
  Zadeh MA.  Nassery P.
Title
  Application of quadratic neural networks to
  seismic signal classification
Source
  Physics of the Earth & Planetary Interiors. 113(1-4 Special Issue
  SI):103-110, 1999 Jun.
Abstract
  This paper solves the seismic signal classification problem
  """,
        """Authors
  Fedorenko YV.  Husebye ES.  Ruud BO.
Title
  Explosion site recognition; neural net discriminator using
  single three-component stations
Source
  Physics of the Earth & Planetary Interiors. 113(1-4 Special Issue
  SI):131-142, 1999 Jun.
Abstract
  In monitoring of local seismicity, the occurrence of many
  All rights reserved. [References: 31]  """]


import cStringIO, os, os.path, re, sys,unittest

sys.path.append (os.path.abspath('../..'))

from Legacy.Base import DataBase, Entry
from Legacy import Config
from Legacy.Key import Key
from Legacy.Types import get_entry
from Legacy.Format.OvidLike import OvidLike, writer, write_source_field 
from Legacy.Fields import Author, AuthorGroup, Date

class WriterCase (unittest.TestCase):

    def setUp (self):


        Config.parse_directory (os.path.abspath('../ConfDir'))
        Config.load_user ()
        self.db = DataBase ('//localhost/Internal')
        self.output = cStringIO.StringIO()
        self.mapping = Config.get('ovid/mapping').data

        
    def test01(self):

        self.entry = Entry ( Key('TEST', 'KEY1'), get_entry('article'),
            {'journal': 'CACM',
             'number': 22, 
             'volume': 123,
             'pages': '234-543'})
        self.db.add(self.entry)
        self.itera = self.db.iterator()
        
        writer (self.itera, self.output, self.mapping)
        print self.output.getvalue()
        

    def test02source (self):

        data = [ ## from cites.ovid
            {'result':
             'International Journal of Hematology. 69(2):81-88, 1999 Feb.',
             'journal': 'International Journal of Hematology',
             'volume': 69, 'number': 2, 'pages': '81-88',
             'date': Date ((1999, 2, None))},
            {'result':
             'Journal of Trauma-Injury Infection & Critical Care. 44(6):1047-1054; discussion 1054-5, 1998 Jun.',              
             'journal': 'Journal of Trauma-Injury Infection & Critical Care',
             'volume': 44, 'number': 6, 'pages': '1047-1054',
             'date': Date ((1998, 6, None)),
             'other-note': 'discussion 1054-5'},
            {'result': 'Chemotherapy. 42(3):215-219, 1996 May.',
             ## date in »cites.ovid«: '1996 May-Jun' ##
             ## pages in »cites.ovid«: '215-19' ##
             'journal': 'Chemotherapy',
             'volume': 42, 'number': 3, 'pages': '215-219',
             'date': Date ((1996, 5, None))},
            {'result': 'Circulatory Shock. 18(3):193-203, 1986.', 
             'journal': 'Circulatory Shock',
             'volume': 18, 'number': 3, 'pages': '193-203',
             'date': Date ('1986')},
            {'result':
             'Archives of Internal Medicine. 162(17):1961-1965, 2002 Sep 23.',
             'journal': 'Archives of Internal Medicine',
             'volume': 162, 'number': 17, 'pages': '1961-1965',
             'date': Date ((2002, 9, 23))},]


        
        for i in data :

            e =  Entry ( Key('TEST', 'KEY1'), get_entry('article'),
                         i)
            self.output.seek(0)
            self.output.truncate(0)
            write_source_field (self.output, e, self.mapping)
            r = self.output.getvalue()
            self.assertEqual (e['result'], r[9:-1])
            




class RexpCase  (unittest.TestCase):

    rx = re.compile (# Fall 1:
        r"""(?P<journal>.*?)\.\ +
        (?P<volume>\w+)?
        (?P<inseries>(\ PG\.\ +))?
        (?:\((?P<number>.*)\))?
        (?::?(?P<pages>.*?(?:-+.*?)?)
        (?:;\ *(?P<other>.*))?)
        (?:[,\.]\ *(?P<year>\d\d\d\d))\ *
        (?P<month>.*)
        \.\Z
        """, flags= re.VERBOSE)

    data = [("""Journal of Trauma-Injury Infection & Critical Care.  44(6):1047-54; discussion 1054-5, 1998 Jun.""",
             'Journal of Trauma-Injury Infection & Critical Care', '44', '6',
             None, '1047-54', '1998', 'Jun', 'discussion 1054-5'),
            ("""Journal of Geophysical Research-Solid Earth. 104(B9):20329-20348, 1999 Sep 10.""",
             'Journal of Geophysical Research-Solid Earth', '104', 'B9', None,
             '20329-20348', '1999', 'Sep 10', None),
            ("""Circulatory Shock.  18(3):193-203, 1986.""",
             'Circulatory Shock', '18', '3', None, '193-203', '1986', '', None),
            ("""New York Times Book Review. :4, 1997 Sep 7.""",
             'New York Times Book Review', None, None, None, '4', '1997',
             'Sep 7', None),
            ("""Clinical Orthopaedics & Related Research. (425):35-43, 2004 Aug.""",
             'Clinical Orthopaedics & Related Research', None, '425', None,
             '35-43', '2004', 'Aug', None),
            ("""PEPTIDE AN(?P<journal>.*?)\.\ +
        (?P<volume>\w+)?
        (?P<inseries>(\ PG\.\ +))?
        (?:\((?P<number>.*)\))?
        (?::?(?P<pages>.*?(?:-+.*?)?)
        (?:;\ *(?P<other>.*))?)
        (?:[,\.]\ *(?P<year>\d\d\d\d))\ *
        (?P<month>.*)
        \.\Z
        D PROTEIN DRUG ANALYSIS. 101 PG. 775-796. 2000 [Figures] [Plates].""",
             'PEPTIDE AND PROTEIN DRUG ANALYSIS', '101', None, ' PG. ',
             '775-796', '2000', '[Figures] [Plates]', None),
            ("""Journal of Hand Surgery - British Volume. 20B(6):841-855, 1995 Dec.""",
             'Journal of Hand Surgery - British Volume', '20B', '6', None,
             '841-855', '1995', 'Dec', None),
            ("""Clinical Orthopaedics & Related Research. (355 Suppl S):S 22-S 30, 1998 Oct.""",
             'Clinical Orthopaedics & Related Research', None, '355 Suppl S',
             None, 'S 22-S 30', '1998', 'Oct', None),
            ("""Human Mutation. (Suppl 1):S 56-S 57, 1998.""",
             'Human Mutation', None, 'Suppl 1', None, 'S 56-S 57',
             '1998', '', None),
            ("""VERY HIGH FREQUENCY (VHF) ESR/EPR. 22 PG. 431-464. 2004 [Figures].""",
             'VERY HIGH FREQUENCY (VHF) ESR/EPR', '22', None, ' PG. ',
             '431-464', '2004', '[Figures]', None),
            ("""Journal of the Chemical Society-Perkin Transactions II. (12):2545-2548, 1997 Dec.""",
             'Journal of the Chemical Society-Perkin Transactions II', None,
             '12', None, '2545-2548', '1997', 'Dec', None),
            ("""Mechanism & Machine Theory. 31(4):381-395, 1996 May.""",
             'Mechanism & Machine Theory', '31', '4', None, '381-395',
             '1996', 'May', None),
            ("""Biophysical Journal. 71(6):3320-3329, 1996 Dec.""",
             'Biophysical Journal', '71', '6', None, '3320-3329',
             '1996', 'Dec', None),
             ("""Biochemistry. 38(49):16333-16339, 1999 Dec 7.""",
              'Biochemistry', '38', '49', None, '16333-16339',
              '1999', 'Dec 7', None),
             ]
             
             


    def test01 (self):
        for test in self.data:
            text, journal, volume, number, inseries, \
                  pages, year, month, other = test
            m = self.rx.match (text)
            if m:
                print m.group(
                    'journal', 'volume', 'number', 'inseries',
                    'pages', 'year', 'month', 'other')
                self.assertEqual (journal, m.group('journal'))             
                self.assertEqual (volume, m.group('volume'))             
                self.assertEqual (number, m.group('number'))             
                self.assertEqual (inseries, m.group('inseries'))             
                self.assertEqual (pages, m.group('pages'))             
                self.assertEqual (year, m.group('year'))             
                self.assertEqual (month, m.group('month'))             
                self.assertEqual (other, m.group('other'))             
            else: print 'Fehler'

class Rexp2Case (unittest.TestCase):

    def test01 (self):
        """Regexp wie oben"""
        rx = re.compile (# Fall 1:
            r"""(?P<journal>.*?)\.\ +
        (?P<volume>\w+)?
        (?P<inseries>(\ PG\.\ +))?
        (?:\((?P<number>.*)\))?
        (?::?(?P<pages>.*?(?:-+.*?)?)
        (?:;\ *(?P<other>.*))?)
        (?:[,\.]\ *(?P<year>\d\d\d\d))\ *
        (?P<month>.*)
        \.\Z
         """
            , flags= re.VERBOSE)
       
        data = ['Biophysical Journal. 71(6):3320-3329, 1996 Dec.',
                'Biochemistry. 38(49):16333-16339, 1999 Dec 7.',
                'VERY HIGH FREQUENCY (VHF) ESR/EPR. 22 PG. 431-464. 2004 [Figures].'
                ]

        for d in data :
            m = rx.match (d)
            if m:
                print m.group(
                    'journal', 'volume', 'number', 'inseries',
                    'pages', 'year', 'month', 'other')
            else:
                print '**** FEHLER', d


    def test02 (self):
        rx = re.compile (# Fall 1:
            r"""(?P<journal>.*?)\.\ +
            (?P<volume>\w+)?
            (?P<inseries>(\ PG\.\ +))?
            (?:\((?P<number>.*)\))?
            (?::?(?P<pages>.*?(?:-+.*?)?)
            (?:;\ *(?P<other>.*))?)
            (?:[,\.]\ *(?P<year>\d\d\d\d))\ *
            (?P<month>.*)
            \.\s*\Z"""
            , flags= re.VERBOSE)
       
        data = ['Biophysical Journal. 71(6):3320-3329, 1996 Dec.',
                'Biochemistry. 38(49):16333-16339, 1999 Dec 7.',
                'VERY HIGH FREQUENCY (VHF) ESR/EPR. 22 PG. 431-464. 2004 [Figures].'
                ]

        for d in data :
            m = rx.match (d)
            if m:
                print m.group(
                    'journal', 'volume', 'number', 'inseries',
                    'pages', 'year', 'month', 'other')
            else:
                print '**** FEHLER', d

class AuthorCase (unittest.TestCase):

    def test01 (self):
        aut = ["Marsh D.",
               "de Planque MRR.", "Kruijtzer JAW."]

        R = OvidLike (None, {}, None)
        for i in aut:
            x = R.parse_author (i)
            print `x`


    def test02 (self):
        aut = """Pali T.  Whyteside G.  Dixon N.  Kee TP.  Ball S.  Harrison MA.  Findlay JBC.
 Finbow ME.  Marsh D."""

        R = OvidLike (None, {}, None)
        R.parse_author (aut)

def suite():
    theSuite = unittest.TestSuite()

    #theSuite.addTest(unittest.makeSuite(WriterCase))
    #theSuite.addTest(unittest.makeSuite(RexpCase))
    #theSuite.addTest(unittest.makeSuite(Rexp2Case))
    theSuite.addTest(unittest.makeSuite(AuthorCase))

    return theSuite

def main ():
    unittest.main (defaultTest='suite' )
    

if __name__ == '__main__':
    
    main()



### Local Variables:
### Mode: python
### encoding: iso-8859-1    
### End:


    


