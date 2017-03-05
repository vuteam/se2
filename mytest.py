import sys, os
from time import time

if os.path.isfile("/usr/lib/enigma2/python/enigma.zip"):
	sys.path.append("/usr/lib/enigma2/python/enigma.zip")

from Tools.Profile import profile, profile_final
profile("PYTHON_START")

import Tools.RedirectOutput
import enigma
from boxbranding import getBoxType, getBrandOEM
import eConsoleImpl
import eBaseImpl
enigma.eTimer = eBaseImpl.eTimer
enigma.eSocketNotifier = eBaseImpl.eSocketNotifier
enigma.eConsoleAppContainer = eConsoleImpl.eConsoleAppContainer
boxtype = getBoxType()

from traceback import print_exc

profile("SetupDevices")
import Components.SetupDevices
Components.SetupDevices.InitSetupDevices()

profile("SimpleSummary")
from Screens import InfoBar
from Screens.SimpleSummary import SimpleSummary

from sys import stdout, exc_info

profile("Bouquets")
from Components.config import config, configfile, ConfigText, ConfigYesNo, ConfigInteger, NoSave, ConfigSelection
config.misc.load_unlinked_userbouquets = ConfigYesNo(default=True)
def setLoadUnlinkedUserbouquets(configElement):
	enigma.eDVBDB.getInstance().setLoadUnlinkedUserbouquets(configElement.value)
config.misc.load_unlinked_userbouquets.addNotifier(setLoadUnlinkedUserbouquets)
enigma.eDVBDB.getInstance().reloadBouquets()

profile("ParentalControl")
import Components.ParentalControl
Components.ParentalControl.InitParentalControl()

profile("LOAD:Navigation")
from Navigation import Navigation

profile("LOAD:skin")
from skin import readSkin

profile("LOAD:Tools")
from Tools.Directories import InitFallbackFiles, resolveFilename, SCOPE_PLUGINS, SCOPE_CURRENT_SKIN
InitFallbackFiles()

profile("config.misc")
config.misc.boxtype = ConfigText(default = getBoxType())
config.misc.radiopic = ConfigText(default = resolveFilename(SCOPE_CURRENT_SKIN, "radio.mvi"))
config.misc.blackradiopic = ConfigText(default = resolveFilename(SCOPE_CURRENT_SKIN, "black.mvi"))
config.misc.startCounter = ConfigInteger(default=0) # number of e2 starts...
config.misc.standbyCounter = NoSave(ConfigInteger(default=0)) # number of standby
config.misc.DeepStandby = NoSave(ConfigYesNo(default=False)) # detect deepstandby
config.misc.RestartUI = ConfigYesNo(default=False) # detect user interface restart
config.misc.prev_wakeup_time = ConfigInteger(default=0)
#config.misc.prev_wakeup_time_type is only valid when wakeup_time is not 0
config.misc.prev_wakeup_time_type = ConfigInteger(default=0)
# 0 = RecordTimer, 1 = ZapTimer, 2 = Plugins, 3 = WakeupTimer
config.misc.epgcache_filename = ConfigText(default = "/hdd/epg.dat")
config.misc.SyncTimeUsing = ConfigSelection(default = "1", choices = [("0", "Transponder Time"), ("1", _("NTP"))])
config.misc.NTPserver = ConfigText(default = 'pool.ntp.org', fixed_size=False)

def setEPGCachePath(configElement):
	enigma.eEPGCache.getInstance().setCacheFile(configElement.value)

#demo code for use of standby enter leave callbacks
#def leaveStandby():
#	print "!!!!!!!!!!!!!!!!!leave standby"

#def standbyCountChanged(configElement):
#	print "!!!!!!!!!!!!!!!!!enter standby num", configElement.value
#	from Screens.Standby import inStandby
#	inStandby.onClose.append(leaveStandby)

#config.misc.standbyCounter.addNotifier(standbyCountChanged, initial_call = False)
####################################################

