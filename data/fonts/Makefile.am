#
# WARNING: If you modify the files installed here, change the version
# number of the enigma2-fonts package in enigma2.bb.
#

installdir = $(datadir)/fonts

dist_install_DATA = \
	ae_AlMateen.ttf \
	andale.ttf \
	lcd.ttf \
	md_khmurabi_10.ttf \
	nmsbd.ttf \
	LiberationSans-Bold.ttf \
	LiberationSans-BoldItalic.ttf \
	LiberationSans-Italic.ttf \
	LiberationSans-Regular.ttf

if VUULTIMO
dist_install_DATA += analog.ttf MyriadPro-Regular.otf MyriadPro-Semibold.otf MyriadPro-SemiboldIt.otf
endif

if VUDUO2
dist_install_DATA += analog.ttf MyriadPro-Regular.otf MyriadPro-Semibold.otf MyriadPro-SemiboldIt.otf
endif

if VUSOLO4K
dist_install_DATA += analog.ttf MyriadPro-Regular.otf MyriadPro-Semibold.otf MyriadPro-SemiboldIt.otf
endif

if VUULTIMO4K
dist_install_DATA += analog.ttf MyriadPro-Regular.otf MyriadPro-Semibold.otf MyriadPro-SemiboldIt.otf
endif

if HAVE_COLORLCD220
dist_install_DATA += hd2.ttf tuxtxt2.ttf
endif

if HAVE_COLORLCD400
dist_install_DATA += hd2.ttf tuxtxt2.ttf robotobold.ttf robotoregular.ttf
endif
