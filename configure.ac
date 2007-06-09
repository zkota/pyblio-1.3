dnl -*- m4 -*-
dnl This file is part of pybliographer
dnl
dnl Copyright (C) 1998-2004 Frederic GOBRY
dnl Email : gobry@pybliographer.org
dnl          
dnl This program is free software; you can redistribute it and/or
dnl modify it under the terms of the GNU General Public License
dnl as published by the Free Software Foundation; either version 2 
dnl of the License, or (at your option) any later version.
dnl   
dnl This program is distributed in the hope that it will be useful,
dnl but WITHOUT ANY WARRANTY; without even the implied warranty of
dnl MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
dnl GNU General Public License for more details. 
dnl
dnl You should have received a copy of the GNU General Public License
dnl along with this program; if not, write to the Free Software 
dnl Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
dnl
dnl
dnl Process this file with autoconf to produce a configure script.

AC_PREREQ(2.57)

AC_INIT
AM_INIT_AUTOMAKE(pyblio, 1.3.0)
AC_SUBST(EXTENSION, [-1.3])

AC_CONFIG_SRCDIR(pybliographer.py)

AC_PROG_LN_S

AC_PATH_PROG(Python, python, no)

if test "${Python}" = "no" ; then
  AC_MSG_ERROR([please install python first])
fi

dnl Python version
MINIMUM_VERSION="2.3"

AC_MSG_CHECKING([python requirements])

${Python} ${srcdir}/setup-check.py ${MINIMUM_VERSION} 2>&5 1>&2

result=$?

if test -f conftest.out ; then
	. ./conftest.out
	rm -f conftest.out
else
	AC_MSG_RESULT([no])
	AC_MSG_ERROR([unable to run the test program])
fi

if test $result = 0 ; then
	if test -z "${Status}" ; then
	  AC_MSG_RESULT([yes (python ${Python_Version}, python-gtk ${PyGtk_Version})])
        else
          AC_MSG_RESULT([assuming yes (${Status})])
        fi
else
	AC_MSG_RESULT([no])
	AC_MSG_ERROR([${Status}])
fi

dnl NLS is now hand-managed for python.

AC_CONFIG_FILES(	
	Makefile 
	po/Makefile
	etc/installer
	scripts/Makefile
	tests/Makefile
	Legacy/Makefile
	Legacy/GnomeUI/Makefile
	Legacy/GnomeUI/glade/Makefile
	Legacy/Format/Makefile
	Legacy/Output/Makefile
	Legacy/ConfDir/Makefile
	Legacy/Style/Makefile
	doc/Makefile
	doc/C/Makefile
	Styles/Makefile
)


AC_OUTPUT

echo "pyblio is now configured. Type make to build it"