def useSyncUsingChanged(configElement):
	if config.misc.SyncTimeUsing.getValue() == "0":
		print "[Time By]: Transponder"
		enigma.eDVBLocalTimeHandler.getInstance().setUseDVBTime(True)
		enigma.eEPGCache.getInstance().timeUpdated()
	else:
		print "[Time By]: NTP"
		enigma.eDVBLocalTimeHandler.getInstance().setUseDVBTime(False)
		enigma.eEPGCache.getInstance().timeUpdated()
config.misc.SyncTimeUsing.addNotifier(useSyncUsingChanged)

def NTPserverChanged(configElement):
	if config.misc.NTPserver.getValue() == "pool.ntp.org":
		return
	print "[NTPDATE] save /etc/default/ntpdate"
	f = open("/etc/default/ntpdate", "w")
	f.write('NTPSERVERS="' + config.misc.NTPserver.value + '"')
	f.close()
	os.chmod("/etc/default/ntpdate", 0755)
	from Components.Console import Console
	Console = Console()
	Console.ePopen('/usr/bin/ntpdate-sync')
config.misc.NTPserver.addNotifier(NTPserverChanged, immediate_feedback = True)

profile("Twisted")
try:
	import e2reactor
	e2reactor.install()

	from twisted.internet import reactor

	def runReactor():
		reactor.run(installSignalHandlers=False)
except ImportError:
	print "twisted not available"
	def runReactor():
		enigma.runMainloop()

profile("LOAD:Plugin")

# initialize autorun plugins and plugin menu entries
from Components.PluginComponent import plugins

profile("LOAD:Wizard")
from Screens.Wizard import wizardManager
from Screens.StartWizard import *
import Screens.Rc
from Tools.BoundFunction import boundFunction
from Plugins.Plugin import PluginDescriptor

profile("misc")
had = dict()

def dump(dir, p = ""):
	if isinstance(dir, dict):
		for (entry, val) in dir.items():
			dump(val, p + "(dict)/" + entry)
	if hasattr(dir, "__dict__"):
		for name, value in dir.__dict__.items():
			if not had.has_key(str(value)):
				had[str(value)] = 1
				dump(value, p + "/" + str(name))
			else:
				print p + "/" + str(name) + ":" + str(dir.__class__) + "(cycle)"
	else:
		print p + ":" + str(dir)

# + ":" + str(dir.__class__)

# display

profile("LOAD:ScreenGlobals")
from Screens.Globals import Globals
from Screens.SessionGlobals import SessionGlobals
from Screens.Screen import Screen

profile("Screen")
Screen.global_screen = Globals()

# Session.open:
# * push current active dialog ('current_dialog') onto stack
# * call execEnd for this dialog
#   * clear in_exec flag
#   * hide screen
# * instantiate new dialog into 'current_dialog'
#   * create screens, components
#   * read, apply skin
#   * create GUI for screen
# * call execBegin for new dialog
#   * set in_exec
#   * show gui screen
#   * call components' / screen's onExecBegin
# ... screen is active, until it calls 'close'...
# Session.close:
# * assert in_exec
# * save return value
# * start deferred close handler ('onClose')
# * execEnd
#   * clear in_exec
#   * hide screen
# .. a moment later:
# Session.doClose:
# * destroy screen

