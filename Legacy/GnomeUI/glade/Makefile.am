gladedir   = $(datadir)/$(PACKAGE)$(EXTENSION)/glade
appicondir = $(datadir)/pixmaps

glade_DATA = 					\
	fields1.glade				\
	pyblio.glade 				\
	search.glade 				\
	sort.glade 				\
	format.glade				\
	medline.glade 				\
	fetch.glade 				\
	config1.glade				\
	openurl.glade				\
	wpconnect.glade

EXTRA_DIST = $(glade_DATA) pyblio.glade.in

pyblio.glade: pyblio.glade.in Makefile
	sed -e 's^\@icondir\@^$(appicondir)^g' 		\
	< $(srcdir)/pyblio.glade.in > pyblio.glade.tmp 	\
	&& mv pyblio.glade.tmp pyblio.glade
