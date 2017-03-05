from Screen import Screen
from Screens.Setup import getConfigMenuItem, Setup
from Components.ServiceEventTracker import ServiceEventTracker
from Components.ActionMap import ActionMap,NumberActionMap
from Components.ConfigList import ConfigListScreen
from Components.ChoiceList import ChoiceList, ChoiceEntryComponent
from Components.config import config, ConfigSubsection, getConfigListEntry, ConfigNothing, ConfigSelection, ConfigOnOff
from Components.Label import Label
from Components.MultiContent import MultiContentEntryText
from Components.Sources.List import List
from Components.Sources.Boolean import Boolean
from Components.SystemInfo import SystemInfo

from enigma import iPlayableService, eTimer, eSize

from Tools.ISO639 import LanguageCodes

FOCUS_CONFIG, FOCUS_STREAMS = range(2)
[PAGE_AUDIO, PAGE_SUBTITLES] = ["audio", "subtitles"]

def pondebug(texto):
	if False:
		import os
		os.system("echo '"+texto+"'>>/tmp/debugaudio.log")
		os.system("echo '*******************************'>>/tmp/debugaudio.log")
		
class AudioSelection(Screen, ConfigListScreen):
	def __init__(self, session, infobar=None, page=PAGE_AUDIO):
		Screen.__init__(self, session)

		self["streams"] = List([], enableWrapAround=True)
		self["key_red"] = Boolean(False)
		self["key_green"] = Boolean(False)
		self["key_yellow"] = Boolean(False)
		self["key_blue"] = Boolean(True)
		#add by mpiero
		try:
			self["key_info"] = Label(_("Audio")+"/"+_("Subtitles"))
			self["key_infos"] = Label(_("Options"))
		except:
			pass

		ConfigListScreen.__init__(self, [])
		self.infobar = infobar or self.session.infobar

		self.__event_tracker = ServiceEventTracker(screen=self, eventmap=
			{
				iPlayableService.evUpdatedInfo: self.__updatedInfo
			})
		self.cached_subtitle_checked = False
		self.__selected_subtitle = None

		self["actions"] = ActionMap(["AudioSelectionActions", "SetupActions", "DirectionActions", "MenuActions"],
		{
			"red": self.keyRed,
			"green": self.keyGreen,
			"yellow": self.keyYellow,
			"blue": self.keyBlue,
			"ok": self.keyOk,
			"cancel": self.cancel,
			"up": self.keyUp,
			"down": self.keyDown,
			"menu": self.openAutoLanguageSetup,

			
		}, -2)
		self["actions2"] = ActionMap(["InfobarSubtitleSelectionActions", "MoviePlayerActions"],
		{
			#add by mpiero		
			"subtitleSelection": self.keyChange,
			"AudioSelection": self.keyChange,
		}, -3)
		self.settings = ConfigSubsection()
		choicelist = [(PAGE_AUDIO,""), (PAGE_SUBTITLES,"")]
		self.settings.menupage = ConfigSelection(choices = choicelist, default=page)
		self.onLayoutFinish.append(self.__layoutFinished)
		#add by mpiero 
		self.numplugin=None
	def keyGotAscii(self):
		pass
	def __layoutFinished(self):
		self["config"].instance.setSelectionEnable(False)
		self.focus = FOCUS_STREAMS
		self.settings.menupage.addNotifier(self.fillList)

	def fillList(self, arg=None):
		streams = []
		conflist = []
		selectedidx = 0

		# self["key_blue"].setBoolean(False)

		subtitlelist = self.getSubtitleList()
		self.nummplugin=None
		
		#### modify this section for add audio functions
		if self.settings.menupage.getValue() == PAGE_AUDIO:
			self.setTitle(_("Select audio track"))
			self["key_yellow"].setBoolean(True)
			self["key_green"].setBoolean(True)
			self["key_red"].setBoolean(True)
			service = self.session.nav.getCurrentService()
			self.audioTracks = audio = service and service.audioTracks()
			n = audio and audio.getNumberOfTracks() or 0

			if SystemInfo["CanDownmixAC3"]:
				self.settings.downmix_ac3 = ConfigOnOff(default=config.av.downmix_ac3.getValue())
				self.settings.downmix_ac3.addNotifier(self.changeAC3Downmix, initial_call = False)
				conflist.append(getConfigListEntry(_("AC3 downmix"), self.settings.downmix_ac3))

			if SystemInfo["CanDownmixDTS"]:
				self.settings.downmix_dts = ConfigOnOff(default=config.av.downmix_dts.value)
				self.settings.downmix_dts.addNotifier(self.changeDTSDownmix, initial_call = False)
				conflist.append(getConfigListEntry(_("DTS downmix"), self.settings.downmix_dts, None))

			if SystemInfo["CanDownmixAAC"]:
				self.settings.downmix_aac = ConfigOnOff(default=config.av.downmix_aac.getValue())
				self.settings.downmix_aac.addNotifier(self.changeAACDownmix, initial_call = False)
				conflist.append(getConfigListEntry(_("AAC downmix"), self.settings.downmix_aac))

			if SystemInfo["CanAACTranscode"]:
				choice_list = [("off", _("off")), ("ac3", _("AC3")), ("dts", _("DTS"))]
				self.settings.transcodeaac = ConfigSelection(choices = choice_list, default = "off")
				self.settings.transcodeaac.addNotifier(self.setAACTranscode, initial_call = False)
				conflist.append(getConfigListEntry(_("AAC transcoding"), self.settings.transcodeaac, None))

			if SystemInfo["CanAC3plusTranscode"]:
				choice_list = [("use_hdmi_caps", _("controlled by HDMI")), ("force_ac3", _("always"))]
				self.settings.transcodeac3plus = ConfigSelection(choices = choice_list, default = "use_hdmi_caps")
				self.settings.transcodeac3plus.addNotifier(self.setAC3plusTranscode, initial_call = False)
				conflist.append(getConfigListEntry(_("AC3plus transcoding"), self.settings.transcodeac3plus, None))

			if SystemInfo["CanPcmMultichannel"]:
				self.settings.pcm_multichannel = ConfigOnOff(default=config.av.pcm_multichannel.getValue())
				self.settings.pcm_multichannel.addNotifier(self.changePCMMultichannel, initial_call = False)
				conflist.append(getConfigListEntry(_("PCM Multichannel"), self.settings.pcm_multichannel, None))

			if n > 0:
				self.audioChannel = service.audioChannel()
				if self.audioChannel:
					choicelist = [("0",_("left")), ("1",_("stereo")), ("2", _("right"))]
					self.settings.channelmode = ConfigSelection(choices = choicelist, default = str(self.audioChannel.getCurrentChannel()))
					self.settings.channelmode.addNotifier(self.changeMode, initial_call = False)
					conflist.append(getConfigListEntry(_("Audio Channel"), self.settings.channelmode))
				else:
					conflist.append(getConfigListEntry("", ConfigNothing()))
					# self["key_green"].setBoolean(False)
				selectedAudio = self.audioTracks.getCurrentTrack()
				conta=0
				
				
				for x in range(n):
					
					number = str(conta + 1)
					i = audio.getTrackInfo(x)
					
					languages = i.getLanguage().split('/')
					description = i.getDescription() or ""
					pondebug("AUDIO "+str(conta)+" - "+str(languages)+" - "+str(description))
					selected = ""
					language = ""

					if selectedAudio == x:
						selected = "X"
						selectedidx = x

					cnt = 0
					for lang in languages:
						if cnt:
							language += ' / '
						if lang.lower() == "und":
							language +=_("Language")+" "+number+""
						elif lang.lower() == "qaa":
							language +=_("Original track audio")+""
						elif LanguageCodes.has_key(lang):
							templan=str(LanguageCodes[lang][0])
							if templan==None or templan=="":
								language +=_("Language")+" "+number+" ("+str(lang)+")"
							else:
								language += _(templan)
						else:
							
							if lang==None or lang=="":
								language += _("Language")+" ["+number+"] "+str(lang)+""
							else:
								language += _("Language")+" ["+number+"] "+str(lang)+""

						cnt += 1
					if language!="---":
						try:
							streams.append((x, "", number,  language,description, selected))
							conta+=1
						except:
							pass

			else:
				streams = []
				conflist.append(getConfigListEntry("", ConfigNothing()))
				# self["key_green"].setBoolean(False)
				
			#add by mpiero
			try:
				self["key_info"].setText(_("To subtitle selection"))
			except:
				pass

			if subtitlelist:
				# self["key_yellow"].setBoolean(True)
				# conflist.append(getConfigListEntry(_("To subtitle selection"), self.settings.menupage))
				pass
			else:
				# self["key_yellow"].setBoolean(False)
				conflist.append(getConfigListEntry("", ConfigNothing()))

			if SystemInfo["Can3DSurround"]:
				surround_choicelist = [("none", _("off")), ("hdmi", _("HDMI")), ("spdif", _("SPDIF")), ("dac", _("DAC"))]
				self.settings.surround_3d = ConfigSelection(choices = surround_choicelist, default = config.av.surround_3d.getValue())
				self.settings.surround_3d.addNotifier(self.change3DSurround, initial_call = False)
				conflist.append(getConfigListEntry(_("3D Surround"), self.settings.surround_3d))

			from Components.PluginComponent import plugins
			from Plugins.Plugin import PluginDescriptor

			if hasattr(self.infobar, "runPlugin"):
				class PluginCaller:
					def __init__(self, fnc, *args):
						self.fnc = fnc
						self.args = args
					def __call__(self, *args, **kwargs):
						self.fnc(*self.args)

				Plugins = [ (p.name, PluginCaller(self.infobar.runPlugin, p)) for p in plugins.getPlugins(where = PluginDescriptor.WHERE_AUDIOMENU) ]

				if len(Plugins):
					#add by mpiero
					# self["key_blue"].setBoolean(True)
					conflist.append(getConfigListEntry(Plugins[0][0], ConfigNothing()))
					self.plugincallfunc = Plugins[0][1]
					self.nummplugin=len(conflist)-1
				
				if len(Plugins) > 1:
					print "plugin(s) installed but not displayed in the dialog box:", Plugins[1:]

		#### modify this section for add subtitle functions
		elif self.settings.menupage.getValue() == PAGE_SUBTITLES:

			self.setTitle(_("Subtitle selection"))
			# conflist.append(getConfigListEntry("----", ConfigNothing()))
			# conflist.append(getConfigListEntry("----", ConfigNothing()))
			self["key_yellow"].setBoolean(False)
			self["key_green"].setBoolean(False)
			self["key_red"].setBoolean(False)
			selected="X"
			for x in subtitlelist:
				if self.selectedSubtitle and x[:4] == self.selectedSubtitle[:4]:
					selected = ""
					
			streams.append(("Ninguno", "", "1",  "("+_("Deactivate")+")",""+_("No subtitles"), selected))
			idx = 1
			selectedidx=0
			for x in subtitlelist:
				pondebug("SUBTITLES "+str(idx)+" - "+str(x))
				number = str(x[1])
				description = "?"
				language = ""
				selected = ""

				if self.selectedSubtitle and x[:4] == self.selectedSubtitle[:4]:
					selected = "X"
					selectedidx = idx
					
				try:
					if x[4].lower()=="und":
						language +=_("Language")+" "+str(idx+1)+""
					elif x[4].lower() == "qaa":
						language +=_("Original track audio")+""
					elif LanguageCodes.has_key(x[4]):
						language = _(LanguageCodes[x[4]][0])
					else:
						language =_("Language")+" "+str(idx+1)+" ("+str(x[4])+")"
				except:
					language = ""


				if x[0] == 0:
					description = _("Digital Subtitle")+"(DVB)"
					number = "%x" % (x[1])

				elif x[0] == 1:
					description =  _("Teletext Subtitle")+"(TXT)"
					number = "%x%02x" %(x[3] and x[3] or 8, x[2])

				elif x[0] == 2:
					types = (_("unknown"), "embedded", _("File")+" "+"SSA", _("File")+" "+"ASS",
							_("File")+" "+"SRT", _("File")+" "+"VOB", _("File")+" "+"PGS")
					try:
						description = types[x[2]]
					except:
						description = _("unknown") + ": %s" % x[2]
					number = str(int(number) + 1)
				if language==None or language=="":
					pass
				else:
					streams.append((x, "", str(idx+1), language,description , selected))
					idx += 1

			# conflist.append(getConfigListEntry(_("To audio selection"), self.settings.menupage))
			try:
				self["key_info"].setText(_("To audio selection"))
			except:
				pass
			if self.infobar.selected_subtitle and self.infobar.selected_subtitle != (0,0,0,0)  and not ".DVDPlayer'>" in `self.infobar`:
				self["key_red"].setBoolean(True)
				conflist.append(getConfigListEntry(_("Subtitle Quickmenu"), ConfigNothing()))
			# else:
				# conflist.append(getConfigListEntry("----", ConfigNothing()))

		self["config"].list = conflist
		self["config"].l.setList(conflist)

		self["streams"].list = streams
		self["streams"].setIndex(selectedidx)


	def __updatedInfo(self):
		self.fillList()
		#add by mpiero
		self.spa__updatedInfo()

	def getSubtitleList(self):
		service = self.session.nav.getCurrentService()
		subtitle = service and service.subtitle()
		subtitlelist = subtitle and subtitle.getSubtitleList()
		self.selectedSubtitle = None
		if self.subtitlesEnabled():
			self.selectedSubtitle = self.infobar.selected_subtitle
			if self.selectedSubtitle and self.selectedSubtitle[:4] == (0,0,0,0):
				self.selectedSubtitle = None
			elif self.selectedSubtitle and not self.selectedSubtitle[:4] in (x[:4] for x in subtitlelist):
				subtitlelist.append(self.selectedSubtitle)
		return subtitlelist

	def subtitlesEnabled(self):
		try:
			return self.infobar.subtitle_window.shown
		except: 
			return False

	def enableSubtitle(self, subtitle):
		if self.infobar.selected_subtitle != subtitle:
			self.infobar.enableSubtitle(subtitle)

	def change3DSurround(self, surround_3d):
		if surround_3d.getValue():
			config.av.surround_3d.value = surround_3d.getValue()
		config.av.surround_3d.save()

	def changeAC3Downmix(self, downmix):
		if downmix.getValue():
			config.av.downmix_ac3.setValue(True)
			if SystemInfo["supportPcmMultichannel"]:
				config.av.pcm_multichannel.setValue(False)
		else:
			config.av.downmix_ac3.setValue(False)
		config.av.downmix_ac3.save()
		if SystemInfo["supportPcmMultichannel"]:
			config.av.pcm_multichannel.save()
		self.fillList()

	def changePCMMultichannel(self, multichan):
		if multichan.getValue():
			config.av.pcm_multichannel.setValue(True)
		else:
			config.av.pcm_multichannel.setValue(False)
		config.av.pcm_multichannel.save()
		self.fillList()

	def changeAACDownmix(self, downmix):
		if downmix.getValue():
			config.av.downmix_aac.setValue(True)
		else:
			config.av.downmix_aac.setValue(False)
		config.av.downmix_aac.save()

	def setAC3plusTranscode(self, transcode):
		config.av.transcodeac3plus.setValue(transcode)
		config.av.transcodeac3plus.save()

	def changeDTSDownmix(self, downmix):
		if downmix.getValue():
			config.av.downmix_dts.setValue(True)
		else:
			config.av.downmix_dts.setValue(False)
		config.av.downmix_dts.save()

	def setAACTranscode(self, transcode):
		config.av.transcodeaac.setValue(transcode)
		config.av.transcodeaac.save()

	def changeMode(self, mode):
		if mode is not None and self.audioChannel:
			self.audioChannel.selectChannel(int(mode.getValue()))

	def changeAudio(self, audio):
		track = int(audio)
		if isinstance(track, int):
			if self.session.nav.getCurrentService().audioTracks().getNumberOfTracks() > track:
				self.audioTracks.selectTrack(track)

	def keyLeft(self):
		if self.focus == FOCUS_CONFIG:
			ConfigListScreen.keyLeft(self)
		elif self.focus == FOCUS_STREAMS:
			self.keyAudioSubtitle()

	def keyRight(self, config = False):
		#add by mpiero
		if config or self.focus == FOCUS_CONFIG:
			if self.nummplugin!=None and self.nummplugin==self["config"].getCurrentIndex() and self.settings.menupage.getValue() == PAGE_AUDIO and hasattr(self, "plugincallfunc"):
				try:
					self.plugincallfunc()
				except:
					pass
			elif self["config"].getCurrentIndex() == 0 and self.settings.menupage.getValue() == PAGE_SUBTITLES and self.infobar.selected_subtitle and self.infobar.selected_subtitle != (0,0,0,0):
				self.session.open(QuickSubtitlesConfigMenu, self.infobar)
			else:
				ConfigListScreen.keyRight(self)

		if self.focus == FOCUS_STREAMS and config == False:
			self.keyAudioSubtitle()

	def keyRed(self):
		if self["key_red"].getBoolean():
			self.colorkey(0)
		else:
			return 0

	def keyGreen(self):
		if self["key_green"].getBoolean():
			self.colorkey(1)
		else:
			return 0

	def keyYellow(self):
		if self["key_yellow"].getBoolean():
			self.colorkey(2)
		else:
			return 0

	def keyBlue(self):
		# add by mpiero
		self.keyChange()
		return
		if self["key_blue"].getBoolean():
			self.colorkey(3)
		else:
			return 0

	def keyAudioSubtitle(self):
		if self.settings.menupage.value == PAGE_AUDIO:
			self.settings.menupage.setValue('subtitles')
		else:
			self.settings.menupage.setValue('audio')

	def colorkey(self, idx):
		try:
			if idx<=len(self["config"].getList())-1:
				self["config"].setCurrentIndex(idx)
				self.keyRight(True)
		except:
			pass

	def keyUp(self):
		#add by mpiero
		if self.focus == FOCUS_CONFIG:
			if self["config"].getCurrentIndex()>0:
				self["config"].instance.moveSelection(self["config"].instance.moveUp)
			else:
				self["config"].instance.setSelectionEnable(False)
				self["streams"].style = "default"
				self.focus = FOCUS_STREAMS
				try:
					self["streams"].setIndex(len(self["streams"].list)-1)
				except:
					pass
		elif self.focus == FOCUS_STREAMS:
			self["streams"].selectPrevious()

	def keyDown(self):
		#add by mpiero
		if self.focus == FOCUS_CONFIG:
			self["config"].instance.moveSelection(self["config"].instance.moveDown)
		elif self.focus == FOCUS_STREAMS:
			if self["streams"].getIndex() < len(self["streams"].list)-1:
				self["streams"].selectNext()
			elif len(self["config"].getList())>0:
				self["config"].instance.setSelectionEnable(True)
				self["streams"].style = "notselected"
				self["config"].setCurrentIndex(0)
				self.focus = FOCUS_CONFIG


	def keyNumberGlobal(self, number=1):
		#add by mpiero
		try:
			if number <= len(self["streams"].list):
				self["streams"].setIndex(number-1)
				self.keyOk()
		except:
			pass

	def keyOk(self):
		if self.focus == FOCUS_STREAMS and self["streams"].list:
			cur = self["streams"].getCurrent()
			if self.settings.menupage.getValue() == PAGE_AUDIO and cur[0] is not None:
				self.changeAudio(cur[0])
				self.__updatedInfo()
			if self.settings.menupage.getValue() == PAGE_SUBTITLES and cur[0] is not None:
				if self["streams"].getIndex()==0:
					self.enableSubtitle(None)
					selectedidx = self["streams"].getIndex()
					self.__updatedInfo()
					self["streams"].setIndex(selectedidx)
				elif self.infobar.selected_subtitle and self.infobar.selected_subtitle[:4] == cur[0][:4]:
					pass
				else:
					self.enableSubtitle(cur[0][:5])
					self.__updatedInfo()
			self.close(0)
		elif self.focus == FOCUS_CONFIG:
			#add by mpiero
			if self.settings.menupage.getValue() == PAGE_SUBTITLES:
				self.keyRight()
			else:
				self.keyLeft()

	def openAutoLanguageSetup(self):
		#add by mpiero openspa
		self.spaopenAutoLanguageSetup()
		# self.session.open(Setup, "autolanguagesetup")

	def cancel(self):
		self.close(0)

	#add by mpiero openspa
	####audio selection fix

	def keyChange(self):
		try:
			if self.settings.menupage.getValue() == PAGE_AUDIO:
				self.settings.menupage.setValue(PAGE_SUBTITLES)
			else:
				self.settings.menupage.setValue(PAGE_AUDIO)
			self["config"].instance.setSelectionEnable(False)
			self["streams"].style = "default"
			self.focus = FOCUS_STREAMS
		except:
			pass

	def spa__updatedInfo(self):
		pass

	def spaopenAutoLanguageSetup(self):
		from Screens.ChoiceBox import ChoiceBox
		listares=[]
		nkeys=[]
		listares.append((_("Setup")+" - "+_("Auto language selection"), "setup"))
		nkeys.append(("1"))
		if self["config"].getCurrentIndex() == 0 and self.settings.menupage.getValue() == PAGE_SUBTITLES and self.infobar.selected_subtitle and self.infobar.selected_subtitle != (0,0,0,0):
			listares.append((_("Subtitle Quickmenu"), "quick"))
			nkeys.append(("red"))
		listares.append(("--", "nada"))
		nkeys.append((""))
		if self.settings.menupage.getValue() != PAGE_AUDIO:
			listares.append((_("To audio selection"), "audio"))
			nkeys.append(("blue"))
		if self.settings.menupage.getValue() != PAGE_SUBTITLES:
			listares.append((_("To subtitle selection"), "sub"))
			nkeys.append(("blue"))
		ctitulo= _("Options")+ " - "+_("Audio")+"/"+_("Subtitles")
		self.session.openWithCallback(self.spaselectaudio,ChoiceBox,keys = nkeys,title=ctitulo ,list=listares)

	def spaselectaudio(self, answer):
		answer = answer and answer[1]
		if answer:
			if answer=="audio":
				self.settings.menupage.setValue(PAGE_AUDIO)
			if answer=="sub":
				self.settings.menupage.setValue(PAGE_SUBTITLES)
			if answer=="setup":
				self.irasetup()
			if answer=="quick":
				try:
					self.session.open(QuickSubtitlesConfigMenu, self.infobar)				
				except:
					pass
		return

	def irasetup(self):
		self.session.open(Setup, "autolanguagesetup")
