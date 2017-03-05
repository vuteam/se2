from enigma import eDVBResourceManager, Misc_Options
from Tools.Directories import fileExists, fileCheck
from Tools.HardwareInfo import HardwareInfo
from os import path
from boxbranding import getBoxType, getMachineBuild

SystemInfo = { }

#FIXMEE...
def getNumVideoDecoders():
	idx = 0
	while fileExists("/dev/dvb/adapter0/video%d"%(idx), 'f'):
		idx += 1
	return idx

SystemInfo["NumVideoDecoders"] = getNumVideoDecoders()
SystemInfo["PIPAvailable"] = SystemInfo["NumVideoDecoders"] > 1
SystemInfo["CanMeasureFrontendInputPower"] = eDVBResourceManager.getInstance().canMeasureFrontendInputPower()


def countFrontpanelLEDs():
	leds = 0
	if fileExists("/proc/stb/fp/led_set_pattern"):
		leds += 1

	while fileExists("/proc/stb/fp/led%d_pattern" % leds):
		leds += 1

	return leds

SystemInfo["HasTuners"] = fileCheck("/dev/dvb/adapter0/frontend0") and fileCheck("/proc/bus/nim_sockets")
SystemInfo["12V_Output"] = Misc_Options.getInstance().detected_12V_output()
SystemInfo["ZapMode"] = fileCheck("/proc/stb/video/zapmode") or fileCheck("/proc/stb/video/zapping_mode")
SystemInfo["NumFrontpanelLEDs"] = countFrontpanelLEDs()
SystemInfo["FrontpanelDisplay"] = fileExists("/dev/dbox/oled0") or fileExists("/dev/dbox/lcd0")
SystemInfo["FPDisplay"] = SystemInfo["FrontpanelDisplay"] and getMachineBuild() not in ('spark7162', 'vuultimo')
SystemInfo["FrontpanelDisplayGrayscale"] = fileExists("/dev/dbox/oled0")
SystemInfo["LCDsymbol_circle"] = fileCheck("/proc/stb/lcd/symbol_circle")
SystemInfo["FBLCDDisplay"] = fileCheck("/proc/stb/fb/sd_detach")
SystemInfo["DeepstandbySupport"] = HardwareInfo().has_deepstandby()
SystemInfo["Fan"] = fileCheck("/proc/stb/fp/fan")
SystemInfo["FanPWM"] = SystemInfo["Fan"] and fileCheck("/proc/stb/fp/fan_pwm")
SystemInfo["StandbyPowerLed"] = fileExists("/proc/stb/power/standbyled")
SystemInfo["LEDButtons"] = getBoxType() == 'vuultimo'
SystemInfo["GraphicLCD"] = getBoxType() in ('vuultimo', 'xpeedlx3', 'et10000', 'mutant2400', 'quadbox2400', 'sezammarvel', 'atemionemesis', 'mbultra', 'beyonwizt4')
SystemInfo["WakeOnLAN"] = fileCheck("/proc/stb/power/wol") or fileCheck("/proc/stb/fp/wol")
SystemInfo["HDMICEC"] = (fileExists("/dev/hdmi_cec") or fileExists("/dev/misc/hdmi_cec0")) and fileExists("/usr/lib/enigma2/python/Plugins/SystemPlugins/HdmiCEC/plugin.pyo")
SystemInfo["Satfinder"] = fileExists("/usr/lib/enigma2/python/Plugins/SystemPlugins/Satfinder/plugin.pyo")
SystemInfo["GBWOL"] = fileExists("/usr/bin/gigablue_wol")
SystemInfo["HasExternalPIP"] = getMachineBuild() not in ('et9x00', 'et6x00', 'et5x00') and fileCheck("/proc/stb/vmpeg/1/external")
SystemInfo["VideoDestinationConfigurable"] = fileExists("/proc/stb/vmpeg/0/dst_left")
SystemInfo["hasPIPVisibleProc"] = fileCheck("/proc/stb/vmpeg/1/visible")
SystemInfo["LCDSKINSetup"] = path.exists("/usr/share/enigma2/display") and getBoxType() in ('et8500', 'et10000', 'gb800ue', 'gb800ueplus', 'gbquad', 'gbquadplus', 'gbultraue', 'vuduo2', 'sf208', 'sf228') and not fileExists("/etc/enigma2/skin_user.xml")
SystemInfo["3DMode"] = fileCheck("/proc/stb/fb/3dmode") or fileCheck("/proc/stb/fb/primary/3d")
SystemInfo["3DZNorm"] = fileCheck("/proc/stb/fb/znorm") or fileCheck("/proc/stb/fb/primary/zoffset")
SystemInfo["IPV6"] = fileCheck("/proc/sys/net/ipv6/conf/all/disable_ipv6")
SystemInfo["Blindscan_t2_available"] = fileCheck("/proc/stb/info/vumodel")
SystemInfo["HasForceLNBOn"] = fileCheck("/proc/stb/frontend/fbc/force_lnbon")
SystemInfo["HasForceToneburst"] = fileCheck("/proc/stb/frontend/fbc/force_toneburst")
SystemInfo["HaveMultiBoot"] = fileCheck("/boot/STARTUP") or fileCheck("/boot/STARTUP_1")
SystemInfo["CanDoTranscodeAndPIP"] = getBoxType() in ('vusolo4k')