class Session:
	def __init__(self, desktop = None, summary_desktop = None, navigation = None):
		self.desktop = desktop
		self.summary_desktop = summary_desktop
		self.nav = navigation
		self.delay_timer = enigma.eTimer()
		self.delay_timer.callback.append(self.processDelay)

		self.current_dialog = None

		self.dialog_stack = [ ]
		self.summary_stack = [ ]
		self.summary = None

		self.in_exec = False

		self.screen = SessionGlobals(self)

		##### hack for Openwebif - Create folders & symlink
		from enigma import eEnv
		from Tools.Directories import fileExists
		import os
		origwebifpath = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/WebInterface')
		hookpath = eEnv.resolve('${libdir}/enigma2/python/Plugins/Extensions/OpenWebif/pluginshook.src')
		if not os.path.islink(origwebifpath + "/WebChilds/Toplevel.py") and os.path.exists(hookpath):
			print "[OpenWebif] hooking original webif plugins"

			cleanuplist = [
				"/__init__.py",
				"/__init__.pyo",
				"/__init__.pyc",
				"/WebChilds/__init__.py",
				"/WebChilds/__init__.pyo",
				"/WebChilds/__init__.pyc",
				"/WebChilds/External/__init__.py",
				"/WebChilds/External/__init__.pyo",
				"/WebChilds/External/__init__.pyc",
				"/WebChilds/Toplevel.py",
				"/WebChilds/Toplevel.pyo"
				"/WebChilds/Toplevel.pyc"
			]

			for cleanupfile in cleanuplist:
				if fileExists(origwebifpath + cleanupfile):
					os.remove(origwebifpath + cleanupfile)

			if not os.path.exists(origwebifpath + "/WebChilds/External"):
				os.makedirs(origwebifpath + "/WebChilds/External")
			open(origwebifpath + "/__init__.py", "w").close()
 			open(origwebifpath + "/WebChilds/__init__.py", "w").close()
 			open(origwebifpath + "/WebChilds/External/__init__.py", "w").close()

			os.symlink(hookpath, origwebifpath + "/WebChilds/Toplevel.py")
		######################################################
		# include auto3D
		from Screens.UserInterfacePositioner import auto3D
		from Components.SystemInfo import SystemInfo
		if SystemInfo["3DMode"]:
			auto3D(self)
		#####################

		for p in plugins.getPlugins(PluginDescriptor.WHERE_SESSIONSTART):
			try:
				p(reason=0, session=self)
			except:
				print "Plugin raised exception at WHERE_SESSIONSTART"
				import traceback
				traceback.print_exc()


	def processDelay(self):
		callback = self.current_dialog.callback

		retval = self.current_dialog.returnValue

		if self.current_dialog.isTmp:
			self.current_dialog.doClose()
#			dump(self.current_dialog)
			del self.current_dialog
		else:
			del self.current_dialog.callback

		## hack for ready eDVBLocalTimeHandler
		enigma.eDVBLocalTimeHandler.getInstance().syncDVBTime()

		self.popCurrent()
		if callback is not None:
			callback(*retval)

	def execBegin(self, first=True, do_show = True):
		assert not self.in_exec
		self.in_exec = True
		c = self.current_dialog

		# when this is an execbegin after a execend of a "higher" dialog,
		# popSummary already did the right thing.
		if first:
			self.instantiateSummaryDialog(c)

		c.saveKeyboardMode()
		c.execBegin()

		# when execBegin opened a new dialog, don't bother showing the old one.
		if c == self.current_dialog and do_show:
			c.show()

	def execEnd(self, last=True):
		assert self.in_exec
		self.in_exec = False

		self.current_dialog.execEnd()
		self.current_dialog.restoreKeyboardMode()
		self.current_dialog.hide()

		if last and self.summary:
			self.current_dialog.removeSummary(self.summary)
			self.popSummary()

	def instantiateDialog(self, screen, *arguments, **kwargs):
		return self.doInstantiateDialog(screen, arguments, kwargs, self.desktop)

	def deleteDialog(self, screen):
		screen.hide()
		screen.doClose()

	def deleteDialogWithCallback(self, callback, screen, *retval):
		screen.hide()
		screen.doClose()
		if callback is not None:
			callback(*retval)

	def instantiateSummaryDialog(self, screen, **kwargs):
		self.pushSummary()
		summary = screen.createSummary() or SimpleSummary
		arguments = (screen,)
		self.summary = self.doInstantiateDialog(summary, arguments, kwargs, self.summary_desktop)
		self.summary.show()
		screen.addSummary(self.summary)

	def doInstantiateDialog(self, screen, arguments, kwargs, desktop):
		# create dialog
		dlg = screen(self, *arguments, **kwargs)
		if dlg is None:
			return
		# read skin data
		readSkin(dlg, None, dlg.skinName, desktop)
		# create GUI view of this dialog
		dlg.setDesktop(desktop)
		dlg.applySkin()
		return dlg

	def pushCurrent(self):
		if self.current_dialog is not None:
			self.dialog_stack.append((self.current_dialog, self.current_dialog.shown))
			self.execEnd(last=False)

	def popCurrent(self):
		if self.dialog_stack:
			(self.current_dialog, do_show) = self.dialog_stack.pop()
			self.execBegin(first=False, do_show=do_show)
		else:
			self.current_dialog = None

	def execDialog(self, dialog):
		self.pushCurrent()
		self.current_dialog = dialog
		self.current_dialog.isTmp = False
		self.current_dialog.callback = None # would cause re-entrancy problems.
		self.execBegin()

	def openWithCallback(self, callback, screen, *arguments, **kwargs):
		dlg = self.open(screen, *arguments, **kwargs)
		dlg.callback = callback
		return dlg

	def open(self, screen, *arguments, **kwargs):
		if self.dialog_stack and not self.in_exec:
			raise RuntimeError("modal open are allowed only from a screen which is modal!")
			# ...unless it's the very first screen.

		self.pushCurrent()
		dlg = self.current_dialog = self.instantiateDialog(screen, *arguments, **kwargs)
		dlg.isTmp = True
		dlg.callback = None
		self.execBegin()
		return dlg

	def close(self, screen, *retval):
		if not self.in_exec:
			print "close after exec!"
			return

		# be sure that the close is for the right dialog!
		# if it's not, you probably closed after another dialog
		# was opened. this can happen if you open a dialog
		# onExecBegin, and forget to do this only once.
		# after close of the top dialog, the underlying will
		# gain focus again (for a short time), thus triggering
		# the onExec, which opens the dialog again, closing the loop.
		assert screen == self.current_dialog

		self.current_dialog.returnValue = retval
		self.delay_timer.start(0, 1)
		self.execEnd()

	def pushSummary(self):
		if self.summary:
			self.summary.hide()
		self.summary_stack.append(self.summary)
		self.summary = None

	def popSummary(self):
		if self.summary:
			self.summary.doClose()
		self.summary = self.summary_stack and self.summary_stack.pop()
		if self.summary:
			self.summary.show()

