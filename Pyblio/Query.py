# This file is part of pybliographer
# 
# Copyright (C) 1998-2004 Frederic GOBRY
# Email : gobry@pybliographer.org
# 	   
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2 
# of the License, or (at your option) any later version.
#   
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details. 
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
# 
# 

"""
Search a keyword in a medline database

This code has been contributed by: John Vu <jvu001@umaryland.edu>
"""

# The time module is added for querying date ranges of publications
import urllib, sys, re, string, time

query_url = 'http://www.ncbi.nlm.nih.gov/entrez/utils/pmqty.fcgi'
fetch_url = 'http://www.ncbi.nlm.nih.gov/entrez/utils/pmfetch.fcgi'


def query_info (searchterm, field, displaynum, displaystart, edate):
    if edate != 'Entrez Date':
        params = urllib.urlencode ({
            'db': 'pubmed',
            'term' : searchterm,  # searchterm is user inputted text, modified by limits if applied
            'field' : field,
            'dopt' : 'd',
            'dispmax' : displaynum,
            'dispstart' : displaystart - 1, # minus 1 because the count starts at 0 and not at 1
            'relentrezdate' : edate  # two different search options given, depending on whether the user provides a relative entrez date
            })
    else:
        params = urllib.urlencode ({
            'db': 'pubmed',
            'term' : searchterm,  # searchterm is user inputted text, modified by limits
            'field' : field,
            'dopt' : 'd',
            'dispmax' : displaynum,
            'dispstart' : displaystart - 1
            })

    f = urllib.urlopen ("%s?%s" % (query_url, params))
    uids = []
    in_body = 0
    uid_re = re.compile (r'^([\d]+)<br>')

    while 1:
        line = f.readline ()
        if line == '': break

        if in_body:
            line = string.strip (string.lower (line))

            if line == '</body>': break

            ret = uid_re.match (line)
            if not ret:
                print "unknown line: %s" % line
                continue

            uids.append (int (ret.group (1)))
        else:
            line = string.strip (string.lower (line))

            if line == '<body>':
                in_body = 1
                continue

    f.close ()
    return uids