#end fix audio openspa

class SubtitleSelection(AudioSelection):
	def __init__(self, session, infobar=None):
		AudioSelection.__init__(self, session, infobar, page=PAGE_SUBTITLES)
		self.skinName = ["AudioSelection"]

class QuickSubtitlesConfigMenu(ConfigListScreen, Screen):
	skin = """
	<screen position="50,75" size="520,255" title="Subtitle Quickmenu" backgroundColor="background" flags="wfBorder">
		<widget name="config" position="5,5" size="510,225" font="Regular;18" zPosition="1" transparent="1" valign="center" />
		<widget name="videofps" position="5,230" size="510,20" transparent="1" zPosition="1" font="Regular;16" valign="center" halign="left"/>
	</screen>"""

	def __init__(self, session, infobar):
		Screen.__init__(self, session)
		self.skin = QuickSubtitlesConfigMenu.skin
		self.infobar = infobar or self.session.infobar

		self.wait = eTimer()
		self.wait.timeout.get().append(self.resyncSubtitles)

		self.resume = eTimer()
		self.resume.timeout.get().append(self.resyncSubtitlesResume)

		self["videofps"] = Label("")

		sub = self.infobar.selected_subtitle
		if sub[0] == 0:  # dvb
			menu = [
				getConfigMenuItem("config.subtitles.dvb_subtitles_yellow"),
				getConfigMenuItem("config.subtitles.dvb_subtitles_centered"),
				getConfigMenuItem("config.subtitles.dvb_subtitles_backtrans"),
				getConfigMenuItem("config.subtitles.dvb_subtitles_original_position"),
				getConfigMenuItem("config.subtitles.subtitle_position"),
				getConfigMenuItem("config.subtitles.subtitle_bad_timing_delay"),
				getConfigMenuItem("config.subtitles.subtitle_noPTSrecordingdelay"),
			]
		elif sub[0] == 1: # teletext
			menu = [
				getConfigMenuItem("config.subtitles.ttx_subtitle_colors"),
				getConfigMenuItem("config.subtitles.ttx_subtitle_original_position"),
				getConfigMenuItem("config.subtitles.subtitle_fontsize"),
				getConfigMenuItem("config.subtitles.subtitle_position"),
				getConfigMenuItem("config.subtitles.subtitle_rewrap"),
				getConfigMenuItem("config.subtitles.subtitle_borderwidth"),
				getConfigMenuItem("config.subtitles.showbackground"),
				getConfigMenuItem("config.subtitles.subtitle_alignment"),
				getConfigMenuItem("config.subtitles.subtitle_bad_timing_delay"),
				getConfigMenuItem("config.subtitles.subtitle_noPTSrecordingdelay"),
			]
		else: 		# pango
			menu = [
				getConfigMenuItem("config.subtitles.pango_subtitles_delay"),
				getConfigMenuItem("config.subtitles.pango_subtitle_colors"),
				getConfigMenuItem("config.subtitles.pango_subtitle_fontswitch"),
				getConfigMenuItem("config.subtitles.colourise_dialogs"),
				getConfigMenuItem("config.subtitles.subtitle_fontsize"),
				getConfigMenuItem("config.subtitles.subtitle_position"),
				getConfigMenuItem("config.subtitles.subtitle_alignment"),
				getConfigMenuItem("config.subtitles.subtitle_rewrap"),
				getConfigMenuItem("config.subtitles.subtitle_borderwidth"),
				getConfigMenuItem("config.subtitles.showbackground"),
				getConfigMenuItem("config.subtitles.pango_subtitles_fps"),
			]
			self["videofps"].setText(_("Video: %s fps") % (self.getFps().rstrip(".000")))

		ConfigListScreen.__init__(self, menu, self.session, on_change = self.changedEntry)

		self["actions"] = NumberActionMap(["SetupActions"],
		{
			"cancel": self.cancel,
			"ok": self.ok,
			"1": self.keyNumber,
			"3": self.keyNumber,
			"4": self.keyNumber,
			"6": self.keyNumber,
			"7": self.keyNumber,
			"9": self.keyNumber,
			"0": self.keyNumber,
		},-2)

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		if not self["videofps"].text:
			self.instance.resize(eSize(self.instance.size().width(), self["config"].l.getItemSize().height()*len(self["config"].getList()) + 10))

	def keyNumber(self, number):
		menuEntry = getConfigMenuItem("config.subtitles.pango_subtitles_delay")
		if self["config"].getCurrent() != menuEntry:
			return
		configItem = menuEntry[1]
		delay = int(configItem.getValue())
		minDelay = int(configItem.choices[0])
		maxDelay = int(configItem.choices[len(configItem.choices) - 1])

		if number == 1:
			delay -= 45000 # -0.5sec
		elif number == 3:
			delay += 45000 # +0.5sec
		elif number == 4:
			delay -= 90000 * 5 # -5sec
		elif number == 6:
			delay += 90000 * 5 # +5sec
		elif number == 7:
			delay -= 90000 * 30 # -30sec
		elif number == 9:
			delay += 90000 * 30 # +30sec
		elif number == 0:
			delay = 0 # reset to "No delay"

		delay = min(max(delay, minDelay), maxDelay)

		configItem.setValue(str(delay))
		self["config"].invalidate(menuEntry)
		self.wait.start(500, True)

	def changedEntry(self):
		if self["config"].getCurrent() in [getConfigMenuItem("config.subtitles.pango_subtitles_delay"),getConfigMenuItem("config.subtitles.pango_subtitles_fps")]:
			self.wait.start(500, True)

	def resyncSubtitles(self):
		self.infobar.setSeekState(self.infobar.SEEK_STATE_PAUSE)
		self.resume.start(100, True)

	def resyncSubtitlesResume(self):
		self.infobar.setSeekState(self.infobar.SEEK_STATE_PLAY)

	def getFps(self):
		from enigma import iServiceInformation
		service = self.session.nav.getCurrentService()
		info = service and service.info()
		if not info:
			return ""
		fps = info.getInfo(iServiceInformation.sFrameRate)
		if fps > 0:
			return "%6.3f" % (fps/1000.)
		return ""

	def cancel(self):
		self.close()

	def ok(self):
		config.subtitles.save()
		self.close()
