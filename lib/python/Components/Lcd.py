from boxbranding import getBoxType

from twisted.internet import threads
from enigma import eDBoxLCD, eTimer

from config import config, ConfigSubsection, ConfigSelection, ConfigSlider, ConfigYesNo, ConfigNothing
from Components.SystemInfo import SystemInfo
from Tools.Directories import fileExists
import usb

def IconCheck(session=None, **kwargs):
	if fileExists("/proc/stb/lcd/symbol_network") or fileExists("/proc/stb/lcd/symbol_usb"):
		global networklinkpoller
		networklinkpoller = IconCheckPoller()
		networklinkpoller.start()

class IconCheckPoller:
	def __init__(self):
		self.timer = eTimer()

	def start(self):
		if self.iconcheck not in self.timer.callback:
			self.timer.callback.append(self.iconcheck)
		self.timer.startLongTimer(0)

	def stop(self):
		if self.iconcheck in self.timer.callback:
			self.timer.callback.remove(self.iconcheck)
		self.timer.stop()

	def iconcheck(self):
		try:
			threads.deferToThread(self.JobTask)
		except:
			pass
		self.timer.startLongTimer(30)

	def JobTask(self):
		LinkState = 0
		if fileExists('/sys/class/net/wlan0/operstate'):
			LinkState = open('/sys/class/net/wlan0/operstate').read()
			if LinkState != 'down':
				LinkState = open('/sys/class/net/wlan0/operstate').read()
		elif fileExists('/sys/class/net/eth0/operstate'):
			LinkState = open('/sys/class/net/eth0/operstate').read()
			if LinkState != 'down':
				LinkState = open('/sys/class/net/eth0/carrier').read()
		LinkState = LinkState[:1]
		if fileExists("/proc/stb/lcd/symbol_network") and config.lcd.mode.value == '1':
			f = open("/proc/stb/lcd/symbol_network", "w")
			f.write(str(LinkState))
			f.close()
		elif fileExists("/proc/stb/lcd/symbol_network") and config.lcd.mode.value == '0':
			f = open("/proc/stb/lcd/symbol_network", "w")
			f.write('0')
			f.close()

		USBState = 0
		busses = usb.busses()
		for bus in busses:
			devices = bus.devices
			for dev in devices:
				if dev.deviceClass != 9 and dev.deviceClass != 2 and dev.idVendor > 0:
					USBState = 1
		if fileExists("/proc/stb/lcd/symbol_usb") and config.lcd.mode.value == '1':
			f = open("/proc/stb/lcd/symbol_usb", "w")
			f.write(str(USBState))
			f.close()
		elif fileExists("/proc/stb/lcd/symbol_usb") and config.lcd.mode.value == '0':
			f = open("/proc/stb/lcd/symbol_usb", "w")
			f.write('0')
			f.close()

		self.timer.startLongTimer(30)