def medline_query (keyword,maxcount,displaystart,field,abstract,epubahead,pubtype,language,subset,agerange,humananimal,gender,entrezdate,pubdate,fromdate,todate):
    # note all the parameters needed to perform the query
    # Search with field limits
    if field == 'All Fields': field = 'ALL'
    elif field == 'Affiliation': field = 'AFFL'
    elif field == 'Author Name': field = 'AUTH'
    elif field == 'EC/RN Number': field = 'ECNO'
    elif field == 'Entrez Date': field = 'EDAT'
    elif field == 'Filter': field = 'FLTR'
    elif field == 'Issue': field = 'ISS'
    elif field == 'Journal Name': field = 'JOUR'
    elif field == 'Language': field = 'LANG'
    elif field == 'MeSH Date': field = 'MHDA'
    elif field == 'MeSH Major Topic': field = 'MAJR'
    elif field == 'MeSH Subheading': field = 'SUBH'
    elif field == 'MeSH Terms': field = 'MESH'
    elif field == 'Pagination': field = 'PAGE'
    elif field == 'Publication Date': field = 'PDAT'
    elif field == 'Publication Type': field = 'PTYP'
    elif field == 'Secondary Source ID': field = 'SI'
    elif field == 'Substance Name': field = 'SUBS'
    elif field == 'Text Word': field = 'WORD'
    elif field == 'Title': field = 'TITL'
    elif field == 'Title/Abstract': field = 'TIAB'
    elif field == 'UID': field = 'UID'
    elif field == 'Volume': field = 'VOL'

    # Below is added to keyword if user wants items with abstracts only
    if abstract: keyword = keyword + ' AND hasabstract'

    # Below is added to keyword if user wants items that are listed on pubmed ahead of print
    if epubahead: keyword = keyword + ' AND pubstatusaheadofprint'
    
    # Below are publication type limits to add to keyword
    if pubtype == 'Addresses': keyword = keyword + ' AND addresses[pt]'
    elif pubtype == 'Bibliography': keyword = keyword + ' AND bibliography[pt]'
    elif pubtype == 'Biography': keyword = keyword + ' AND biography[pt]'
    elif pubtype == 'Classical Article': keyword = keyword + ' AND classical article[pt]'
    elif pubtype == 'Clinical Conference': keyword = keyword + ' AND clinical conference[pt]'
    elif pubtype == 'Clinical Trial': keyword = keyword + ' AND clinical trial[pt]'
    elif pubtype == 'Clinical Trial, Phase I': keyword = keyword + ' AND clinical trial, phase I[pt]'
    elif pubtype == 'Clinical Trial, Phase II': keyword = keyword + ' AND clinical trial, phase II[pt]'
    elif pubtype == 'Clinical Trial, Phase III': keyword = keyword + ' AND clinical trial, phase III[pt]'
    elif pubtype == 'Clinical Trial, Phase IV': keyword = keyword + ' AND clinical trial, phase IV[pt]'
    elif pubtype == 'Comment': keyword = keyword + ' AND comment[pt]'
    elif pubtype == 'Congresses': keyword = keyword + ' AND congresses[pt]'
    elif pubtype == 'Consensus Development Conference': keyword = keyword + ' AND consensus development conference[pt]'
    elif pubtype == 'Consensus Development Conference, NIH': keyword = keyword + ' AND consensus development conference, NIH[pt]'
    elif pubtype == 'Controlled Clinical Trial': keyword = keyword + ' AND controlled clinical trial[pt]'
    elif pubtype == 'Corrected and Republished Article': keyword = keyword + ' AND corrected and republished article[pt]'
    elif pubtype == 'Dictionary': keyword = keyword + ' AND dictionary[pt]'
    elif pubtype == 'Directory': keyword = keyword + ' AND directory[pt]'
    elif pubtype == 'Duplicate Publication': keyword = keyword + ' AND duplicate publication[pt]'
    elif pubtype == 'Editorial': keyword = keyword + ' AND editorial[pt]'
    elif pubtype == 'Evaluation Studies': keyword = keyword + ' AND evaluation studies[pt]'
    elif pubtype == 'Festschrift': keyword = keyword + ' AND festschrift[pt]'
    elif pubtype == 'Government Publications': keyword = keyword + ' AND government publications[pt]'
    elif pubtype == 'Guideline': keyword = keyword + ' AND guideline[pt]'
    elif pubtype == 'Historical Article': keyword = keyword + ' AND historical article[pt]'
    elif pubtype == 'Interview': keyword = keyword + ' AND interview[pt]'
    elif pubtype == 'Journal Article': keyword = keyword + ' AND journal article[pt]'
    elif pubtype == 'Lectures': keyword = keyword + ' AND lectures[pt]'
    elif pubtype == 'Legal Cases': keyword = keyword + ' AND legal cases[pt]'
    elif pubtype == 'Legislation': keyword = keyword + ' AND legislation[pt]'
    elif pubtype == 'Letter': keyword = keyword + ' AND letter[pt]'
    elif pubtype == 'Meta-Analysis': keyword = keyword + ' AND meta-analysis[pt]'
    elif pubtype == 'Multicenter Study': keyword = keyword + ' AND multicenter study[pt]'
    elif pubtype == 'News': keyword = keyword + ' AND news[pt]'
    elif pubtype == 'Newspaper Article': keyword = keyword + ' AND newspaper article[pt]'
    elif pubtype == 'Overall': keyword = keyword + ' AND overall[pt]'
    elif pubtype == 'Periodical Index': keyword = keyword + ' AND periodical index[pt]'
    elif pubtype == 'Practice Guideline': keyword = keyword + ' AND practice guideline[pt'
    elif pubtype == 'Published Erratum': keyword = keyword + ' AND published erratum[pt]'
    elif pubtype == 'Randomized Controlled Trial': keyword = keyword + ' AND randomized controlled trial[pt]'
    elif pubtype == 'Retraction of Publication': keyword = keyword + ' AND retraction of publication[pt]'
    elif pubtype == 'Retracted Publication': keyword = keyword + ' AND retracted publication[pt]'
    elif pubtype == 'Review': keyword = keyword + ' AND review[pt]'
    elif pubtype == 'Review, Academic': keyword = keyword + ' AND review, academic[pt]'
    elif pubtype == 'Review Literature': keyword = keyword + ' AND review, literature[pt]'
    elif pubtype == 'Review, Multicase': keyword = keyword + ' AND review, multicase[pt]'
    elif pubtype == 'Review of Reported Cases': keyword = keyword + ' AND review of reported cases[pt]'
    elif pubtype == 'Review, Tutorial': keyword = keyword + ' AND review, tutorial[pt]'
    elif pubtype == 'Scientific Integrity Review': keyword = keyword + ' AND scientific integrity review[pt]'
    elif pubtype == 'Technical Report': keyword = keyword + ' AND technical report[pt]'
    elif pubtype == 'Twin Study': keyword = keyword + ' AND twin study[pt]'
    elif pubtype == 'Validation Studies': keyword = keyword + ' AND validation studies[pt]'
    
    # Below are language limits to add to keyword if chosen

    if language == 'English': keyword = keyword + ' AND english[la]'
    elif language == 'French': keyword = keyword + ' AND french[la]'
    elif language == 'German': keyword = keyword + ' AND german[la]'
    elif language == 'Italian': keyword = keyword + ' AND italian[la]'
    elif language == 'Japanese': keyword = keyword + ' AND japanese[la]'
    elif language == 'Russian': keyword = keyword + ' AND russian[la]'
    elif language == 'Spanish': keyword = keyword + ' AND spanish[la]'

    # Below are subset limits to add to keyword if chosen

    if subset == 'AIDS': keyword = keyword + ' AND aids[sb]'
    elif subset == 'AIDS/HIV journals': keyword = keyword + ' AND jsubsetx' #X -  AIDS/HIV journals, non-Index Medicus 
    elif subset == 'Bioethics': keyword = keyword + ' AND bioethics[ab]'
    elif subset == 'Bioethics journals': keyword = keyword + ' AND jsubsete' #E -  bioethics journals, non-Index Medicus
    elif subset == 'Biotechnology journals': keyword = keyword + ' AND jsubsetb' #B -  biotechnology journals (assigned 1990 - 1998), non-Index Medicus 
    elif subset == 'Communication disorders journals': keyword = keyword + ' AND jusbsetc' #C -  communication disorders journals (assigned 1977 - 1997), non-Index Medicus 
    elif subset == 'Complementary and Alternative Medicine': keyword = keyword + ' AND cam[sb]'
    elif subset == 'Consumer health journals': keyword = keyword + ' AND jsubsetk' #K -  consumer health journals, non-Index Medicus 
    elif subset == 'Core clinical journals': keyword = keyword + ' AND jsubsetaim' #AIM - Abridged Index Medicus A list of core clinical journals created 20 years ago 
    elif subset == 'Dental journals': keyword = keyword + ' AND jsubsetd' #D  -  dentistry journals 
    elif subset == 'Health administration journals': keyword = keyword + ' AND jsubseth' #H -  health administration journals, non-Index Medicus 
    elif subset == 'Health tech assesment journals': keyword = keyword + ' AND jsubsett'#T -  health technology assessment journals, non-Index Medicus 
    elif subset == 'History of Medicine': keyword = keyword + ' AND history[sb]'
    elif subset == 'History of Medicine journals': keyword = keyword + ' AND jsubsetq' #Q -  history of medicine journals, non-Index Medicus 
    elif subset == 'In process': keyword = keyword + ' AND in process[sb]'
    elif subset == 'Index Medicus journals': keyword = keyword + ' AND jsubsetim' #IM -  Index Medicus journals 
    elif subset == 'MEDLINE': keyword = keyword + ' AND medline[sb]'
    elif subset == 'NASA journals': keyword = keyword + ' AND jsubsets' #S -  National Aeronautics and Space Administration (NASA) journals, non-Index Medicus 
    elif subset == 'Nursing journals': keyword = keyword + ' AND jsubsetn' #N  -  nursing journals 
    elif subset == 'PubMed Central': keyword = keyword + ' AND medline pmc[sb]'
    elif subset == 'Reproduction journals': keyword = keyword + ' AND jsubsetr' #R -  reproduction journals (assigned 1972 - 1979), non-Index Medicus
    elif subset == 'Space Life Sciences': keyword = keyword + ' AND space[sb]'
    elif subset == 'Supplied by Publisher': keyword = keyword + ' AND publisher[sb]'
    elif subset == 'Toxicology': keyword = keyword + ' AND tox[sb]'

    # Age range will be added to keyword if desired
    if agerange == 'All Infant: birth-23 month': keyword = keyword + ' AND infant[mh]'
    elif agerange == 'All Child: 0-18 years': keyword = keyword + ' AND child[mh]'
    elif agerange == 'All Adult: 19+ years': keyword = keyword + ' AND adult[mh]'
    elif agerange == 'Newborn: birth-1 month': keyword = keyword + ' AND infant, newborn[mh]'
    elif agerange == 'Infant: 1-23 months': keyword = keyword + ' AND infant[mh]'
    elif agerange == 'Preschool Child: 2-5 years': keyword = keyword + ' AND child, preschool[mh]'
    elif agerange == 'Child: 6-12 years': keyword = keyword + ' AND child[mh]'
    elif agerange == 'Adolescent: 13-18 years': keyword = keyword + ' AND adolescence[mh]'
    elif agerange == 'Adult: 19-44 years': keyword = keyword + ' AND adult[mh]'
    elif agerange == 'Middle Aged: 45-64 years': keyword = keyword + ' AND middle age[mh]'
    elif agerange == 'Aged: 65+ years': keyword = keyword + ' AND aged[mh]'
    elif agerange == '80 and over: 80+ years': keyword = keyword + ' AND aged, 80 and over[mh]'

    # Human or animal studies limit will be added to keyword if desired
    if humananimal == 'Human': keyword = keyword + ' AND human[mh]'
    elif humananimal == 'Animal': keyword = keyword + ' AND animal[mh]'

    # Studies done on either females or males will be a limit of keyword
    if gender == 'Female': keyword = keyword + ' AND female[mh]'
    elif gender == 'Male': keyword = keyword + ' AND male[mh]'
    
    # Past Entrez date range will be added to keyword; the number is the relative number of days prior to today
    if entrezdate == '30 Days': entrezdate = '30'
    elif entrezdate == '60 Days': entrezdate = '60'
    elif entrezdate == '90 Days': entrezdate = '90'
    elif entrezdate == '180 Days': entrezdate = '180'
    elif entrezdate == '1 Year': entrezdate = '365'
    elif entrezdate == '2 Years': entrezdate = '730'
    elif entrezdate == '5 Years': entrezdate = '1825'
    elif entrezdate == '10 Years': entrezdate = '3650'

    # if date limits are provided, then the following will be added to keyword
    # I will only allow this if the relative entrez date is not specified above, hence the elif command
    # This is where I used the time function, gmtime() to get the current global mean time
    elif fromdate != '':
        if todate == '':
            if pubdate == 'Publication Date': keyword = keyword + ' ' + fromdate + ':' + time.strftime('%Y/%m/%d', time.gmtime()) + '[dp]'
            elif pubdate == 'Entrez Date': keyword = keyword + ' ' + fromdate +':' + time.strftime('%Y/%m/%d',time.gmtime()) + '[edat]'
        else:
            if pubdate == 'Publication Date': keyword = keyword + ' ' + fromdate + ':' + todate + '[dp]'
            elif pubdate == 'Entrez Date': keyword = keyword + ' ' + fromdate + ':' + todate + '[edat]'

    # Below is the actual call to the URL (PubMed's cgi): first to gain the pubmed UIDs
    # and then to get the entries that is passed to pyblio to open
    uids = query_info (keyword, field, maxcount, displaystart, entrezdate) # get the pubmed UIDs and dump into uids variable
    
    uids = string.replace (str(uids),'[','') # get rid of open bracket in string
    uids = string.replace (str(uids),']','') # get rid of close bracket in the string
    uids = string.replace (str(uids),' ','') # get rid of all the spaces in the string

    if uids.strip () == '': return None
    
    params = urllib.urlencode ({
        'db'     : 'pubmed',
        'report' : 'medline',
        'mode'   : 'text'
        })

    url = "%s?%s&id=%s" % (fetch_url, params, str(uids))

    file, data = urllib.urlretrieve (url)
    
    return file

