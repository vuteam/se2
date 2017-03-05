SUBDIRS = countries fonts extensions keymaps 

dist_pkgdata_DATA = \
	encoding.conf \
	keymap.xml \
	menu.xml \
	prev.png \
	black.mvi \
	hd-testcard.mvi \
	rcpositions.xml \
	setup.xml \
	skin_default.xml \
	skin_subtitles.xml \
	startwizard.xml \
	skin.xml \
	userinterfacepositionerwizard.xml \
	freesat.t1 \
	freesat.t2 \
	timezone.xml \
	unicable.xml \
	videowizard.xml

if HAVE_TEXTLCD
if SPARK
SUBDIRS += displaydualtext
else
SUBDIRS += displaytext
endif
endif

if HAVE_COLORLCD2
SUBDIRS += display96
endif

if HAVE_COLORLCD220
SUBDIRS += display220
endif

if HAVE_COLORLCD400
SUBDIRS += display400
endif

if HAVE_COLORLCD480
SUBDIRS += display480
endif

if HAVE_BWLCD140
SUBDIRS += vfd140
endif

if HAVE_BWLCD255
SUBDIRS += vfd255
endif

#skin_display.xml: $(srcdir)/skin_display_default.xml
#	test -f $(srcdir)/skin_display_$(BOXTYPE).xml && cp $(srcdir)/skin_display_$(BOXTYPE).xml skin_display.xml || cp $(srcdir)/skin_display_default.xml skin_display.xml