class LCD:
	def __init__(self):
		pass

	def setBright(self, value):
		value *= 255
		value /= 10
		if value > 255:
			value = 255
		eDBoxLCD.getInstance().setLCDBrightness(value)

	def setContrast(self, value):
		value *= 63
		value /= 20
		if value > 63:
			value = 63
		eDBoxLCD.getInstance().setLCDContrast(value)

	def setInverted(self, value):
		if value:
			value = 255
		eDBoxLCD.getInstance().setInverted(value)

	def setFlipped(self, value):
		eDBoxLCD.getInstance().setFlipped(value)

	def setScreenShot(self, value):
		eDBoxLCD.getInstance().setDump(value)

	def isOled(self):
		return eDBoxLCD.getInstance().isOled()

	def setMode(self, value):
		if fileExists("/proc/stb/lcd/show_symbols"):
			print 'setLCDMode',value
			f = open("/proc/stb/lcd/show_symbols", "w")
			f.write(value)
			f.close()

	def setPower(self, value):
		if fileExists("/proc/stb/power/vfd"):
			print 'setLCDPower',value
			f = open("/proc/stb/power/vfd", "w")
			f.write(value)
			f.close()
		elif fileExists("/proc/stb/lcd/vfd"):
			print 'setLCDPower',value
			f = open("/proc/stb/lcd/vfd", "w")
			f.write(value)
			f.close()

	def setfblcddisplay(self, value):
		print 'setfblcddisplay',value
		f = open("/proc/stb/fb/sd_detach", "w")
		f.write(value)
		f.close()

	def setRepeat(self, value):
		if fileExists("/proc/stb/lcd/scroll_repeats"):
			print 'setLCDRepeat',value
			f = open("/proc/stb/lcd/scroll_repeats", "w")
			f.write(value)
			f.close()

	def setScrollspeed(self, value):
		if fileExists("/proc/stb/lcd/scroll_delay"):
			print 'setLCDScrollspeed',value
			f = open("/proc/stb/lcd/scroll_delay", "w")
			f.write(str(value))
			f.close()

	def setLEDNormalState(self, value):
		eDBoxLCD.getInstance().setLED(value, 0)

	def setLEDDeepStandbyState(self, value):
		eDBoxLCD.getInstance().setLED(value, 1)

	def setLEDBlinkingTime(self, value):
		eDBoxLCD.getInstance().setLED(value, 2)

def leaveStandby():
	config.lcd.bright.apply()
	config.lcd.ledbrightness.apply()
	config.lcd.ledbrightnessdeepstandby.apply()

def standbyCounterChanged(configElement):
	from Screens.Standby import inStandby
	inStandby.onClose.append(leaveStandby)
	config.lcd.standby.apply()
	config.lcd.ledbrightnessstandby.apply()
	config.lcd.ledbrightnessdeepstandby.apply()