profile("Standby,PowerKey")
import Screens.Standby
from Screens.Menu import MainMenu, mdom
from GlobalActions import globalActionMap

class PowerKey:
	""" PowerKey stuff - handles the powerkey press and powerkey release actions"""

	def __init__(self, session):
		self.session = session
		globalActionMap.actions["power_down"]=self.powerdown
		globalActionMap.actions["power_up"]=self.powerup
		globalActionMap.actions["power_long"]=self.powerlong
		globalActionMap.actions["deepstandby"]=self.shutdown # frontpanel long power button press
		globalActionMap.actions["discrete_off"]=self.standby
		self.standbyblocked = 1

	def MenuClosed(self, *val):
		self.session.infobar = None

	def shutdown(self):
		print "PowerOff - Now!"
		if not Screens.Standby.inTryQuitMainloop and self.session.current_dialog and self.session.current_dialog.ALLOW_SUSPEND:
			self.session.open(Screens.Standby.TryQuitMainloop, 1)

	def powerlong(self):
		if Screens.Standby.inTryQuitMainloop or (self.session.current_dialog and not self.session.current_dialog.ALLOW_SUSPEND):
			return
		self.doAction(action = config.usage.on_long_powerpress.getValue())

	def doAction(self, action):
		self.standbyblocked = 1
		if action == "shutdown":
			self.shutdown()
		elif action == "show_menu":
			print "Show shutdown Menu"
			root = mdom.getroot()
			for x in root.findall("menu"):
				y = x.find("id")
				if y is not None:
					id = y.get("val")
					if id and id == "shutdown":
						self.session.infobar = self
						menu_screen = self.session.openWithCallback(self.MenuClosed, MainMenu, x)
						menu_screen.setTitle(_("Standby / restart"))
						return
		elif action == "standby":
			self.standby()
		elif action == "restart":
			self.restart()

	def powerdown(self):
		self.standbyblocked = 0

	def powerup(self):
		if self.standbyblocked == 0:
			self.doAction(action = config.usage.on_short_powerpress.getValue())

	def standby(self):
		if not Screens.Standby.inStandby and self.session.current_dialog and self.session.current_dialog.ALLOW_SUSPEND and self.session.in_exec:
			self.session.open(Screens.Standby.Standby)

	def restart(self):
		print "Restart Box - Now!"
		if not Screens.Standby.inTryQuitMainloop and self.session.current_dialog and self.session.current_dialog.ALLOW_SUSPEND:
			self.session.open(Screens.Standby.TryQuitMainloop, 2)

