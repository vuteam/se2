installdir = $(pkglibdir)/python/Plugins/Extensions

SUBDIRS = TuxboxPlugins CutListEditor PicturePlayer MediaScanner MediaPlayer GraphMultiEPG SocketMMI DVDBurn

if HAVE_LIBDDVD
SUBDIRS += DVDPlayer
endif

if VUSOLO4K
SUBDIRS += MiniTV
endif

if VUULTIMO4K
SUBDIRS += MiniTV
endif

if HAVE_WETEK_XBMC
SUBDIRS += StartKodi
endif

install_PYTHON =	\
	__init__.py