def InitLcd():
	if getBoxType() in ('wetekplay', 'wetekplay2', 'nanoc', 'nano', 'amikomini', 'dynaspark', 'amiko8900', 'sognorevolution', 'arguspingulux', 'arguspinguluxmini', 'arguspinguluxplus', 'sparkreloaded', 'sabsolo', 'sparklx', 'gis8120', 'gb800se', 'gb800solo', 'gb800seplus', 'gbultrase', 'gbipbox', 'tmsingle', 'tmnano2super', 'iqonios300hd', 'iqonios300hdv2', 'optimussos1plus', 'optimussos1', 'vusolo', 'et4x00', 'et5x00', 'et6x00', 'et7000', 'et7x00mini', 'mixosf7', 'mixoslumi', 'gbx1', 'gbx3', 'xpeedlxcs2', 'xpeedlxcc', 'zgemmai55', 'sf98'):
		detected = False
	else:
		detected = eDBoxLCD.getInstance().detected()
	SystemInfo["Display"] = detected
	config.lcd = ConfigSubsection()

	if fileExists("/proc/stb/lcd/mode"):
		f = open("/proc/stb/lcd/mode", "r")
		can_lcdmodechecking = f.read().strip().split(" ")
		f.close()
	else:
		can_lcdmodechecking = False
	SystemInfo["LCDMiniTV"] = can_lcdmodechecking

	if detected:
		ilcd = LCD()
		if can_lcdmodechecking:
			def setLCDModeMinitTV(configElement):
				try:
					f = open("/proc/stb/lcd/mode", "w")
					f.write(configElement.value)
					f.close()
				except:
					pass
			def setMiniTVFPS(configElement):
				try:
					f = open("/proc/stb/lcd/fps", "w")
					f.write("%d \n" % configElement.value)
					f.close()
				except:
					pass
			def setLCDModePiP(configElement):
				pass

			def setLCDScreenshot(configElement):
				ilcd.setScreenShot(configElement.value);

			config.lcd.modepip = ConfigSelection(choices={
					"0": _("off"),
					"5": _("PIP"),
					"7": _("PIP with OSD")},
					default = "0")
			if config.misc.boxtype.value == 'gbquad' or config.misc.boxtype.value == 'gbquadplus':
				config.lcd.modepip.addNotifier(setLCDModePiP)
			else:
				config.lcd.modepip = ConfigNothing()

			config.lcd.screenshot = ConfigYesNo(default=False)
			config.lcd.screenshot.addNotifier(setLCDScreenshot)

			config.lcd.modeminitv = ConfigSelection(choices={
					"0": _("normal"),
					"1": _("MiniTV"),
					"2": _("OSD"),
					"3": _("MiniTV with OSD")},
					default = "0")
			config.lcd.fpsminitv = ConfigSlider(default=30, limits=(0, 30))
			config.lcd.modeminitv.addNotifier(setLCDModeMinitTV)
			config.lcd.fpsminitv.addNotifier(setMiniTVFPS)
		else:
			config.lcd.modeminitv = ConfigNothing()
			config.lcd.screenshot = ConfigNothing()
			config.lcd.fpsminitv = ConfigNothing()

		config.lcd.scroll_speed = ConfigSelection(default = "300", choices = [
			("500", _("slow")),
			("300", _("normal")),
			("100", _("fast"))])
		config.lcd.scroll_delay = ConfigSelection(default = "10000", choices = [
			("10000", "10 " + _("seconds")),
			("20000", "20 " + _("seconds")),
			("30000", "30 " + _("seconds")),
			("60000", "1 " + _("minute")),
			("300000", "5 " + _("minutes")),
			("noscrolling", _("off"))])

		def setLCDbright(configElement):
			ilcd.setBright(configElement.value)

		def setLCDcontrast(configElement):
			ilcd.setContrast(configElement.value)

		def setLCDinverted(configElement):
			ilcd.setInverted(configElement.value)

		def setLCDflipped(configElement):
			ilcd.setFlipped(configElement.value)

		def setLCDmode(configElement):
			ilcd.setMode(configElement.value)

		def setLCDpower(configElement):
			ilcd.setPower(configElement.value);

		def setfblcddisplay(configElement):
			ilcd.setfblcddisplay(configElement.value);

		def setLCDrepeat(configElement):
			ilcd.setRepeat(configElement.value)

		def setLCDscrollspeed(configElement):
			ilcd.setScrollspeed(configElement.value)

		def setLEDnormalstate(configElement):
			ilcd.setLEDNormalState(configElement.value)

		def setLEDdeepstandby(configElement):
			ilcd.setLEDDeepStandbyState(configElement.value)

		def setLEDblinkingtime(configElement):
			ilcd.setLEDBlinkingTime(configElement.value)

		def setPowerLEDstanbystate(configElement):
			if fileExists("/proc/stb/power/standbyled"):
				f = open("/proc/stb/power/standbyled", "w")
				f.write(configElement.value)
				f.close()

		def setDateOnStandby(configElement):
			pass

		def setDateFormat(configElement):
			pass

		from datetime import datetime
		ntime=datetime.now()
		# 8 digit
		if getBoxType() in ('formuler1', 'osminiplus'):
			config.usage.lcd_dateformat = ConfigSelection(default="%H:%M", choices = [
				("OFF","Off"),
				("%H:%M",str(ntime.strftime(_("%H:%M")))),
				("A%H:%M %d/%m",str(ntime.strftime(_("%H:%M <A> %d/%m")))),
				("A%H:%M %d/%m/%y",str(ntime.strftime(_("%H:%M <A> %d/%m/%y")))),
				("A%H:%M %d %b",str(ntime.strftime(_("%H:%M <A> %d %b")))),
				("A%H:%M %a %d",str(ntime.strftime(_("%H:%M <A> %a %d"))))])
			config.usage.lcd_dateformat.addNotifier(setDateFormat)
		#12 digit
		elif getBoxType() in ('vusolo2', 'osmega'):
			config.usage.lcd_dateformat = ConfigSelection(default="%H:%M %d/%m", choices = [
				("OFF","Off"),
				("%H:%M",str(ntime.strftime(_("%H:%M")))),
				("%H:%M %d/%m",str(ntime.strftime(_("%H:%M %d/%m")))),
				("%H:%M %d %b",str(ntime.strftime(_("%H:%M %d %b")))),
				("%H:%M %a %d",str(ntime.strftime(_("%H:%M %a %d")))),
				("A%H:%M %d/%m",str(ntime.strftime(_("%H:%M <A> %d/%m")))),
				("A%H:%M %d/%m/%y",str(ntime.strftime(_("%H:%M <A> %d/%m/%y")))),
				("A%H:%M %d/%m/%Y",str(ntime.strftime(_("%H:%M <A> %d/%m/%Y")))), 
				("A%H:%M %d %b",str(ntime.strftime(_("%H:%M <A> %d %b")))),
				("A%H:%M %d %b %y",str(ntime.strftime(_("%H:%M <A> %d %b %y")))),
				("A%H:%M %a %d",str(ntime.strftime(_("%H:%M <A> %a %d")))),
				("A%H:%M %a %d/%m",str(ntime.strftime(_("%H:%M <A> %a %d/%m")))),
				("A%H:%M %a %d/%m/%y",str(ntime.strftime(_("%H:%M <A> %a %d/%m/%y"))))])
			config.usage.lcd_dateformat.addNotifier(setDateFormat)
		#16 digit
		elif getBoxType() in ('sf3038', 'sf4008', 'mutant51'):
			config.usage.lcd_dateformat = ConfigSelection(default="%H:%M %d/%m/%Y", choices = [
				("OFF","Off"),
				("%H:%M",str(ntime.strftime(_("%H:%M")))),
				("%H:%M %d/%m",str(ntime.strftime(_("%H:%M %d/%m")))),
				("%H:%M %d/%m/%y",str(ntime.strftime(_("%H:%M %d/%m/%y")))),
				("%H:%M %d/%m/%Y",str(ntime.strftime(_("%H:%M %d/%m/%Y")))), 
				("%H:%M %d %b",str(ntime.strftime(_("%H:%M %d %b")))),
				("%H:%M %d %b %y",str(ntime.strftime(_("%H:%M %d %b %y")))),
				("%H:%M %a %d",str(ntime.strftime(_("%H:%M %a %d")))),
				("%H:%M %a %d/%m",str(ntime.strftime(_("%H:%M %a %d/%m")))),
				("A%H:%M %d/%m",str(ntime.strftime(_("%H:%M <A> %d/%m")))),
				("A%H:%M %d/%m/%y",str(ntime.strftime(_("%H:%M <A> %d/%m/%y")))),
				("A%H:%M %d/%m/%Y",str(ntime.strftime(_("%H:%M <A> %d/%m/%Y")))), 
				("A%H:%M %d %b",str(ntime.strftime(_("%H:%M <A> %d %b")))),
				("A%H:%M %d %b %y",str(ntime.strftime(_("%H:%M <A> %d %b %y")))),
				("A%H:%M %a %d",str(ntime.strftime(_("%H:%M <A> %a %d")))),
				("A%H:%M %a %d/%m",str(ntime.strftime(_("%H:%M <A> %a %d/%m")))),
				("A%H:%M %a %d/%m/%y",str(ntime.strftime(_("%H:%M <A> %a %d/%m/%y")))),
				("A%H:%M %a %d/%m/%Y",str(ntime.strftime(_("%H:%M <A> %a %d/%m/%Y"))))])
			config.usage.lcd_dateformat.addNotifier(setDateFormat)
		else:
			config.usage.lcd_dateformat = ConfigNothing()
		
		config.usage.lcd_standbypowerled = ConfigSelection(default = "on", choices = [("off", _("Off")), ("on", _("On"))])
		config.usage.lcd_standbypowerled.addNotifier(setPowerLEDstanbystate)

		standby_default = 0

		if not ilcd.isOled():
			config.lcd.contrast = ConfigSlider(default=5, limits=(0, 20))
			config.lcd.contrast.addNotifier(setLCDcontrast)
		else:
			config.lcd.contrast = ConfigNothing()
			standby_default = 1

		if getBoxType() in ('mixosf5', 'mixosf5mini', 'gi9196m', 'gi9196lite', 'marvel1', 'enfinity', 'zgemmass', 'zgemmas2s', 'zgemmash1', 'zgemmash2', 'spycat'):
			config.lcd.standby = ConfigSlider(default=standby_default, limits=(0, 4))
			config.lcd.bright = ConfigSlider(default=4, limits=(0, 4))
		elif getBoxType() in ('zgemmahs', 'zgemmah2s', 'zgemmah2h', 'zgemmaslc'):
			config.lcd.standby = ConfigSlider(default=2, limits=(0, 8))
			config.lcd.bright = ConfigSlider(default=5, limits=(0, 8))
		else:
			config.lcd.standby = ConfigSlider(default=standby_default, limits=(0, 10))
			config.lcd.bright = ConfigSlider(default=5, limits=(0, 10))
		config.lcd.standby.addNotifier(setLCDbright)
		config.lcd.standby.apply = lambda : setLCDbright(config.lcd.standby)
		config.lcd.bright.addNotifier(setLCDbright)
		config.lcd.bright.apply = lambda : setLCDbright(config.lcd.bright)
		config.lcd.bright.callNotifiersOnSaveAndCancel = True

		config.lcd.invert = ConfigYesNo(default=False)
		config.lcd.invert.addNotifier(setLCDinverted)

		config.lcd.flip = ConfigYesNo(default=False)
		config.lcd.flip.addNotifier(setLCDflipped)

		if getBoxType() in ('mixosf5', 'mixosf5mini', 'gi9196m', 'gi9196lite'):
			config.lcd.scrollspeed = ConfigSlider(default = 150, increment = 10, limits = (0, 500))
			config.lcd.scrollspeed.addNotifier(setLCDscrollspeed);
			config.lcd.repeat = ConfigSelection([("0", _("None")), ("1", _("1X")), ("2", _("2X")), ("3", _("3X")), ("4", _("4X")), ("500", _("Continues"))], "3")
			config.lcd.repeat.addNotifier(setLCDrepeat);
			config.lcd.mode = ConfigNothing()
		elif fileExists("/proc/stb/lcd/scroll_delay") and getBoxType() not in ('ixussone', 'ixusszero', 'axodin', 'axodinc', 'marvel1', 'enfinity', 'vusolose', 'vuzero', 'zgemmass', 'zgemmas2s', 'zgemmash1', 'zgemmash2', 'zgemmahs', 'zgemmah2s', 'zgemmah2h'):
			config.lcd.scrollspeed = ConfigSlider(default = 150, increment = 10, limits = (0, 500))
			config.lcd.scrollspeed.addNotifier(setLCDscrollspeed)
			config.lcd.repeat = ConfigSelection([("0", _("None")), ("1", _("1X")), ("2", _("2X")), ("3", _("3X")), ("4", _("4X")), ("500", _("Continues"))], "3")
			config.lcd.repeat.addNotifier(setLCDrepeat)
			config.lcd.mode = ConfigSelection([("0", _("No")), ("1", _("Yes"))], "1")
			config.lcd.mode.addNotifier(setLCDmode)
		else:
			config.lcd.mode = ConfigNothing()
			config.lcd.repeat = ConfigNothing()
			config.lcd.scrollspeed = ConfigNothing()

		if fileExists("/proc/stb/power/vfd") or fileExists("/proc/stb/lcd/vfd"):
			config.lcd.power = ConfigSelection([("0", _("Off")), ("1", _("On"))], "1")
			config.lcd.power.addNotifier(setLCDpower);
		else:
			config.lcd.power = ConfigNothing()

		if fileExists("/proc/stb/fb/sd_detach"):
			config.lcd.fblcddisplay = ConfigSelection([("1", _("No")), ("0", _("Yes"))], "1")
			config.lcd.fblcddisplay.addNotifier(setfblcddisplay);
		else:
			config.lcd.fblcddisplay = ConfigNothing()

		if getBoxType() == 'vuultimo':
			config.lcd.ledblinkingtime = ConfigSlider(default = 5, increment = 1, limits = (0,15))
			config.lcd.ledblinkingtime.addNotifier(setLEDblinkingtime)
			config.lcd.ledbrightnessdeepstandby = ConfigSlider(default = 1, increment = 1, limits = (0,15))
			config.lcd.ledbrightnessdeepstandby.addNotifier(setLEDnormalstate)
			config.lcd.ledbrightnessdeepstandby.addNotifier(setLEDdeepstandby)
			config.lcd.ledbrightnessdeepstandby.apply = lambda : setLEDdeepstandby(config.lcd.ledbrightnessdeepstandby)
			config.lcd.ledbrightnessstandby = ConfigSlider(default = 1, increment = 1, limits = (0,15))
			config.lcd.ledbrightnessstandby.addNotifier(setLEDnormalstate)
			config.lcd.ledbrightnessstandby.apply = lambda : setLEDnormalstate(config.lcd.ledbrightnessstandby)
			config.lcd.ledbrightness = ConfigSlider(default = 3, increment = 1, limits = (0,15))
			config.lcd.ledbrightness.addNotifier(setLEDnormalstate)
			config.lcd.ledbrightness.apply = lambda : setLEDnormalstate(config.lcd.ledbrightness)
			config.lcd.ledbrightness.callNotifiersOnSaveAndCancel = True
		else:
			def doNothing():
				pass
			config.lcd.ledbrightness = ConfigNothing()
			config.lcd.ledbrightness.apply = lambda : doNothing()
			config.lcd.ledbrightnessstandby = ConfigNothing()
			config.lcd.ledbrightnessstandby.apply = lambda : doNothing()
			config.lcd.ledbrightnessdeepstandby = ConfigNothing()
			config.lcd.ledbrightnessdeepstandby.apply = lambda : doNothing()
			config.lcd.ledblinkingtime = ConfigNothing()
	else:
		def doNothing():
			pass
		config.lcd.contrast = ConfigNothing()
		config.lcd.bright = ConfigNothing()
		config.lcd.standby = ConfigNothing()
		config.lcd.bright.apply = lambda : doNothing()
		config.lcd.standby.apply = lambda : doNothing()
		config.lcd.mode = ConfigNothing()
		config.lcd.power = ConfigNothing()
		config.lcd.fblcddisplay = ConfigNothing()
		config.lcd.repeat = ConfigNothing()
		config.lcd.scrollspeed = ConfigNothing()
		config.lcd.scroll_speed = ConfigSelection(default = "300", choices = [
		("500", _("slow")),
		("300", _("normal")),
		("100", _("fast"))])
		config.lcd.scroll_delay = ConfigSelection(default = "10000", choices = [
		("10000", "10 " + _("seconds")),
		("20000", "20 " + _("seconds")),
		("30000", "30 " + _("seconds")),
		("60000", "1 " + _("minute")),
		("300000", "5 " + _("minutes")),
		("noscrolling", _("off"))])
		config.lcd.ledbrightness = ConfigNothing()
		config.lcd.ledbrightness.apply = lambda : doNothing()
		config.lcd.ledbrightnessstandby = ConfigNothing()
		config.lcd.ledbrightnessstandby.apply = lambda : doNothing()
		config.lcd.ledbrightnessdeepstandby = ConfigNothing()
		config.lcd.ledbrightnessdeepstandby.apply = lambda : doNothing()
		config.lcd.ledblinkingtime = ConfigNothing()

	config.misc.standbyCounter.addNotifier(standbyCounterChanged, initial_call = False)