profile("Scart")
from Screens.Scart import Scart

class AutoScartControl:
	def __init__(self, session):
		self.force = False
		self.current_vcr_sb = enigma.eAVSwitch.getInstance().getVCRSlowBlanking()
		if self.current_vcr_sb and config.av.vcrswitch.getValue():
			self.scartDialog = session.instantiateDialog(Scart, True)
		else:
			self.scartDialog = session.instantiateDialog(Scart, False)
		config.av.vcrswitch.addNotifier(self.recheckVCRSb)
		enigma.eAVSwitch.getInstance().vcr_sb_notifier.get().append(self.VCRSbChanged)

	def recheckVCRSb(self, configElement):
		self.VCRSbChanged(self.current_vcr_sb)

	def VCRSbChanged(self, value):
		#print "vcr sb changed to", value
		self.current_vcr_sb = value
		if config.av.vcrswitch.getValue() or value > 2:
			if value:
				self.scartDialog.showMessageBox()
			else:
				self.scartDialog.switchToTV()

profile("Load:CI")
from enigma import eDVBCIInterfaces
from Screens.Ci import CiHandler

profile("Load:VolumeControl")
from Components.VolumeControl import VolumeControl

def runScreenTest():
	config.misc.startCounter.value += 1
	config.misc.startCounter.save()

	profile("readPluginList")
	plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))

	profile("Init:Session")
	nav = Navigation()
	session = Session(desktop = enigma.getDesktop(0), summary_desktop = enigma.getDesktop(1), navigation = nav)

	CiHandler.setSession(session)

	screensToRun = [ p.__call__ for p in plugins.getPlugins(PluginDescriptor.WHERE_WIZARD) ]

	profile("wizards")
	screensToRun += wizardManager.getWizards()

	screensToRun.append((100, InfoBar.InfoBar))

	screensToRun.sort()

	enigma.ePythonConfigQuery.setQueryFunc(configfile.getResolvedKey)

	def runNextScreen(session, screensToRun, *result):
		if result:
			enigma.quitMainloop(*result)
			return

		screen = screensToRun[0][1]
		args = screensToRun[0][2:]

		if screensToRun:
			session.openWithCallback(boundFunction(runNextScreen, session, screensToRun[1:]), screen, *args)
		else:
			session.open(screen, *args)

	config.misc.epgcache_filename.addNotifier(setEPGCachePath)

	runNextScreen(session, screensToRun)

	profile("Init:VolumeControl")
	vol = VolumeControl(session)
	profile("Init:PowerKey")
	power = PowerKey(session)

	# we need session.scart to access it from within menu.xml
	session.scart = AutoScartControl(session)

	profile("Init:Trashcan")
	import Tools.Trashcan
	Tools.Trashcan.init(session)

	profile("Init:AutoVideoMode")
	import Screens.VideoMode
	Screens.VideoMode.autostart(session)

	profile("RunReactor")
	profile_final()

	if boxtype in ('sf8', 'classm', 'axodin', 'axodinc', 'starsatlx', 'genius', 'evo'):
		f = open("/dev/dbox/oled0", "w")
		f.write('-E2-')
		f.close()

	runReactor()

	profile("wakeup")

	from time import time, strftime, localtime
	from Tools.StbHardware import setFPWakeuptime, getFPWakeuptime, setRTCtime
	from Screens.SleepTimerEdit import isNextWakeupTime
	#get currentTime
	nowTime = time()
	if not config.misc.SyncTimeUsing.value == "0" or boxtype.startswith('gb') or getBrandOEM().startswith('ini'):
		print "dvb time sync disabled... so set RTC now to current linux time!", strftime("%Y/%m/%d %H:%M", localtime(nowTime))
		setRTCtime(nowTime)

	wakeupList = [
		x for x in ((session.nav.RecordTimer.getNextRecordingTime(), 0),
					(session.nav.RecordTimer.getNextZapTime(isWakeup=True), 1),
					(plugins.getNextWakeupTime(), 2),
					(isNextWakeupTime(), 3))
		if x[0] != -1
	]
	wakeupList.sort()
	if wakeupList:
		from time import strftime
		startTime = wakeupList[0]
		if (startTime[0] - nowTime) < 270: # no time to switch box back on
			wptime = nowTime + 30  # so switch back on in 30 seconds
		else:
			if boxtype.startswith("gb"):
				wptime = startTime[0] - 120 # Gigaboxes already starts 2 min. before wakeup time
			else:
				wptime = startTime[0] - 240
