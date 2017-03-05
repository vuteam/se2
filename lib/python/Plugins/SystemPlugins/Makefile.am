installdir = $(pkglibdir)/python/Plugins/SystemPlugins

SUBDIRS = SoftwareManager PositionerSetup Satfinder \
	SatelliteEquipmentControl VideoTune Hotplug CableScan \
	DefaultServicesScanner DiseqcTester CommonInterfaceAssignment \
	FastScan OSD3DSetup HdmiCEC VideoClippingSetup \
	VideoEnhancement WirelessLan NetworkWizard

if HAVE_TEMPFANCONTROL
SUBDIRS += TempFanControl
endif

if HAVE_LIBVUGLES2
SUBDIRS += AnimationSetup
endif

if HAVE_OSDANIMATION
SUBDIRS += AnimationSetup
endif

if WETEKPLAY
SUBDIRS += WetekFRQ
endif

install_PYTHON = __init__.py
