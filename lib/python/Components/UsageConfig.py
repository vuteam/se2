from Components.Harddisk import harddiskmanager
from config import ConfigSubsection, ConfigYesNo, config, ConfigSelection, ConfigText, ConfigNumber, ConfigSet, ConfigLocations, ConfigSelectionNumber, ConfigInteger, ConfigPassword, ConfigIP, ConfigClock, ConfigSlider, NoSave, ConfigEnableDisable, ConfigSubDict, ConfigNothing
from Tools.Directories import resolveFilename, SCOPE_HDD, defaultRecordingLocation
from enigma import setTunerTypePriorityOrder, setPreferredTuner, setSpinnerOnOff, setEnableTtCachingOnOff, eEnv, eDVBDB, Misc_Options, eBackgroundFileEraser, eServiceEvent
from Components.NimManager import nimmanager
from Components.Harddisk import harddiskmanager
from Components.ServiceList import refreshServiceList
from SystemInfo import SystemInfo
from boxbranding import getBoxType
import os
import time

def InitUsageConfig():
	config.misc.useNTPminutes = ConfigSelection(default = "30", choices = [("30", "30" + " " +_("minutes")), ("60", _("Hour")), ("1440", _("Once per day"))])
	config.usage = ConfigSubsection()
	config.usage.showdish = ConfigYesNo(default = True)
	config.misc.showrotorposition = ConfigSelection(default = "no", choices = [("no", _("no")), ("yes", _("yes")), ("withtext", _("with text")), ("tunername", _("with tuner name"))])
	config.usage.multibouquet = ConfigYesNo(default = True)

	config.usage.alternative_number_mode = ConfigYesNo(default = False)
	def alternativeNumberModeChange(configElement):
		eDVBDB.getInstance().setNumberingMode(configElement.value)
		refreshServiceList()
	config.usage.alternative_number_mode.addNotifier(alternativeNumberModeChange)

	config.usage.hide_number_markers = ConfigYesNo(default = True)
	config.usage.hide_number_markers.addNotifier(refreshServiceList)

	config.usage.crypto_icon_mode = ConfigSelection(default = "0", choices = [("0", _("None")), ("1", _("Left from servicename")), ("2", _("Right from servicename"))])
	config.usage.crypto_icon_mode.addNotifier(refreshServiceList)

	config.usage.servicetype_icon_mode = ConfigSelection(default = "0", choices = [("0", _("None")), ("1", _("Left from servicename")), ("2", _("Right from servicename"))])  
	config.usage.servicetype_icon_mode.addNotifier(refreshServiceList)
	config.usage.record_indicator_mode = ConfigSelection(default = "0", choices = [("0", _("None")), ("1", _("Left from servicename")), ("2", _("Right from servicename")), ("3", _("Red colored"))])
	config.usage.record_indicator_mode.addNotifier(refreshServiceList)

	choicelist = [("-1", _("Disable"))]
	for i in range(0,1300,100):
		choicelist.append((str(i), ngettext("%d pixel wide", "%d pixels wide", i) % i))
	config.usage.servicelist_column = ConfigSelection(default="-1", choices=choicelist)
	config.usage.servicelist_column.addNotifier(refreshServiceList)

	config.usage.service_icon_enable = ConfigYesNo(default = False)
	config.usage.service_icon_enable.addNotifier(refreshServiceList)

	config.usage.servicelist_cursor_behavior = ConfigSelection(default = "standard", choices = [
		("standard", _("Standard")),
		("keep", _("Keep service")),
		("reverseB", _("Reverse bouquet buttons")),
		("keep reverseB", _("Keep service") + " + " + _("Reverse bouquet buttons"))])

	config.usage.multiepg_ask_bouquet = ConfigYesNo(default = False)

	config.usage.quickzap_bouquet_change = ConfigYesNo(default = False)
	config.usage.e1like_radio_mode = ConfigYesNo(default = True)

	config.usage.volume_step_slow = ConfigSelectionNumber(default = 1, stepwidth = 1, min = 1, max = 10, wraparound = False)
	config.usage.volume_step_fast = ConfigSelectionNumber(default = 3, stepwidth = 1, min = 1, max = 10, wraparound = False)

	choicelist = [("0", _("No timeout"))]
	for i in range(1, 12):
		choicelist.append((str(i), ngettext("%d second", "%d seconds", i) % i))
	config.usage.infobar_timeout = ConfigSelection(default = "5", choices = choicelist)
	config.usage.show_infobar_do_dimming = ConfigYesNo(default = False)
	config.usage.show_infobar_dimming_speed = ConfigSelectionNumber(min = 1, max = 40, stepwidth = 1, default = 40, wraparound = True)
	config.usage.show_infobar_on_zap = ConfigYesNo(default = True)
	config.usage.show_infobar_on_skip = ConfigYesNo(default = True)
	config.usage.show_infobar_on_event_change = ConfigYesNo(default = False)
	config.usage.show_second_infobar = ConfigSelection(default = "11", choices = [(None, _("None"))] + choicelist + [("EPG",_("EPG"))])
	config.usage.infobar_frontend_source = ConfigSelection(default = "tuner", choices = [("settings", _("Settings")), ("tuner", _("Tuner"))])
	config.usage.oldstyle_zap_controls = ConfigSelection(default = "standard", choices = [
		("standard", _("Standard")),
		("neutrino", _("Neutrino")),
		("openspa", _("OpenSPA")) ])
	config.usage.oldstyle_channel_select_controls =  ConfigYesNo(default = False)
	config.usage.zap_with_ch_buttons = ConfigYesNo(default = False)
	config.usage.ok_is_channelselection = ConfigYesNo(default = False)
	config.usage.channelselection_preview = ConfigYesNo(default = False)
	config.usage.show_spinner = ConfigYesNo(default = True)
	config.usage.enable_tt_caching = ConfigYesNo(default = True)

	config.usage.tuxtxt_font_and_res = ConfigSelection(default = "TTF_SD", choices = [("X11_SD", _("Fixed X11 font (SD)")), ("TTF_SD", _("TrueType font (SD)")), ("TTF_HD", _("TrueType font (HD)")), ("TTF_FHD", _("TrueType font (full-HD)")), ("expert_mode", _("Expert mode"))])
	config.usage.tuxtxt_UseTTF = ConfigSelection(default = "1", choices = [("0", "0"), ("1", "1")])
	config.usage.tuxtxt_TTFBold = ConfigSelection(default = "1", choices = [("0", "0"), ("1", "1")])
	config.usage.tuxtxt_TTFScreenResX = ConfigSelection(default = "720", choices = [("720", "720"), ("1280", "1280"), ("1920", "1920")])
	config.usage.tuxtxt_StartX = ConfigInteger(default=50, limits = (0, 200))
	config.usage.tuxtxt_EndX = ConfigInteger(default=670, limits = (500, 1920))
	config.usage.tuxtxt_StartY = ConfigInteger(default=30, limits = (0, 200))
	config.usage.tuxtxt_EndY = ConfigInteger(default=555, limits = (400, 1080))
	config.usage.tuxtxt_TTFShiftY = ConfigSelection(default = "2", choices = [("-9", "-9"), ("-8", "-8"), ("-7", "-7"), ("-6", "-6"), ("-5", "-5"), ("-4", "-4"), ("-3", "-3"), ("-2", "-2"), ("-1", "-1"), ("0", "0"), ("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5"), ("6", "6"), ("7", "7"), ("8", "8"), ("9", "9")])
	config.usage.tuxtxt_TTFShiftX = ConfigSelection(default = "0", choices = [("-9", "-9"), ("-8", "-8"), ("-7", "-7"), ("-6", "-6"), ("-5", "-5"), ("-4", "-4"), ("-3", "-3"), ("-2", "-2"), ("-1", "-1"), ("0", "0"), ("1", "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5"), ("6", "6"), ("7", "7"), ("8", "8"), ("9", "9")])
	config.usage.tuxtxt_TTFWidthFactor16 = ConfigInteger(default=29, limits = (8, 31))
	config.usage.tuxtxt_TTFHeightFactor16 = ConfigInteger(default=14, limits = (8, 31))
	config.usage.tuxtxt_CleanAlgo = ConfigInteger(default=0, limits = (0, 9))

	config.usage.tuxtxt_ConfFileHasBeenPatched = NoSave(ConfigYesNo(default=False))

	config.usage.tuxtxt_font_and_res.addNotifier(patchTuxtxtConfFile, initial_call = False, immediate_feedback = False, call_on_save_or_cancel = True)
	config.usage.tuxtxt_UseTTF.addNotifier(patchTuxtxtConfFile, initial_call = False, immediate_feedback = False, call_on_save_or_cancel = True)
	config.usage.tuxtxt_TTFBold.addNotifier(patchTuxtxtConfFile, initial_call = False, immediate_feedback = False, call_on_save_or_cancel = True)
	config.usage.tuxtxt_TTFScreenResX.addNotifier(patchTuxtxtConfFile, initial_call = False, immediate_feedback = False, call_on_save_or_cancel = True)
	config.usage.tuxtxt_StartX.addNotifier(patchTuxtxtConfFile, initial_call = False, immediate_feedback = False, call_on_save_or_cancel = True)
	config.usage.tuxtxt_EndX.addNotifier(patchTuxtxtConfFile, initial_call = False, immediate_feedback = False, call_on_save_or_cancel = True)
	config.usage.tuxtxt_StartY.addNotifier(patchTuxtxtConfFile, initial_call = False, immediate_feedback = False, call_on_save_or_cancel = True)
	config.usage.tuxtxt_EndY.addNotifier(patchTuxtxtConfFile, initial_call = False, immediate_feedback = False, call_on_save_or_cancel = True)
	config.usage.tuxtxt_TTFShiftY.addNotifier(patchTuxtxtConfFile, initial_call = False, immediate_feedback = False, call_on_save_or_cancel = True)
	config.usage.tuxtxt_TTFShiftX.addNotifier(patchTuxtxtConfFile, initial_call = False, immediate_feedback = False, call_on_save_or_cancel = True)
	config.usage.tuxtxt_TTFWidthFactor16.addNotifier(patchTuxtxtConfFile, initial_call = False, immediate_feedback = False, call_on_save_or_cancel = True)
	config.usage.tuxtxt_TTFHeightFactor16.addNotifier(patchTuxtxtConfFile, initial_call = False, immediate_feedback = False, call_on_save_or_cancel = True)
	config.usage.tuxtxt_CleanAlgo.addNotifier(patchTuxtxtConfFile, initial_call = False, immediate_feedback = False, call_on_save_or_cancel = True)

	config.usage.sort_settings = ConfigYesNo(default = False)
	config.usage.sort_menus = ConfigYesNo(default = False)
	choicelist = []
	for i in (10, 30):
		choicelist.append((str(i), ngettext("%d second", "%d seconds", i) % i))
	for i in (60, 120, 300, 600, 1200, 1800):
		m = i / 60
		choicelist.append((str(i), ngettext("%d minute", "%d minutes", m) % m))
	for i in (3600, 7200, 14400):
		h = i / 3600
		choicelist.append((str(i), ngettext("%d hour", "%d hours", h) % h))
	config.usage.hdd_standby = ConfigSelection(default = "300", choices = [("0", _("No standby"))] + choicelist)
	config.usage.hdd_standby_in_standby = ConfigSelection(default = "-1", choices = [("-1", _("Same as in active")), ("0", _("No standby"))] + choicelist)
	config.usage.hdd_timer = ConfigYesNo(default = False)
	config.usage.output_12V = ConfigSelection(default = "do not change", choices = [
		("do not change", _("Do not change")), ("off", _("Off")), ("on", _("On")) ])

	config.usage.pip_zero_button = ConfigSelection(default = "standard", choices = [
		("standard", _("Standard")), ("swap", _("Swap PiP and main picture")),
		("swapstop", _("Move PiP to main picture")), ("stop", _("Stop PiP")) ])

	config.usage.pip_hideOnExit = ConfigSelection(default = "without popup", choices = [
		("no", _("No")), ("popup", _("With popup")), ("without popup", _("Without popup")) ])
	choicelist = [("-1", _("Disabled")), ("0", _("No timeout"))]
	for i in [60, 300, 600, 900, 1800, 2700, 3600]:
		m = i/60
		choicelist.append((str(i), ngettext("%d minute", "%d minutes", m) % m))
	config.usage.pip_last_service_timeout = ConfigSelection(default = "0", choices = choicelist)

	config.usage.default_path = ConfigText(default = resolveFilename(SCOPE_HDD))
	config.usage.timer_path = ConfigText(default = "<default>")
	config.usage.instantrec_path = ConfigText(default = "<default>")
	config.usage.timeshift_path = ConfigText(default = "/media/hdd/")
	config.usage.allowed_timeshift_paths = ConfigLocations(default = ["/media/hdd/"])

	config.plisettings = ConfigSubsection()
	config.plisettings.Subservice = ConfigYesNo(default = True)

	config.oscaminfo = ConfigSubsection()
	config.oscaminfo.showInExtensions = ConfigYesNo(default=False)
	config.oscaminfo.userdatafromconf = ConfigYesNo(default = False)
	config.oscaminfo.autoupdate = ConfigYesNo(default = False)
	config.oscaminfo.username = ConfigText(default = "username", fixed_size = False, visible_width=12)
	config.oscaminfo.password = ConfigPassword(default = "password", fixed_size = False)
	config.oscaminfo.ip = ConfigIP( default = [ 127,0,0,1 ], auto_jump=True)
	config.oscaminfo.port = ConfigInteger(default = 16002, limits=(0,65536) )
	config.oscaminfo.intervall = ConfigSelectionNumber(min = 1, max = 600, stepwidth = 1, default = 10, wraparound = True)

	config.cccaminfo = ConfigSubsection()
	config.cccaminfo.showInExtensions = ConfigYesNo(default=False)
	config.cccaminfo.serverNameLength = ConfigSelectionNumber(min = 10, max = 100, stepwidth = 1, default = 22, wraparound = True)
	config.cccaminfo.name = ConfigText(default="Profile", fixed_size=False)
	config.cccaminfo.ip = ConfigText(default="192.168.2.12", fixed_size=False)
	config.cccaminfo.username = ConfigText(default="", fixed_size=False)
	config.cccaminfo.password = ConfigText(default="", fixed_size=False)
	config.cccaminfo.port = ConfigInteger(default=16001, limits=(1, 65535))
	config.cccaminfo.profile = ConfigText(default="", fixed_size=False)
	config.cccaminfo.ecmInfoEnabled = ConfigYesNo(default=True)
	config.cccaminfo.ecmInfoTime = ConfigSelectionNumber(min = 1, max = 10, stepwidth = 1, default = 5, wraparound = True)
	config.cccaminfo.ecmInfoForceHide = ConfigYesNo(default=True)
	config.cccaminfo.ecmInfoPositionX = ConfigInteger(default=50)
	config.cccaminfo.ecmInfoPositionY = ConfigInteger(default=50)
	config.cccaminfo.blacklist = ConfigText(default="/media/cf/CCcamInfo.blacklisted", fixed_size=False)
	config.cccaminfo.profiles = ConfigText(default="/media/cf/CCcamInfo.profiles", fixed_size=False)

	config.usage.movielist_trashcan = ConfigYesNo(default=True)
	config.usage.movielist_trashcan_days = ConfigNumber(default=8)
	config.usage.movielist_trashcan_reserve = ConfigNumber(default=40)
	config.usage.on_movie_start = ConfigSelection(default = "resume", choices = [
		("ask yes", _("Ask user") + " " + _("default") + " " + _("yes")),
		("ask no", _("Ask user") + " " + _("default") + " " + _("no")),
		("resume", _("Resume from last position")),
		("beginning", _("Start from the beginning"))])
	config.usage.on_movie_stop = ConfigSelection(default = "movielist", choices = [
		("ask", _("Ask user")), ("movielist", _("Return to movie list")), ("quit", _("Return to previous service")) ])
	config.usage.on_movie_eof = ConfigSelection(default = "movielist", choices = [
		("ask", _("Ask user")), ("movielist", _("Return to movie list")), ("quit", _("Return to previous service")), ("pause", _("Pause movie at end")), ("playlist", _("Play next (return to movie list)")),
		("playlistquit", _("Play next (return to previous service)")), ("loop", _("Continues play (loop)")), ("repeatcurrent", _("Repeat"))])
	config.usage.next_movie_msg = ConfigYesNo(default = True)
	config.usage.last_movie_played = ConfigText()
	config.usage.leave_movieplayer_onExit = ConfigSelection(default = "popup", choices = [
		("no", _("No")), ("popup", _("With popup")), ("without popup", _("Without popup")), ("movielist", _("Return to movie list")) ])

	config.usage.setup_level = ConfigSelection(default = "expert", choices = [
		("simple", _("Simple")),
		("intermediate", _("Intermediate")),
		("expert", _("Expert")) ])

	config.usage.startup_to_standby = ConfigSelection(default = "no", choices = [
		("no", _("No")),
		("yes", _("Yes")),
		("except", _("No, except Wakeup timer")) ])

	config.usage.wakeup_enabled = ConfigSelection(default = "no", choices = [
		("no", _("No")),
		("yes", _("Yes")),
		("standby", _("Yes, only from standby")),
		("deepstandby", _("Yes, only from deep standby")) ])
	config.usage.wakeup_day = ConfigSubDict()
	config.usage.wakeup_time = ConfigSubDict()
	for i in range(7):
		config.usage.wakeup_day[i] = ConfigEnableDisable(default = False)
		config.usage.wakeup_time[i] = ConfigClock(default = ((6 * 60 + 0) * 60))

	config.usage.on_long_powerpress = ConfigSelection(default = "show_menu", choices = [
		("show_menu", _("Show shutdown menu")),
		("shutdown", _("Immediate shutdown")),
		("standby", _("Standby")),
		("restart", _("Reboot")) ] )

	config.usage.on_short_powerpress = ConfigSelection(default = "standby", choices = [
		("show_menu", _("Show shutdown menu")),
		("shutdown", _("Immediate shutdown")),
		("standby", _("Standby")) ] )

	choicelist = [("0", _("Do nothing"))]
	for i in range(3600, 21601, 3600):
		h = abs(i / 3600)
		h = ngettext("%d hour", "%d hours", h) % h
		choicelist.append((str(i), _("Standby in ") + h))
	config.usage.inactivity_timer = ConfigSelection(default = "0", choices = choicelist)
	config.usage.inactivity_timer_blocktime = ConfigYesNo(default = True)
	config.usage.inactivity_timer_blocktime_begin = ConfigClock(default = time.mktime((0, 0, 0, 18, 0, 0, 0, 0, 0)))
	config.usage.inactivity_timer_blocktime_end = ConfigClock(default = time.mktime((0, 0, 0, 23, 0, 0, 0, 0, 0)))
	config.usage.inactivity_timer_blocktime_extra = ConfigYesNo(default = False)
	config.usage.inactivity_timer_blocktime_extra_begin = ConfigClock(default = time.mktime((0, 0, 0, 6, 0, 0, 0, 0, 0)))
	config.usage.inactivity_timer_blocktime_extra_end = ConfigClock(default = time.mktime((0, 0, 0, 9, 0, 0, 0, 0, 0)))
	config.usage.inactivity_timer_blocktime_by_weekdays = ConfigYesNo(default = False)
	config.usage.inactivity_timer_blocktime_day = ConfigSubDict()
	config.usage.inactivity_timer_blocktime_begin_day = ConfigSubDict()
	config.usage.inactivity_timer_blocktime_end_day = ConfigSubDict()
	config.usage.inactivity_timer_blocktime_extra_day = ConfigSubDict()
	config.usage.inactivity_timer_blocktime_extra_begin_day = ConfigSubDict()
	config.usage.inactivity_timer_blocktime_extra_end_day = ConfigSubDict()
	for i in range(7):
		config.usage.inactivity_timer_blocktime_day[i] = ConfigYesNo(default = False)
		config.usage.inactivity_timer_blocktime_begin_day[i] = ConfigClock(default = time.mktime((0, 0, 0, 18, 0, 0, 0, 0, 0)))
		config.usage.inactivity_timer_blocktime_end_day[i] = ConfigClock(default = time.mktime((0, 0, 0, 23, 0, 0, 0, 0, 0)))
		config.usage.inactivity_timer_blocktime_extra_day[i] = ConfigYesNo(default = False)
		config.usage.inactivity_timer_blocktime_extra_begin_day[i] = ConfigClock(default = time.mktime((0, 0, 0, 6, 0, 0, 0, 0, 0)))
		config.usage.inactivity_timer_blocktime_extra_end_day[i] = ConfigClock(default = time.mktime((0, 0, 0, 9, 0, 0, 0, 0, 0)))

	choicelist = [("0", _("Disabled")),("event_standby", _("Standby after current event"))]
	for i in range(900, 7201, 900):
		m = abs(i / 60)
		m = ngettext("%d minute", "%d minutes", m) % m
		choicelist.append((str(i), _("Standby in ") + m))
	config.usage.sleep_timer = ConfigSelection(default = "0", choices = choicelist)

	choicelist = [("0", _("Disabled"))]
	for i in [60, 300, 600] + range(900, 7201, 900):
		m = abs(i / 60)
		m = ngettext("%d minute", "%d minutes", m) % m
		choicelist.append((str(i), _("after ") + m))
	config.usage.standby_to_shutdown_timer = ConfigSelection(default = "0", choices = choicelist)
	config.usage.standby_to_shutdown_timer_blocktime = ConfigYesNo(default = False)
	config.usage.standby_to_shutdown_timer_blocktime_begin = ConfigClock(default = time.mktime((0, 0, 0, 6, 0, 0, 0, 0, 0)))
	config.usage.standby_to_shutdown_timer_blocktime_end = ConfigClock(default = time.mktime((0, 0, 0, 23, 0, 0, 0, 0, 0)))

	choicelist = [("0", _("Disabled"))]
	for m in (1, 5, 10, 15, 30, 60):
		choicelist.append((str(m * 60), ngettext("%d minute", "%d minutes", m) % m))
	config.usage.screen_saver = ConfigSelection(default = "300", choices = choicelist)

	config.usage.check_timeshift = ConfigYesNo(default = True)

	choicelist = [("0", _("Disabled"))]
	for i in (2, 3, 4, 5, 10, 20, 30):
		choicelist.append((str(i), ngettext("%d second", "%d seconds", i) % i))
	for i in (60, 120, 300):
		m = i / 60
		choicelist.append((str(i), ngettext("%d minute", "%d minutes", m) % m))
	config.usage.timeshift_start_delay = ConfigSelection(default = "0", choices = choicelist)

	config.usage.alternatives_priority = ConfigSelection(default = "0", choices = [
		("0", "DVB-S/-C/-T"),
		("1", "DVB-S/-T/-C"),
		("2", "DVB-C/-S/-T"),
		("3", "DVB-C/-T/-S"),
		("4", "DVB-T/-C/-S"),
		("5", "DVB-T/-S/-C"),
		("127", _("No priority")) ])

	def remote_fallback_changed(configElement):
		if configElement.value:
			configElement.value = "%s%s" % (not configElement.value.startswith("http://") and "http://" or "", configElement.value)
			configElement.value = "%s%s" % (configElement.value, configElement.value.count(":") == 1 and ":8001" or "")
	config.usage.remote_fallback_enabled = ConfigYesNo(default = False)
	config.usage.remote_fallback = ConfigText(default = _("http://IP-ADDRESS:8001"), fixed_size = False)
	config.usage.remote_fallback.addNotifier(remote_fallback_changed, immediate_feedback=False)

	config.usage.show_timer_conflict_warning = ConfigYesNo(default = True)

	dvbs_nims = [("-2", _("Disabled"))]
	dvbt_nims = [("-2", _("Disabled"))]
	dvbc_nims = [("-2", _("Disabled"))]
	atsc_nims = [("-2", _("Disabled"))]

	nims = [("-1", _("auto"))]
	for x in nimmanager.nim_slots:
		if x.isCompatible("DVB-S"):
			dvbs_nims.append((str(x.slot), x.getSlotName()))
		elif x.isCompatible("DVB-T"):
			dvbt_nims.append((str(x.slot), x.getSlotName()))
		elif x.isCompatible("DVB-C"):
			dvbc_nims.append((str(x.slot), x.getSlotName()))
		elif x.isCompatible("ATSC"):
			atsc_nims.append((str(x.slot), x.getSlotName()))
		nims.append((str(x.slot), x.getSlotName()))

	config.usage.frontend_priority = ConfigSelection(default = "-1", choices = list(nims))
	nims.insert(0,("-2", _("Disabled")))
	config.usage.recording_frontend_priority = ConfigSelection(default = "-2", choices = nims)
	config.usage.frontend_priority_dvbs = ConfigSelection(default = "-2", choices = list(dvbs_nims))
	dvbs_nims.insert(1,("-1", _("auto")))
	config.usage.recording_frontend_priority_dvbs = ConfigSelection(default = "-2", choices = dvbs_nims)
	config.usage.frontend_priority_dvbt = ConfigSelection(default = "-2", choices = list(dvbt_nims))
	dvbt_nims.insert(1,("-1", _("auto")))
	config.usage.recording_frontend_priority_dvbt = ConfigSelection(default = "-2", choices = dvbt_nims)
	config.usage.frontend_priority_dvbc = ConfigSelection(default = "-2", choices = list(dvbc_nims))
	dvbc_nims.insert(1,("-1", _("auto")))
	config.usage.recording_frontend_priority_dvbc = ConfigSelection(default = "-2", choices = dvbc_nims)
	config.usage.frontend_priority_atsc = ConfigSelection(default = "-2", choices = list(atsc_nims))
	atsc_nims.insert(1,("-1", _("auto")))
	config.usage.recording_frontend_priority_atsc = ConfigSelection(default = "-2", choices = atsc_nims)

	SystemInfo["DVB-S_priority_tuner_available"] = len(dvbs_nims) > 3 and any(len(i) > 2 for i in (dvbt_nims, dvbc_nims, atsc_nims))
	SystemInfo["DVB-T_priority_tuner_available"] = len(dvbt_nims) > 3 and any(len(i) > 2 for i in (dvbs_nims, dvbc_nims, atsc_nims))
	SystemInfo["DVB-C_priority_tuner_available"] = len(dvbc_nims) > 3 and any(len(i) > 2 for i in (dvbs_nims, dvbt_nims, atsc_nims))
	SystemInfo["ATSC_priority_tuner_available"] = len(atsc_nims) > 3 and any(len(i) > 2 for i in (dvbs_nims, dvbc_nims, dvbt_nims))
 
	config.misc.disable_background_scan = ConfigYesNo(default = False)

	config.usage.servicenum_fontsize = ConfigSelectionNumber(default = 0, stepwidth = 1, min = -8, max = 10, wraparound = True)
	config.usage.servicename_fontsize = ConfigSelectionNumber(default = 0, stepwidth = 1, min = -8, max = 10, wraparound = True)
	config.usage.serviceinfo_fontsize = ConfigSelectionNumber(default = 0, stepwidth = 1, min = -8, max = 10, wraparound = True)
	config.usage.serviceitems_per_page = ConfigSelectionNumber(default = 14, stepwidth = 1, min = 8, max = 20, wraparound = True)

	config.usage.show_event_progress_in_servicelist = ConfigSelection(default = 'barright', choices = [
		('barleft', _("Progress bar left")),
		('barright', _("Progress bar right")),
		('percleft', _("Percentage left")),
		('percright', _("Percentage right")),
		('no', _("No")) ])
	config.usage.show_channel_numbers_in_servicelist = ConfigYesNo(default = True)
	config.usage.show_event_progress_in_servicelist.addNotifier(refreshServiceList)
	config.usage.show_channel_numbers_in_servicelist.addNotifier(refreshServiceList)

	config.usage.blinking_display_clock_during_recording = ConfigYesNo(default = False)

	config.usage.blinking_rec_symbol_during_recording = ConfigYesNo(default = False)

	config.usage.show_message_when_recording_starts = ConfigYesNo(default = True)

	config.usage.load_length_of_movies_in_moviellist = ConfigYesNo(default = True)
	config.usage.show_icons_in_movielist = ConfigSelection(default = 'i', choices = [
		('o', _("Off")),
		('p', _("Progress")),
		('s', _("Small progress")),
		('i', _("Icons")),
	])
	config.usage.movielist_unseen = ConfigYesNo(default = False)

	config.usage.swap_snr_on_osd = ConfigYesNo(default = False)

	config.usage.swap_time_display_on_osd = ConfigSelection(default = "0", choices = [("0", _("Skin Setting")), ("1", _("Mins")), ("2", _("Mins Secs")), ("3", _("Hours Mins")), ("4", _("Hours Mins Secs")), ("5", _("Percentage"))])
	config.usage.swap_media_time_display_on_osd = ConfigSelection(default = "0", choices = [("0", _("Skin Setting")), ("1", _("Mins")), ("2", _("Mins Secs")), ("3", _("Hours Mins")), ("4", _("Hours Mins Secs")), ("5", _("Percentage"))])
	config.usage.swap_time_remaining_on_osd = ConfigSelection(default = "0", choices = [("0", _("Remaining")), ("1", _("Elapsed")), ("2", _("Elapsed & Remaining")), ("3", _("Remaining & Elapsed"))])
	config.usage.elapsed_time_positive_osd = ConfigYesNo(default = False)
	config.usage.swap_time_display_on_vfd = ConfigSelection(default = "0", choices = [("0", _("Skin Setting")), ("1", _("Mins")), ("2", _("Mins Secs")), ("3", _("Hours Mins")), ("4", _("Hours Mins Secs")), ("5", _("Percentage"))])
	config.usage.swap_media_time_display_on_vfd = ConfigSelection(default = "0", choices = [("0", _("Skin Setting")), ("1", _("Mins")), ("2", _("Mins Secs")), ("3", _("Hours Mins")), ("4", _("Hours Mins Secs")), ("5", _("Percentage"))])
	config.usage.swap_time_remaining_on_vfd = ConfigSelection(default = "0", choices = [("0", _("Remaining")), ("1", _("Elapsed")), ("2", _("Elapsed & Remaining")), ("3", _("Remaining & Elapsed"))])
	config.usage.elapsed_time_positive_vfd = ConfigYesNo(default = False)
	config.usage.lcd_scroll_delay = ConfigSelection(default = "10000", choices = [
		("10000", "10 " + _("seconds")),
		("20000", "20 " + _("seconds")),
		("30000", "30 " + _("seconds")),
		("60000", "1 " + _("minute")),
		("300000", "5 " + _("minutes")),
		("noscrolling", _("off"))])
	config.usage.lcd_scroll_speed = ConfigSelection(default = "300", choices = [
		("500", _("slow")),
		("300", _("normal")),
		("100", _("fast"))])

	config.usage.maxchannelnumlen = ConfigSelection(default = "5", choices = [("4", _("4")), ("5", _("5"))])
	config.usage.numzaptimeoutmode = ConfigSelection(default = "standard", choices = [("standard", _("Standard")), ("userdefined", _("User defined")), ("off", _("off"))])
	config.usage.numzaptimeout1 = ConfigSlider(default = 3000, increment = 250, limits = (750, 5000))
	config.usage.numzaptimeout2 = ConfigSlider(default = 1000, increment = 250, limits = (750, 5000))

	def SpinnerOnOffChanged(configElement):
		setSpinnerOnOff(int(configElement.value))
	config.usage.show_spinner.addNotifier(SpinnerOnOffChanged)

	def EnableTtCachingChanged(configElement):
		setEnableTtCachingOnOff(int(configElement.value))
	config.usage.enable_tt_caching.addNotifier(EnableTtCachingChanged)

	def TunerTypePriorityOrderChanged(configElement):
		setTunerTypePriorityOrder(int(configElement.value))
	config.usage.alternatives_priority.addNotifier(TunerTypePriorityOrderChanged, immediate_feedback=False)

	def PreferredTunerChanged(configElement):
		setPreferredTuner(int(configElement.value))
	config.usage.frontend_priority.addNotifier(PreferredTunerChanged)

	config.usage.hide_zap_errors = ConfigYesNo(default = False)
	config.usage.hide_ci_messages = ConfigYesNo(default = True)
	config.usage.show_cryptoinfo = ConfigYesNo(default = True)
	config.usage.show_eit_nownext = ConfigYesNo(default = True)
	config.usage.show_vcr_scart = ConfigYesNo(default = False)
	config.usage.show_update_disclaimer = ConfigYesNo(default = True)
	config.usage.pic_resolution = ConfigSelection(default = None, choices = [(None, _("Same resolution as skin")), ("(720, 576)","720x576"), ("(1280, 720)", "1280x720"), ("(1920, 1080)", "1920x1080")])

	if SystemInfo["Fan"]:
		choicelist = [('off', _("Off")), ('on', _("On")), ('auto', _("Auto"))]
		if os.path.exists("/proc/stb/fp/fan_choices"):
			choicelist = [x for x in choicelist if x[0] in open("/proc/stb/fp/fan_choices", "r").read().strip().split(" ")]
		config.usage.fan = ConfigSelection(choicelist)
		def fanChanged(configElement):
			open(SystemInfo["Fan"], "w").write(configElement.value)
		config.usage.fan.addNotifier(fanChanged)

	if SystemInfo["FanPWM"]:
		def fanSpeedChanged(configElement):
			open(SystemInfo["FanPWM"], "w").write(hex(configElement.value)[2:])
		config.usage.fanspeed = ConfigSlider(default=127, increment=8, limits=(0, 255))
		config.usage.fanspeed.addNotifier(fanSpeedChanged)

	config.epg = ConfigSubsection()
	config.epg.eit = ConfigYesNo(default = True)
	config.epg.mhw = ConfigYesNo(default = True)
	config.epg.freesat = ConfigYesNo(default = True)
	config.epg.viasat = ConfigYesNo(default = True)
	config.epg.netmed = ConfigYesNo(default = True)
	config.epg.virgin = ConfigYesNo(default = False)
	config.misc.showradiopic = ConfigYesNo(default = True)
	def EpgSettingsChanged(configElement):
		from enigma import eEPGCache
		mask = 0xffffffff
		if not config.epg.eit.value:
			mask &= ~(eEPGCache.NOWNEXT | eEPGCache.SCHEDULE | eEPGCache.SCHEDULE_OTHER)
		if not config.epg.mhw.value:
			mask &= ~eEPGCache.MHW
		if not config.epg.freesat.value:
			mask &= ~(eEPGCache.FREESAT_NOWNEXT | eEPGCache.FREESAT_SCHEDULE | eEPGCache.FREESAT_SCHEDULE_OTHER)
		if not config.epg.viasat.value:
			mask &= ~eEPGCache.VIASAT
		if not config.epg.netmed.value:
			mask &= ~(eEPGCache.NETMED_SCHEDULE | eEPGCache.NETMED_SCHEDULE_OTHER)
		if not config.epg.virgin.value:
			mask &= ~(eEPGCache.VIRGIN_NOWNEXT | eEPGCache.VIRGIN_SCHEDULE)
		eEPGCache.getInstance().setEpgSources(mask)
	config.epg.eit.addNotifier(EpgSettingsChanged)
	config.epg.mhw.addNotifier(EpgSettingsChanged)
	config.epg.freesat.addNotifier(EpgSettingsChanged)
	config.epg.viasat.addNotifier(EpgSettingsChanged)
	config.epg.netmed.addNotifier(EpgSettingsChanged)
	config.epg.virgin.addNotifier(EpgSettingsChanged)

	config.epg.maxdays = ConfigSelectionNumber(min = 1, max = 28, stepwidth = 1, default = 5, wraparound = True)
	def EpgmaxdaysChanged(configElement):
		from enigma import eEPGCache
		eEPGCache.getInstance().setEpgmaxdays(config.epg.maxdays.getValue())
	config.epg.maxdays.addNotifier(EpgmaxdaysChanged)

	config.epg.histminutes = ConfigSelectionNumber(min = 0, max = 120, stepwidth = 15, default = 0, wraparound = True)
	def EpgHistorySecondsChanged(configElement):
		from enigma import eEPGCache
		eEPGCache.getInstance().setEpgHistorySeconds(config.epg.histminutes.getValue()*60)
	config.epg.histminutes.addNotifier(EpgHistorySecondsChanged)

	def setHDDStandby(configElement):
		for hdd in harddiskmanager.HDDList():
			hdd[1].setIdleTime(int(configElement.value))
	config.usage.hdd_standby.addNotifier(setHDDStandby, immediate_feedback=False)

	if SystemInfo["12V_Output"]:
		def set12VOutput(configElement):
			Misc_Options.getInstance().set_12V_output(configElement.value == "on" and 1 or 0)
		config.usage.output_12V.addNotifier(set12VOutput, immediate_feedback=False)

	config.usage.keymap = ConfigText(default = eEnv.resolve("${datadir}/enigma2/keymap.xml"))
	config.usage.keytrans = ConfigText(default = eEnv.resolve("${datadir}/enigma2/keytranslation.xml"))

	config.network = ConfigSubsection()
	if SystemInfo["WakeOnLAN"]:
		def wakeOnLANChanged(configElement):
			if getBoxType() in ('et7000', 'et7500', 'gbx1', 'gbx3', 'et10000', 'gbquadplus', 'gbquad', 'gb800ueplus', 'gb800seplus', 'gbultraue', 'gbultrase', 'gbipbox', 'quadbox2400', 'mutant2400', 'et7x00', 'et8500', 'et8500s'):
				open(SystemInfo["WakeOnLAN"], "w").write(configElement.value and "on" or "off")
			else:
				open(SystemInfo["WakeOnLAN"], "w").write(configElement.value and "enable" or "disable")	
		config.network.wol = ConfigYesNo(default = False)
		config.network.wol.addNotifier(wakeOnLANChanged)

	config.network.Inadyn_autostart = ConfigYesNo(default = False)
	config.network.OpenVPN_autostart = ConfigYesNo(default = False)

	config.seek = ConfigSubsection()
	config.seek.selfdefined_13 = ConfigNumber(default=15)
	config.seek.selfdefined_46 = ConfigNumber(default=60)
	config.seek.selfdefined_79 = ConfigNumber(default=300)

	config.seek.speeds_forward = ConfigSet(default=[2, 4, 8, 16, 32, 64, 128], choices=[2, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128])
	config.seek.speeds_backward = ConfigSet(default=[2, 4, 8, 16, 32, 64, 128], choices=[1, 2, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128])
	config.seek.speeds_slowmotion = ConfigSet(default=[2, 4, 8], choices=[2, 4, 6, 8, 12, 16, 25])

	config.seek.enter_forward = ConfigSelection(default = "2", choices = ["2", "4", "6", "8", "12", "16", "24", "32", "48", "64", "96", "128"])
	config.seek.enter_backward = ConfigSelection(default = "1", choices = ["1", "2", "4", "6", "8", "12", "16", "24", "32", "48", "64", "96", "128"])

	config.seek.on_pause = ConfigSelection(default = "play", choices = [
		("play", _("Play")),
		("step", _("Single step (GOP)")),
		("last", _("Last speed")) ])


	config.crash = ConfigSubsection()
	config.crash.details = ConfigYesNo(default = False)

	debugpath = [('/home/root/logs/', '/home/root/')]
	for p in harddiskmanager.getMountedPartitions():
		if os.path.exists(p.mountpoint):
			d = os.path.normpath(p.mountpoint)
			if p.mountpoint != '/':
				debugpath.append((p.mountpoint + 'logs/', d))
	config.crash.debug_path = ConfigSelection(default = "/home/root/logs/", choices = debugpath)
	if not os.path.exists("/home"):
		os.mkdir("/home",0755)
	if not os.path.exists("/home/root"):
		os.mkdir("/home/root",0755)

	def updatedebug_path(configElement):
		if not os.path.exists(config.crash.debug_path.value):
			try:
				os.mkdir(config.crash.debug_path.value,0755)
			except:
				print "Failed to create log path: %s" % config.crash.debug_path.value
	config.crash.debug_path.addNotifier(updatedebug_path, immediate_feedback = False)

	crashlogheader = "We are really sorry. Your receiver encountered " \
					 "a software problem, and needs to be restarted.\n" \
					 "Please send the logfile %senigma2_crash_xxxxxx.log to http://openspa.info.\n" \
					 "Your receiver restarts in 10 seconds!\n" \
					 "Component: enigma2" % config.crash.debug_path.value
	config.crash.debug_text = ConfigText(default=_(crashlogheader), fixed_size=False)

	config.usage.timerlist_finished_timer_position = ConfigSelection(default = "end", choices = [("beginning", _("At beginning")), ("end", _("At end"))])

	def updateEnterForward(configElement):
		if not configElement.value:
			configElement.value = [2]
		updateChoices(config.seek.enter_forward, configElement.value)

	config.seek.speeds_forward.addNotifier(updateEnterForward, immediate_feedback = False)

	def updateEnterBackward(configElement):
		if not configElement.value:
			configElement.value = [2]
		updateChoices(config.seek.enter_backward, configElement.value)

	config.seek.speeds_backward.addNotifier(updateEnterBackward, immediate_feedback = False)

	def updateEraseSpeed(el):
		eBackgroundFileEraser.getInstance().setEraseSpeed(int(el.value))
	def updateEraseFlags(el):
		eBackgroundFileEraser.getInstance().setEraseFlags(int(el.value))
	config.misc.erase_speed = ConfigSelection(default="20", choices = [
		("10", "10 MB/s"),
		("20", "20 MB/s"),
		("50", "50 MB/s"),
		("100", "100 MB/s")])
	config.misc.erase_speed.addNotifier(updateEraseSpeed, immediate_feedback = False)
	config.misc.erase_flags = ConfigSelection(default="1", choices = [
		("0", _("Disable")),
		("1", _("Internal hdd only")),
		("3", _("Everywhere"))])
	config.misc.erase_flags.addNotifier(updateEraseFlags, immediate_feedback = False)

	if SystemInfo["ZapMode"]:
		def setZapmode(el):
			open(SystemInfo["ZapMode"], "w").write(el.value)
		config.misc.zapmode = ConfigSelection(default = "mute", choices = [
			("mute", _("Black screen")), ("hold", _("Hold screen")), ("mutetilllock", _("Black screen till locked")), ("holdtilllock", _("Hold till locked"))])
		config.misc.zapmode.addNotifier(setZapmode, immediate_feedback = False)

	if SystemInfo["HasForceLNBOn"]:
		def forceLNBPowerChanged(configElement):
			open(SystemInfo["HasForceLNBOn"], "w").write(configElement.value)
		config.misc.forceLnbPower = ConfigSelection(default = "on", choices = [ ("on", _("Yes")), ("off", _("No"))] )
		config.misc.forceLnbPower.addNotifier(forceLNBPowerChanged)

	if SystemInfo["HasForceToneburst"]:
		def forceToneBurstChanged(configElement):
			open(SystemInfo["HasForceToneburst"], "w").write(configElement.value)
		config.misc.forceToneBurst = ConfigSelection(default = "enable", choices = [ ("enable", _("Yes")), ("disable", _("No"))] )
		config.misc.forceToneBurst.addNotifier(forceToneBurstChanged)

	config.subtitles = ConfigSubsection()
	config.subtitles.ttx_subtitle_colors = ConfigSelection(default = "1", choices = [
		("0", _("original")),
		("1", _("white")),
		("2", _("yellow")) ])
	config.subtitles.ttx_subtitle_original_position = ConfigYesNo(default = False)
	config.subtitles.subtitle_position = ConfigSelection( choices = ["0", "10", "20", "30", "40", "50", "60", "70", "80", "90", "100", "150", "200", "250", "300", "350", "400", "450"], default = "50")
	config.subtitles.subtitle_alignment = ConfigSelection(choices = [("left", _("left")), ("center", _("center")), ("right", _("right"))], default = "center")
	config.subtitles.subtitle_rewrap = ConfigYesNo(default = False)
	config.subtitles.colourise_dialogs = ConfigYesNo(default = False)
	config.subtitles.subtitle_borderwidth = ConfigSelection(choices = ["1", "2", "3", "4", "5"], default = "3")
	config.subtitles.subtitle_fontsize  = ConfigSelection(choices = ["%d" % x for x in range(16,101) if not x % 2], default = "40")
	config.subtitles.showbackground = ConfigYesNo(default = False)

	subtitle_delay_choicelist = []
	for i in range(-900000, 1845000, 45000):
		if i == 0:
			subtitle_delay_choicelist.append(("0", _("No delay")))
		else:
			subtitle_delay_choicelist.append((str(i), "%2.1f sec" % (i / 90000.)))
	config.subtitles.subtitle_noPTSrecordingdelay = ConfigSelection(default = "315000", choices = subtitle_delay_choicelist)

	config.subtitles.dvb_subtitles_yellow = ConfigYesNo(default = False)
	config.subtitles.dvb_subtitles_original_position = ConfigSelection(default = "0", choices = [("0", _("Original")), ("1", _("Fixed")), ("2", _("Relative"))])
	config.subtitles.dvb_subtitles_centered = ConfigYesNo(default = False)
	config.subtitles.subtitle_bad_timing_delay = ConfigSelection(default = "0", choices = subtitle_delay_choicelist)
	config.subtitles.dvb_subtitles_backtrans = ConfigSelection(default = "0", choices = [
		("0", _("No transparency")),
		("25", "10%"),
		("50", "20%"),
		("75", "30%"),
		("100", "40%"),
		("125", "50%"),
		("150", "60%"),
		("175", "70%"),
		("200", "80%"),
		("225", "90%"),
		("255", _("Full transparency"))])
	config.subtitles.pango_subtitle_colors = ConfigSelection(default = "1", choices = [
		("0", _("alternative")),
		("1", _("white")),
		("2", _("yellow")) ])
	config.subtitles.pango_subtitle_fontswitch = ConfigYesNo(default = True)
	config.subtitles.pango_subtitles_delay = ConfigSelection(default = "0", choices = subtitle_delay_choicelist)
	config.subtitles.pango_subtitles_fps = ConfigSelection(default = "1", choices = [
		("1", _("Original")),
		("23976", _("23.976")),
		("24000", _("24")),
		("25000", _("25")),
		("29970", _("29.97")),
		("30000", _("30"))])
	config.subtitles.pango_autoturnon = ConfigYesNo(default = True)

	config.autolanguage = ConfigSubsection()
	audio_language_choices=[
		("---", _("None")),
		("orj dos ory org esl qaa und mis mul ORY ORJ Audio_ORJ", _("Original")),
		("ara", _("Arabic")),
		("eus baq", _("Basque")),
		("bul", _("Bulgarian")),
		("hrv", _("Croatian")),
		("chn sgp", _("Simplified Chinese")),
		("twn hkn", _("Traditional Chinese")),
		("ces cze", _("Czech")),
		("dan", _("Danish")),
		("dut ndl", _("Dutch")),
		("eng qaa", _("English")),
		("est", _("Estonian")),
		("fin", _("Finnish")),
		("fra fre", _("French")),
		("deu ger", _("German")),
		("ell gre", _("Greek")),
		("heb", _("Hebrew")),
		("hun", _("Hungarian")),
		("ita", _("Italian")),
		("lav", _("Latvian")),
		("lit", _("Lithuanian")),
		("ltz", _("Luxembourgish")),
		("nor", _("Norwegian")),
		("pol", _("Polish")),
		("por dub DUB ud1", _("Portuguese")),
		("fas per", _("Persian")),
		("ron rum", _("Romanian")),
		("rus", _("Russian")),
		("srp", _("Serbian")),
		("slk slo", _("Slovak")),
		("slv", _("Slovenian")),
		("spa", _("Spanish")),
		("swe", _("Swedish")),
		("tha", _("Thai")),
		("tur Audio_TUR", _("Turkish"))]

	def setEpgLanguage(configElement):
		eServiceEvent.setEPGLanguage(configElement.value)
	config.autolanguage.audio_epglanguage = ConfigSelection(audio_language_choices[:1] + audio_language_choices [2:], default="---")
	config.autolanguage.audio_epglanguage.addNotifier(setEpgLanguage)

	def setEpgLanguageAlternative(configElement):
		eServiceEvent.setEPGLanguageAlternative(configElement.value)
	config.autolanguage.audio_epglanguage_alternative = ConfigSelection(audio_language_choices[:1] + audio_language_choices [2:], default="---")
	config.autolanguage.audio_epglanguage_alternative.addNotifier(setEpgLanguageAlternative)

	config.autolanguage.audio_autoselect1 = ConfigSelection(choices=audio_language_choices, default="---")
	config.autolanguage.audio_autoselect2 = ConfigSelection(choices=audio_language_choices, default="---")
	config.autolanguage.audio_autoselect3 = ConfigSelection(choices=audio_language_choices, default="---")
	config.autolanguage.audio_autoselect4 = ConfigSelection(choices=audio_language_choices, default="---")
	config.autolanguage.audio_defaultac3 = ConfigYesNo(default = False)
	config.autolanguage.audio_defaultddp = ConfigYesNo(default = False)
	config.autolanguage.audio_usecache = ConfigYesNo(default = True)

	subtitle_language_choices = audio_language_choices[:1] + audio_language_choices [2:]
	config.autolanguage.subtitle_autoselect1 = ConfigSelection(choices=subtitle_language_choices, default="---")
	config.autolanguage.subtitle_autoselect2 = ConfigSelection(choices=subtitle_language_choices, default="---")
	config.autolanguage.subtitle_autoselect3 = ConfigSelection(choices=subtitle_language_choices, default="---")
	config.autolanguage.subtitle_autoselect4 = ConfigSelection(choices=subtitle_language_choices, default="---")
	config.autolanguage.subtitle_hearingimpaired = ConfigYesNo(default = False)
	config.autolanguage.subtitle_defaultimpaired = ConfigYesNo(default = False)
	config.autolanguage.subtitle_defaultdvb = ConfigYesNo(default = False)
	config.autolanguage.subtitle_usecache = ConfigYesNo(default = True)
	config.autolanguage.equal_languages = ConfigSelection(default = "15", choices = [
		("0", _("None")),("1", "1"),("2", "2"),("3", "1,2"),
		("4", "3"),("5", "1,3"),("6", "2,3"),("7", "1,2,3"),
		("8", "4"),("9", "1,4"),("10", "2,4"),("11", "1,2,4"),
		("12", "3,4"),("13", "1,3,4"),("14", "2,3,4"),("15", _("All"))])

	config.streaming = ConfigSubsection()
	config.streaming.stream_ecm = ConfigYesNo(default = False)
	config.streaming.descramble = ConfigYesNo(default = True)
	config.streaming.descramble_client = ConfigYesNo(default = False)
	config.streaming.stream_eit = ConfigYesNo(default = True)
	config.streaming.stream_ait = ConfigYesNo(default = True)
	config.streaming.authentication = ConfigYesNo(default = False)

	config.mediaplayer = ConfigSubsection()
	config.mediaplayer.useAlternateUserAgent = ConfigYesNo(default=False)
	config.mediaplayer.alternateUserAgent = ConfigText(default="")

	#config.osd = ConfigSubsection()
	config.osd.dst_left = ConfigSelectionNumber(default = 0, stepwidth = 1, min = 0, max = 720, wraparound = False)
	config.osd.dst_width = ConfigSelectionNumber(default = 720, stepwidth = 1, min = 0, max = 720, wraparound = False)
	config.osd.dst_top = ConfigSelectionNumber(default = 0, stepwidth = 1, min = 0, max = 576, wraparound = False)
	config.osd.dst_height = ConfigSelectionNumber(default = 576, stepwidth = 1, min = 0, max = 576, wraparound = False)
	config.osd.alpha = ConfigSelectionNumber(default = 255, stepwidth = 1, min = 0, max = 255, wraparound = False)
	config.osd.alpha_teletext = ConfigSelectionNumber(default = 255, stepwidth = 1, min = 0, max = 255, wraparound = False)
	config.osd.alpha_webbrowser = ConfigSelectionNumber(default = 255, stepwidth = 1, min = 0, max = 255, wraparound = False)
	config.av.osd_alpha = NoSave(ConfigNumber(default = 255))
	config.osd.threeDmode = ConfigSelection([("off", _("Off")), ("auto", _("Auto")), ("sidebyside", _("Side by Side")),("topandbottom", _("Top and Bottom"))], "auto")
	config.osd.threeDznorm = ConfigSlider(default = 50, increment = 1, limits = (0, 100))
	config.osd.show3dextensions = ConfigYesNo(default = False)
	choiceoptions = [("mode1", _("Mode 1")), ("mode2", _("Mode 2"))]
	config.osd.threeDsetmode = ConfigSelection(default = 'mode1' , choices = choiceoptions )

