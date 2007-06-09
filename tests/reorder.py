import sys
from Legacy import Selection, Sort

a = bibopen (sys.argv [2])
f = open (sys.argv [3], 'w')

# write out in the key order
sel = Selection.Selection (sort = Sort.Sort ([Sort.KeySort ()]))
it  = sel.iterator (a.iterator ())

bibwrite (it, out = f, how = a.id)
