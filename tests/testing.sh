#!/bin/sh

run () 
{
	eval $*
	if test $? != 0 ; then	
		echo "error: while processing $*" 1>&2
		exit 1
	fi
}

tst_start ()
{
    source="${srcdir}/.."

    PYTHONPATH="${PYTHONPATH}:${source}:../compiled:${source}/extras"
    export PYTHONPATH

    run ln -fs \
	${source}/Pyblio \
	${source}/Styles/Alpha.xml \
	${source}/pybrc.py \
	.
}

tst_stop ()
{
    run rm -f Pyblio pybrc.py Alpha.xml
}