def updateChoices(sel, choices):
	if choices:
		defval = None
		val = int(sel.value)
		if not val in choices:
			tmp = choices[:]
			tmp.reverse()
			for x in tmp:
				if x < val:
					defval = str(x)
					break
		sel.setChoices(map(str, choices), defval)

def preferredPath(path):
	if config.usage.setup_level.index < 2 or path == "<default>":
		return None  # config.usage.default_path.value, but delay lookup until usage
	elif path == "<current>":
		return config.movielist.last_videodir.value
	elif path == "<timer>":
		return config.movielist.last_timer_videodir.value
	else:
		return path

def preferredTimerPath():
	return preferredPath(config.usage.timer_path.value)

def preferredInstantRecordPath():
	return preferredPath(config.usage.instantrec_path.value)

def defaultMoviePath():
	return defaultRecordingLocation(config.usage.default_path.value)

def patchTuxtxtConfFile(dummyConfigElement):
	print "[tuxtxt] patching tuxtxt2.conf"
	if config.usage.tuxtxt_font_and_res.value == "X11_SD":
		tuxtxt2 = [["UseTTF",0],
		           ["TTFBold",1],
		           ["TTFScreenResX",720],
		           ["StartX",50],
		           ["EndX",670],
		           ["StartY",30],
		           ["EndY",555],
		           ["TTFShiftY",0],
		           ["TTFShiftX",0],
		           ["TTFWidthFactor16",26],
		           ["TTFHeightFactor16",14]]
	elif config.usage.tuxtxt_font_and_res.value == "TTF_SD":
		tuxtxt2 = [["UseTTF",1],
		           ["TTFBold",1],
		           ["TTFScreenResX",720],
		           ["StartX",50],
		           ["EndX",670],
		           ["StartY",30],
		           ["EndY",555],
		           ["TTFShiftY",2],
		           ["TTFShiftX",0],
		           ["TTFWidthFactor16",29],
		           ["TTFHeightFactor16",14]]
	elif config.usage.tuxtxt_font_and_res.value == "TTF_HD":
		tuxtxt2 = [["UseTTF",1],
		           ["TTFBold",0],
		           ["TTFScreenResX",1280],
		           ["StartX",80],
		           ["EndX",1200],
		           ["StartY",35],
		           ["EndY",685],
		           ["TTFShiftY",-3],
		           ["TTFShiftX",0],
		           ["TTFWidthFactor16",26],
		           ["TTFHeightFactor16",14]]
	elif config.usage.tuxtxt_font_and_res.value == "TTF_FHD":
		tuxtxt2 = [["UseTTF",1],
		           ["TTFBold",0],
		           ["TTFScreenResX",1920],
		           ["StartX",140],
		           ["EndX",1780],
		           ["StartY",52],
		           ["EndY",1027],
		           ["TTFShiftY",-6],
		           ["TTFShiftX",0],
		           ["TTFWidthFactor16",26],
		           ["TTFHeightFactor16",14]]
	elif config.usage.tuxtxt_font_and_res.value == "expert_mode":
		tuxtxt2 = [["UseTTF",            int(config.usage.tuxtxt_UseTTF.value)],
		           ["TTFBold",           int(config.usage.tuxtxt_TTFBold.value)],
		           ["TTFScreenResX",     int(config.usage.tuxtxt_TTFScreenResX.value)],
		           ["StartX",            config.usage.tuxtxt_StartX.value],
		           ["EndX",              config.usage.tuxtxt_EndX.value],
		           ["StartY",            config.usage.tuxtxt_StartY.value],
		           ["EndY",              config.usage.tuxtxt_EndY.value],
		           ["TTFShiftY",         int(config.usage.tuxtxt_TTFShiftY.value)],
		           ["TTFShiftX",         int(config.usage.tuxtxt_TTFShiftX.value)],
		           ["TTFWidthFactor16",  config.usage.tuxtxt_TTFWidthFactor16.value],
		           ["TTFHeightFactor16", config.usage.tuxtxt_TTFHeightFactor16.value]]
	tuxtxt2.append(    ["CleanAlgo",         config.usage.tuxtxt_CleanAlgo.value] )

	TUXTXT_CFG_FILE = "/etc/tuxtxt/tuxtxt2.conf"
	command = "sed -i -r '"
	for f in tuxtxt2:
		#replace keyword (%s) followed by any value ([-0-9]+) by that keyword \1 and the new value %d
		command += "s|(%s)\s+([-0-9]+)|\\1 %d|;" % (f[0],f[1])
	command += "' %s" % TUXTXT_CFG_FILE
	for f in tuxtxt2:
		#if keyword is not found in file, append keyword and value
		command += " ; if ! grep -q '%s' %s ; then echo '%s %d' >> %s ; fi"  % (f[0],TUXTXT_CFG_FILE,f[0],f[1],TUXTXT_CFG_FILE)
	try:
		os.system(command)
	except:
		print "Error: failed to patch %s!" % TUXTXT_CFG_FILE
	print "[tuxtxt] patched tuxtxt2.conf"

	config.usage.tuxtxt_ConfFileHasBeenPatched.setValue(True)