#		if not config.misc.SyncTimeUsing.getValue() == "0" or getBoxType().startswith('gb'):
#			print "dvb time sync disabled... so set RTC now to current linux time!", strftime("%Y/%m/%d %H:%M", localtime(nowTime))
#			setRTCtime(nowTime)
		print "set wakeup time to", strftime("%Y/%m/%d %H:%M", localtime(wptime))
		setFPWakeuptime(wptime)
		config.misc.prev_wakeup_time.value = int(startTime[0])
		config.misc.prev_wakeup_time_type.value = startTime[1]
		config.misc.prev_wakeup_time_type.save()
	else:
		config.misc.prev_wakeup_time.value = 0
	config.misc.prev_wakeup_time.save()

	profile("stopService")
	session.nav.stopService()
	profile("nav shutdown")
	session.nav.shutdown()

	profile("configfile.save")
	configfile.save()
	from Screens import InfoBarGenerics
	InfoBarGenerics.saveResumePoints()

	return 0

profile("Init:skin")
import skin
skin.loadSkinData(enigma.getDesktop(0))

profile("InputDevice")
import Components.InputDevice
Components.InputDevice.InitInputDevices()
import Components.InputHotplug

profile("AVSwitch")
import Components.AVSwitch
Components.AVSwitch.InitAVSwitch()
Components.AVSwitch.InitiVideomodeHotplug()

profile("RecordingConfig")
import Components.RecordingConfig
Components.RecordingConfig.InitRecordingConfig()

profile("UsageConfig")
import Components.UsageConfig
Components.UsageConfig.InitUsageConfig()

profile("Init:NTPSync")
import Components.NetworkTime
Components.NetworkTime.AutoNTPSync()

profile("keymapparser")
import keymapparser
keymapparser.readKeymap(config.usage.keymap.value)
keymapparser.readKeymap(config.usage.keytrans.value)

profile("Network")
import Components.Network
Components.Network.InitNetwork()

profile("LCD")
import Components.Lcd
Components.Lcd.InitLcd()

profile("UserInterface")
import Screens.UserInterfacePositioner
Screens.UserInterfacePositioner.InitOsd()

profile("RFMod")
import Components.RFmod
Components.RFmod.InitRFmod()

profile("Init:CI")
import Screens.Ci
Screens.Ci.InitCiConfig()

profile("RcModel")
import Components.RcModel

profile("IPv6")
if os.path.exists('/etc/enigma2/ipv6'):
	try:
		fp = open('/proc/sys/net/ipv6/conf/all/disable_ipv6', 'w')
		fp.write("1")
		fp.close()
	except:
		pass

#from enigma import dump_malloc_stats
#t = eTimer()
#t.callback.append(dump_malloc_stats)
#t.start(1000)

# first, setup a screen
try:
	runScreenTest()

	plugins.shutdown()

	Components.ParentalControl.parentalControl.save()
except:
	print 'EXCEPTION IN PYTHON STARTUP CODE:'
	print '-'*60
	print_exc(file=stdout)
	enigma.quitMainloop(5)
	print '-'*60
