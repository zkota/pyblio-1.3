gladedir = $(datadir)/$(PACKAGE)/glade

glade_DATA = 					\
	pyblio.glade 				\
	search.glade 				\
	sort.glade 				\
	format.glade				\
	medline.glade 				\
	config1.glade


messages.pot: $(glade_DATA:%.glade=%.glade.h)

	xgettext -o messages.pot --language=c --keyword=N_ \
		--from-code=utf-8 $(glade_DATA:%.glade=%.glade.h)

%.glade.h: %.glade
	intltool-extract --type=gettext/glade $<

EXTRA_DIST = $(glade_DATA)

