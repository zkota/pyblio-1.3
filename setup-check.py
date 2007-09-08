# -*- coding: utf-8 -*-

import sys, string, re, traceback, os

base_version = string.split (sys.version) [0]
base_version = re.match ('[\d\.]+', base_version).group (0)

version = map (int, string.split (base_version, '.'))
if len (version) < 3: version.append (0)
fd = open ('conftest.out', 'w')
fd.write ('Python_Version=%s\n' % base_version)
fd.write ('Python_Major_Version=%d\n' % version [0])
fd.write ('Python_Minor_Version=%d\n' % version [1])
fd.write ('Python_Micro_Version=%d\n' % version [2])
fd.write ('Python_Prefix="%s"\n' % sys.exec_prefix)
fd.close ()


def error (msg):
    fd = open ('conftest.out', 'a')
    fd.write ('Status="%s"\n' % msg)
    fd.close ()
    sys.exit (1)

def warning (msg):
    fd = open ('conftest.out', 'a')
    fd.write ('Status="%s"\n' % msg)
    fd.close ()

requested_python, requested_pyblio = sys.argv[1:]

testversion = map(int, requested_python.split('.'))
if len (testversion) < 3:
    testversion.append(0)

if version < testversion:
    error ('requested version for python is %s, but I detected %s' % (
        requested_python, sys.version))

# check the version of pyblio-core
try:
    from Pyblio import numeric_version as pyblio_version
    from Pyblio import version
except ImportError:
    error('cannot import pyblio-core')
else:
    if pyblio_version < tuple(int(x) for x in requested_pyblio.split('.')):
        error('this version of pyblio requires pyblio-core-%s, detected %s' % (
            requested_pyblio, version))
    else:
        fd = open ('conftest.out', 'a')
        fd.write ('PyblioCore_Version="%s"\n' % version)
        fd.close ()

# check for gtk and gnome 2.0
try:
    import pygtk
	
    pygtk.require('2.0')
    
    import gnome, gtk
    import gtk.glade
    import gnome.ui
    import gconf

    v = string.join (map (str, gtk.pygtk_version), '.')

    fd = open ('conftest.out', 'a')
    fd.write ('PyGtk_Version="%s"\n' % v)
    fd.close ()
except ImportError, msg:
    error('error in python modules dependencies: %s' % msg)

except AssertionError, msg:
    error('gtk problem: %s' % msg)

except RuntimeError, msg:
    if os.environ.get('DISPLAY', '') != '':
        etype, value, tb = sys.exc_info()
        traceback.print_exception(etype, value, tb)
        error('unexpected runtime error')

    warning('cannot test gtk [no DISPLAY]')
except:
    etype, value, tb = sys.exc_info ()
    traceback.print_exception (etype, value, tb)

    error ('unexpected error')
else:
    if gtk.pygtk_version < (2,4,0):
        error ('requested version for PyGtk is %s, but I detected %s' % ('2.4.0', v))

try:
    import _recode
    import _bibtex
    import Pyblio

    rq = _recode.request('latin1..latex')

    l = 'abcd'
    c = _recode.recode(rq, l)

    if l != c:
        error('broken recode version')
except ImportError, msg:
    error('error in python modules dependencies: %s' % msg)

try:
    _bibtex.next_unfiltered
except AttributeError, msg:
    error('Error in python-bibtex module: required function »next_unfiltered« missing: %s'
	   % msg)
except:
    etype, value, tb = sys.exc_info ()
    traceback.print_exception (etype, value, tb)
    error('unexpected error')
