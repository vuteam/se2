from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.InputBox import InputBox
from Screens.Standby import *
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Screens.HelpMenu import HelpableScreen
from Components.Console import Console
from Components.Network import iNetwork
from Components.Sources.StaticText import StaticText
from Components.Sources.Boolean import Boolean
from Components.Sources.List import List
from Components.SystemInfo import SystemInfo
from Components.Label import Label, MultiColorLabel
from Components.ScrollLabel import ScrollLabel
from Components.Pixmap import Pixmap, MultiPixmap
from Components.MenuList import MenuList
from Components.config import config, ConfigYesNo, ConfigIP, NoSave, ConfigText, ConfigPassword, ConfigSelection, getConfigListEntry, ConfigNothing, ConfigBoolean, ConfigNumber
from Components.ConfigList import ConfigListScreen
from Components.PluginComponent import plugins
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest
from Components.ActionMap import ActionMap, NumberActionMap, HelpableActionMap
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS, SCOPE_CURRENT_SKIN
from Tools.LoadPixmap import LoadPixmap
from Plugins.Plugin import PluginDescriptor
from enigma import eTimer, ePoint, eSize, RT_HALIGN_LEFT, eListboxPythonMultiContent, gFont
from boxbranding import getBoxType, getMachineBrand, getMachineName
from os import remove, symlink, unlink, rename, chmod
from re import compile as re_compile, search as re_search
import time
import os

basegroup = "packagegroup-base"

def getSSID(ssid_value):
	file = '/etc/wifis/'+ssid_value+'.wifi'
	if fileExists(file):
		f=open(file,'r')
		line = f.readlines()
		f.close()
		hiddenessid = line[0].replace("\n","")
		encryption = line[2].replace("\n","")
		wepkeytype = line[3].replace("\n","")
		psk = line[4].replace("\n","")
	else:
		hiddenessid = encryption = wepkeytype = psk = None

	return hiddenessid,encryption,wepkeytype,psk


class NetworkAdapterSelection(Screen, HelpableScreen):
	def __init__(self, session):
		Screen.__init__(self, session)
		HelpableScreen.__init__(self)
		#Screen.setTitle(self, _("Network Setup"))

		self.wlan_errortext = _("No working wireless network adapter found.\nPlease verify that you have attached a compatible WLAN device and your network is configured correctly.")
		self.lan_errortext = _("No working local network adapter found.\nPlease verify that you have attached a network cable and your network is configured correctly.")
		self.oktext = _("Press OK on your remote control to continue.")
		self.edittext = _("Press OK to edit the settings.")
		self.defaulttext = _("Press yellow to set this interface as default interface.")
		self.restartLanRef = None

		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("Select"))
		self["key_yellow"] = StaticText("")
		self["key_blue"] = StaticText("")
		self["introduction"] = StaticText(self.edittext)

		self["OkCancelActions"] = HelpableActionMap(self, "OkCancelActions",
			{
			"cancel": (self.close, _("Exit network interface list")),
			"ok": (self.okbuttonClick, _("Select interface")),
			})

		self["ColorActions"] = HelpableActionMap(self, "ColorActions",
			{
			"red": (self.close, _("Exit network interface list")),
			"green": (self.okbuttonClick, _("Select interface")),
			"blue": (self.openNetworkWizard, _("Use the network wizard to configure selected network adapter")),
			})

		self["DefaultInterfaceAction"] = HelpableActionMap(self, "ColorActions",
			{
			"yellow": (self.setDefaultInterface, [_("Set interface as default Interface"),_("* Only available if more than one interface is active.")] ),
			})

		self.adapters = [(iNetwork.getFriendlyAdapterName(x),x) for x in iNetwork.getAdapterList()]

		if not self.adapters:
			self.adapters = [(iNetwork.getFriendlyAdapterName(x),x) for x in iNetwork.getConfiguredAdapters()]

		if len(self.adapters) == 0:
			self.adapters = [(iNetwork.getFriendlyAdapterName(x),x) for x in iNetwork.getInstalledAdapters()]

		self.onChangedEntry = [ ]
		self.list = []
		self["list"] = List(self.list)
		self.updateList()
		if not self.selectionChanged in self["list"].onSelectionChanged:
			self["list"].onSelectionChanged.append(self.selectionChanged)

		if len(self.adapters) == 1:
			self.onFirstExecBegin.append(self.okbuttonClick)
		self.onClose.append(self.cleanup)

	def createSummary(self):
		from Screens.PluginBrowser import PluginBrowserSummary
		return PluginBrowserSummary

	def selectionChanged(self):
		item = self["list"].getCurrent()
		if item:
			name = item[0]
			desc = item[1]
		else:
			name = ""
			desc = ""
		for cb in self.onChangedEntry:
			cb(name, desc)

	def buildInterfaceList(self,iface,name,default,active ):
		divpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/div-h.png"))
		defaultpng = None
		activepng = None
		description = None
		interfacepng = None

		if not iNetwork.isWirelessInterface(iface):
			if active is True:
				interfacepng = LoadPixmap(resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/icons/network_wired-active.png"))
			elif active is False:
				interfacepng = LoadPixmap(resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/icons/network_wired-inactive.png"))
			else:
				interfacepng = LoadPixmap(resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/icons/network_wired.png"))
		elif iNetwork.isWirelessInterface(iface):
			if active is True:
				interfacepng = LoadPixmap(resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/icons/network_wireless-active.png"))
			elif active is False:
				interfacepng = LoadPixmap(resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/icons/network_wireless-inactive.png"))
			else:
				interfacepng = LoadPixmap(resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/icons/network_wireless.png"))

		num_configured_if = len(iNetwork.getConfiguredAdapters())
		if num_configured_if >= 2:
			if default is True:
				defaultpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/buttons/button_blue.png"))
			elif default is False:
				defaultpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/buttons/button_blue_off.png"))
		if active is True:
			activepng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/icons/lock_on.png"))
		elif active is False:
			activepng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, "skin_default/icons/lock_error.png"))

		description = iNetwork.getFriendlyAdapterDescription(iface)

		return((iface, name, description, interfacepng, defaultpng, activepng, divpng))	

	def updateList(self):
		self.list = []
		default_gw = None
		num_configured_if = len(iNetwork.getConfiguredAdapters())
		if num_configured_if >= 2:
			self["key_yellow"].setText(_("Default"))
			self["introduction"].setText(self.defaulttext)
			self["DefaultInterfaceAction"].setEnabled(True)
		else:
			self["key_yellow"].setText("")
			self["introduction"].setText(self.edittext)
			self["DefaultInterfaceAction"].setEnabled(False)

		if num_configured_if < 2 and fileExists("/etc/default_gw"):
			unlink("/etc/default_gw")

		if fileExists("/etc/default_gw"):
			fp = file('/etc/default_gw', 'r')
			result = fp.read()
			fp.close()
			default_gw = result

		for x in self.adapters:
			if x[1] == default_gw:
				default_int = True
			else:
				default_int = False
			if iNetwork.getAdapterAttribute(x[1], 'up') is True:
				active_int = True
			else:
				active_int = False
			self.list.append(self.buildInterfaceList(x[1],_(x[0]),default_int,active_int ))

		if fileExists(resolveFilename(SCOPE_PLUGINS, "SystemPlugins/NetworkWizard/networkwizard.xml")):
			self["key_blue"].setText(_("Network wizard"))
		self["list"].setList(self.list)

	def setDefaultInterface(self):
		selection = self["list"].getCurrent()
		num_if = len(self.list)
		old_default_gw = None
		num_configured_if = len(iNetwork.getConfiguredAdapters())
		if fileExists("/etc/default_gw"):
			fp = open('/etc/default_gw', 'r')
			old_default_gw = fp.read()
			fp.close()
		if num_configured_if > 1 and (not old_default_gw or old_default_gw != selection[0]):
			fp = open('/etc/default_gw', 'w+')
			fp.write(selection[0])
			fp.close()
			self.restartLan()
		elif old_default_gw and num_configured_if < 2:
			unlink("/etc/default_gw")
			self.restartLan()

	def okbuttonClick(self):
		selection = self["list"].getCurrent()
		if selection is not None:
			self.session.openWithCallback(self.AdapterSetupClosed, AdapterSetupConfiguration, selection[0])

	def AdapterSetupClosed(self, *ret):
		if len(self.adapters) == 1:
			self.close()
		else:
			self.updateList()

	def cleanup(self):
		iNetwork.stopLinkStateConsole()
		iNetwork.stopRestartConsole()
		iNetwork.stopGetInterfacesConsole()

	def restartLan(self):
		iNetwork.restartNetwork(self.restartLanDataAvail)
		self.restartLanRef = self.session.openWithCallback(self.restartfinishedCB, MessageBox, _("Please wait while we configure your network..."), type = MessageBox.TYPE_INFO, enable_input = False)

	def restartLanDataAvail(self, data):
		if data is True:
			iNetwork.getInterfaces(self.getInterfacesDataAvail)

	def getInterfacesDataAvail(self, data):
		if data is True:
			self.restartLanRef.close(True)

	def restartfinishedCB(self, data):
		if data is True:
			self.updateList()
			self.session.open(MessageBox, _("Finished configuring your network"), type = MessageBox.TYPE_INFO, timeout = 10, default = False)

	def openNetworkWizard(self):
		if fileExists(resolveFilename(SCOPE_PLUGINS, "SystemPlugins/NetworkWizard/networkwizard.xml")):
			try:
				from Plugins.SystemPlugins.NetworkWizard.NetworkWizard import NetworkWizard
			except ImportError:
				self.session.open(MessageBox, _("The network wizard extension is not installed!\nPlease install it."), type = MessageBox.TYPE_INFO,timeout = 10 )
			else:
				selection = self["list"].getCurrent()
				if selection is not None:
					self.session.openWithCallback(self.AdapterSetupClosed, NetworkWizard, selection[0])


class NameserverSetup(Screen, ConfigListScreen, HelpableScreen):
	def __init__(self, session):
		Screen.__init__(self, session)
		HelpableScreen.__init__(self)
		#Screen.setTitle(self, _("Nameserver settings"))
		self.backupNameserverList = iNetwork.getNameserverList()[:]
		print "backup-list:", self.backupNameserverList

		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Save"))
		self["key_yellow"] = StaticText(_("Add"))
		self["key_blue"] = StaticText(_("Delete"))

		self["introduction"] = StaticText(_("Press OK to activate the settings."))
		self.createConfig()

		self["OkCancelActions"] = HelpableActionMap(self, "OkCancelActions",
			{
			"cancel": (self.cancel, _("Exit nameserver configuration")),
			"ok": (self.ok, _("Activate current configuration")),
			})

		self["ColorActions"] = HelpableActionMap(self, "ColorActions",
			{
			"red": (self.cancel, _("Exit nameserver configuration")),
			"green": (self.ok, _("Activate current configuration")),
			"yellow": (self.add, _("Add a nameserver entry")),
			"blue": (self.remove, _("Remove a nameserver entry")),
			})

		self["actions"] = NumberActionMap(["SetupActions"],
		{
			"ok": self.ok,
		}, -2)

		self.list = []
		ConfigListScreen.__init__(self, self.list)
		self.createSetup()

	def createConfig(self):
		self.nameservers = iNetwork.getNameserverList()
		self.nameserverEntries = [ NoSave(ConfigIP(default=nameserver)) for nameserver in self.nameservers]

	def createSetup(self):
		self.list = []

		i = 1
		for x in self.nameserverEntries:
			self.list.append(getConfigListEntry(_("Nameserver %d") % i, x))
			i += 1

		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def ok(self):
		iNetwork.clearNameservers()
		for nameserver in self.nameserverEntries:
			iNetwork.addNameserver(nameserver.getValue())
		iNetwork.writeNameserverConfig()
		self.close()

	def run(self):
		self.ok()

	def cancel(self):
		iNetwork.clearNameservers()
		print "backup-list:", self.backupNameserverList
		for nameserver in self.backupNameserverList:
			iNetwork.addNameserver(nameserver)
		self.close()

	def add(self):
		iNetwork.addNameserver([0, 0, 0, 0])
		self.createConfig()
		self.createSetup()

	def remove(self):
		print "currentIndex:", self["config"].getCurrentIndex()
		index = self["config"].getCurrentIndex()
		if index < len(self.nameservers):
			iNetwork.removeNameserver(self.nameservers[index])
			self.createConfig()
			self.createSetup()

class AdapterSetup(Screen, ConfigListScreen, HelpableScreen):
	def __init__(self, session, networkinfo, essid=None):
		Screen.__init__(self, session)
		HelpableScreen.__init__(self)
		#Screen.setTitle(self, _("Adapter settings"))
		self.session = session
		if isinstance(networkinfo, (list, tuple)):
			self.iface = networkinfo[0]
			self.essid = networkinfo[1]
		else:
			self.iface = networkinfo
			self.essid = essid

		self.extended = None
		self.applyConfigRef = None
		self.finished_cb = None
		self.oktext = _("Press OK on your remote control to continue.")
		self.oldInterfaceState = iNetwork.getAdapterAttribute(self.iface, "up")

		self.newssid = False
		if iNetwork.isWirelessInterface(self.iface):
			from Plugins.SystemPlugins.WirelessLan.Wlan import wpaSupplicant
			self.ws = wpaSupplicant()
			self.wsconfig = self.ws.loadConfig(self.iface)
			if essid:
				if essid != self.wsconfig['ssid']:
					self.newssid = True
		self.timer = eTimer()
		self.timer.timeout.get().append(self.getSSID)
		self.first = True


		self.createConfig()

		self["OkCancelActions"] = HelpableActionMap(self, "OkCancelActions",
			{
			"cancel": (self.keyCancel, _("exit network adapter configuration")),
			"ok": (self.keySave, _("activate network adapter configuration")),
			})

		self["ColorActions"] = HelpableActionMap(self, "ColorActions",
			{
			"red": (self.keyCancel, _("exit network adapter configuration")),
			"green": (self.keySave, _("activate network adapter configuration")),
			"blue": (self.KeyBlue, _("open nameserver configuration")),
			})

		self["actions"] = NumberActionMap(["SetupActions"],
		{
			"ok": self.keySave,
		}, -2)

		self.list = []
		ConfigListScreen.__init__(self, self.list,session = self.session)
		self.createSetup()
		self.onLayoutFinish.append(self.layoutFinished)
		self.onClose.append(self.cleanup)

		self["DNS1text"] = StaticText(_("Primary DNS"))
		self["DNS2text"] = StaticText(_("Secondary DNS"))
		self["DNS1"] = StaticText()
		self["DNS2"] = StaticText()
		self["introduction"] = StaticText(_("Current settings:"))

		self["IPtext"] = StaticText(_("IP address"))
		self["Netmasktext"] = StaticText(_("Netmask"))
		self["Gatewaytext"] = StaticText(_("Gateway"))

		self["IP"] = StaticText()
		self["Mask"] = StaticText()
		self["Gateway"] = StaticText()

		self["Adaptertext"] = StaticText(_("Network:"))
		self["Adapter"] = StaticText()
		self["introduction2"] = StaticText(_("Press OK to activate the settings."))
		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Save"))
		self["key_blue"] = StaticText(_("Edit DNS"))

		self["VKeyIcon"] = Boolean(False)
		self["HelpWindow"] = Pixmap()
		self["HelpWindow"].hide()

	def layoutFinished(self):
		self["DNS1"].setText(self.primaryDNS.getText())
		self["DNS2"].setText(self.secondaryDNS.getText())
		if self.ipConfigEntry.getText() is not None:
			if self.ipConfigEntry.getText() == "0.0.0.0":
				self["IP"].setText(_("N/A"))
			else:
				self["IP"].setText(self.ipConfigEntry.getText())
		else:
			self["IP"].setText(_("N/A"))
		if self.netmaskConfigEntry.getText() is not None:
			if self.netmaskConfigEntry.getText() == "0.0.0.0":
				self["Mask"].setText(_("N/A"))
			else:
				self["Mask"].setText(self.netmaskConfigEntry.getText())
		else:
			self["IP"].setText(_("N/A"))
		if iNetwork.getAdapterAttribute(self.iface, "gateway"):
			if self.gatewayConfigEntry.getText() == "0.0.0.0":
				self["Gatewaytext"].setText(_("Gateway"))
				self["Gateway"].setText(_("N/A"))
			else:
				self["Gatewaytext"].setText(_("Gateway"))
				self["Gateway"].setText(self.gatewayConfigEntry.getText())
		else:
			self["Gateway"].setText("")
			self["Gatewaytext"].setText("")
		self["Adapter"].setText(iNetwork.getFriendlyAdapterName(self.iface))
	
	def SaveAP(self):
		if not os.path.exists('/etc/wifis'):
			os.system('mkdir /etc/wifis')
		self.updateSSID()
		
	def updateSSID(self):
		wifis = '/etc/wifis/' + config.plugins.wlan.essid.value + '.wifi'
		lista = [config.plugins.wlan.hiddenessid.value, config.plugins.wlan.essid.value, config.plugins.wlan.encryption.value, config.plugins.wlan.wepkeytype.value, config.plugins.wlan.psk.value]
		info = '\n#Line 1 : Hidden network?\n#Line 2 : Network name\n#Line 3 : Encryption type\n#Line 4 : WEP type\n#Line 5 : Wifi password'
		g=open(wifis, 'w')
		for x in lista:
			g.writelines(str(x)+'\n')
		g.write(info)
		g.close()

	def getSSID(self):
		self.timer.stop()
		if self.newssid:
			ssid_value = config.plugins.wlan.essid.value
			hiddenessid,encryption,wepkeytype,psk = getSSID(ssid_value)
			if wepkeytype:
				config.plugins.wlan.encryption.setValue(encryption)
				config.plugins.wlan.wepkeytype.setValue(wepkeytype)
				config.plugins.wlan.psk.setValue(psk)
				if self.activateInterfaceEntry.getValue():
					self.applyConfig(True)

	def createConfig(self):
		self.InterfaceEntry = None
		self.dhcpEntry = None
		self.gatewayEntry = None
		self.hiddenSSID = None
		self.wlanSSID = None
		self.encryption = None
		self.encryptionType = None
		self.encryptionKey = None
		self.encryptionlist = None
		self.weplist = None
		self.wsconfig = None
		self.default = None

		if iNetwork.isWirelessInterface(self.iface):
			from Plugins.SystemPlugins.WirelessLan.Wlan import wpaSupplicant
			self.ws = wpaSupplicant()
			self.encryptionlist = []
			self.encryptionlist.append(("Unencrypted", _("Unencrypted")))
			self.encryptionlist.append(("WEP", _("WEP")))
			self.encryptionlist.append(("WPA", _("WPA")))
			self.encryptionlist.append(("WPA/WPA2", _("WPA or WPA2")))
			self.encryptionlist.append(("WPA2", _("WPA2")))
			self.weplist = []
			self.weplist.append("ASCII")
			self.weplist.append("HEX")

			self.wsconfig = self.ws.loadConfig(self.iface)
			if self.essid is None:
				self.essid = self.wsconfig['ssid']

			config.plugins.wlan.hiddenessid = NoSave(ConfigYesNo(default = self.wsconfig['hiddenessid']))
			config.plugins.wlan.essid = NoSave(ConfigText(default = self.essid, visible_width = 50, fixed_size = False))
			config.plugins.wlan.encryption = NoSave(ConfigSelection(self.encryptionlist, default = self.wsconfig['encryption'] ))
			config.plugins.wlan.wepkeytype = NoSave(ConfigSelection(self.weplist, default = self.wsconfig['wepkeytype'] ))
			config.plugins.wlan.psk = NoSave(ConfigPassword(default = self.wsconfig['key'], visible_width = 50, fixed_size = False))

		self.activateInterfaceEntry = NoSave(ConfigYesNo(default=iNetwork.getAdapterAttribute(self.iface, "up") or False))
		self.dhcpConfigEntry = NoSave(ConfigYesNo(default=iNetwork.getAdapterAttribute(self.iface, "dhcp") or False))
		self.ipConfigEntry = NoSave(ConfigIP(default=iNetwork.getAdapterAttribute(self.iface, "ip")) or [0,0,0,0])
		self.netmaskConfigEntry = NoSave(ConfigIP(default=iNetwork.getAdapterAttribute(self.iface, "netmask") or [255,0,0,0]))
		if iNetwork.getAdapterAttribute(self.iface, "gateway"):
			self.dhcpdefault = True
		else:
			self.dhcpdefault = False
		self.hasGatewayConfigEntry = NoSave(ConfigYesNo(default=self.dhcpdefault or False))
		self.gatewayConfigEntry = NoSave(ConfigIP(default=iNetwork.getAdapterAttribute(self.iface, "gateway") or [0,0,0,0]))
		nameserver = (iNetwork.getNameserverList() + [[0,0,0,0]] * 2)[0:2]
		self.primaryDNS = NoSave(ConfigIP(default=nameserver[0]))
		self.secondaryDNS = NoSave(ConfigIP(default=nameserver[1]))

	def createSetup(self):
		if SystemInfo["WakeOnLAN"]:
			self.wolstartvalue = config.network.wol.value
		self.list = []
		self.InterfaceEntry = getConfigListEntry(_("Use interface"), self.activateInterfaceEntry)

		self.list.append(self.InterfaceEntry)
		if self.activateInterfaceEntry.getValue():
			self.dhcpEntry = getConfigListEntry(_("Use DHCP"), self.dhcpConfigEntry)
			self.list.append(self.dhcpEntry)
			if not self.dhcpConfigEntry.getValue():
				self.list.append(getConfigListEntry(_('IP address'), self.ipConfigEntry))
				self.list.append(getConfigListEntry(_('Netmask'), self.netmaskConfigEntry))
				self.gatewayEntry = getConfigListEntry(_('Use a gateway'), self.hasGatewayConfigEntry)
				self.list.append(self.gatewayEntry)
				if self.hasGatewayConfigEntry.getValue():
					self.list.append(getConfigListEntry(_('Gateway'), self.gatewayConfigEntry))
			havewol = False
			if SystemInfo["WakeOnLAN"] and not getBoxType() in ('et10000', 'gb800seplus', 'gb800ueplus', 'gbultrase', 'gbultraue', 'gbipbox', 'gbquad', 'gbx1', 'gbx3'):
				havewol = True
			if getBoxType() == 'et10000' and self.iface == 'eth0':
				havewol = False
			if havewol:
				self.list.append(getConfigListEntry(_('Enable Wake On LAN'), config.network.wol))

			self.extended = None
			self.configStrings = None
			for p in plugins.getPlugins(PluginDescriptor.WHERE_NETWORKSETUP):
				callFnc = p.__call__["ifaceSupported"](self.iface)
				if callFnc is not None:
					if p.__call__.has_key("WlanPluginEntry"): # internally used only for WLAN Plugin
						self.extended = callFnc
						if p.__call__.has_key("configStrings"):
							self.configStrings = p.__call__["configStrings"]

						self.hiddenSSID = getConfigListEntry(_("Hidden network"), config.plugins.wlan.hiddenessid)
						self.list.append(self.hiddenSSID)
						self.wlanSSID = getConfigListEntry(_("Network name (SSID)"), config.plugins.wlan.essid)
						self.list.append(self.wlanSSID)
						self.encryption = getConfigListEntry(_("Encryption"), config.plugins.wlan.encryption)
						self.list.append(self.encryption)

						self.encryptionType = getConfigListEntry(_("Encryption key type"), config.plugins.wlan.wepkeytype)
						self.encryptionKey = getConfigListEntry(_("Encryption key"), config.plugins.wlan.psk)

						if config.plugins.wlan.encryption.getValue() != "Unencrypted":
							if config.plugins.wlan.encryption.getValue() == 'WEP':
								self.list.append(self.encryptionType)
							self.list.append(self.encryptionKey)
		self["config"].list = self.list
		self["config"].l.setList(self.list)
		if self.first:
			self.first = False
			self.timer.start(500, True)


	def KeyBlue(self):
		self.session.openWithCallback(self.NameserverSetupClosed, NameserverSetup)

	def newConfig(self):
		if self["config"].getCurrent() == self.InterfaceEntry:
			self.createSetup()
		if self["config"].getCurrent() == self.dhcpEntry:
			self.createSetup()
		if self["config"].getCurrent() == self.gatewayEntry:
			self.createSetup()
		if iNetwork.isWirelessInterface(self.iface):
			if self["config"].getCurrent() == self.encryption:
				self.createSetup()

	def keyLeft(self):
		ConfigListScreen.keyLeft(self)
		self.newConfig()

	def keyRight(self):
		ConfigListScreen.keyRight(self)
		self.newConfig()

	def keySave(self):
		self.hideInputHelp()
		if self["config"].isChanged() or (SystemInfo["WakeOnLAN"] and self.wolstartvalue != config.network.wol.value) or self.newssid:
			self.session.openWithCallback(self.keySaveConfirm, MessageBox, (_("Are you sure you want to activate this network configuration?\n\n") + self.oktext ) )
		else:
			if self.finished_cb:
				self.finished_cb()
			else:
				self.close('cancel')
		config.network.save()

	def keySaveConfirm(self, ret = False):
		if ret == True:
			num_configured_if = len(iNetwork.getConfiguredAdapters())
			if num_configured_if >= 1:
				if self.iface in iNetwork.getConfiguredAdapters():
					self.applyConfig(True)
				else:
					self.session.openWithCallback(self.secondIfaceFoundCB, MessageBox, _("A second configured interface has been found.\n\nDo you want to disable the second network interface?"), default = True)
			else:
				self.applyConfig(True)
		else:
			self.keyCancel()

	def secondIfaceFoundCB(self, data):
		if data is False:
			self.applyConfig(True)
		else:
			configuredInterfaces = iNetwork.getConfiguredAdapters()
			for interface in configuredInterfaces:
				if interface == self.iface:
					continue
				iNetwork.setAdapterAttribute(interface, "up", False)
			iNetwork.deactivateInterface(configuredInterfaces,self.deactivateSecondInterfaceCB)

	def deactivateSecondInterfaceCB(self, data):
		if data is True:
			self.applyConfig(True)

	def applyConfig(self, ret = False):
		if ret == True:
			self.applyConfigRef = None
			iNetwork.setAdapterAttribute(self.iface, "up", self.activateInterfaceEntry.getValue())
			iNetwork.setAdapterAttribute(self.iface, "dhcp", self.dhcpConfigEntry.getValue())
			iNetwork.setAdapterAttribute(self.iface, "ip", self.ipConfigEntry.getValue())
			iNetwork.setAdapterAttribute(self.iface, "netmask", self.netmaskConfigEntry.getValue())
			if self.hasGatewayConfigEntry.getValue():
				iNetwork.setAdapterAttribute(self.iface, "gateway", self.gatewayConfigEntry.getValue())
			else:
				iNetwork.removeAdapterAttribute(self.iface, "gateway")

			if self.extended is not None and self.configStrings is not None:
				iNetwork.setAdapterAttribute(self.iface, "configStrings", self.configStrings(self.iface))
				self.ws.writeConfig(self.iface)

			if self.activateInterfaceEntry.getValue() is False:
				iNetwork.deactivateInterface(self.iface,self.deactivateInterfaceCB)
				iNetwork.writeNetworkConfig()
				self.applyConfigRef = self.session.openWithCallback(self.applyConfigfinishedCB, MessageBox, _("Please wait for activation of your network configuration..."), type = MessageBox.TYPE_INFO, enable_input = False)
			else:
				if self.oldInterfaceState is False:
					iNetwork.activateInterface(self.iface,self.deactivateInterfaceCB)
				else:
					iNetwork.deactivateInterface(self.iface,self.activateInterfaceCB)
				iNetwork.writeNetworkConfig()
				self.applyConfigRef = self.session.openWithCallback(self.applyConfigfinishedCB, MessageBox, _("Please wait for activation of your network configuration..."), type = MessageBox.TYPE_INFO, enable_input = False)
		else:
			self.keyCancel()

	def deactivateInterfaceCB(self, data):
		if data is True:
			self.applyConfigDataAvail(True)

	def activateInterfaceCB(self, data):
		if data is True:
			iNetwork.activateInterface(self.iface,self.applyConfigDataAvail)

	def applyConfigDataAvail(self, data):
		if data is True:
			iNetwork.getInterfaces(self.getInterfacesDataAvail)

	def getInterfacesDataAvail(self, data):
		if data is True:
			self.applyConfigRef.close(True)

	def applyConfigfinishedCB(self,data):
		if data is True:
			if self.finished_cb:
				self.session.openWithCallback(lambda x : self.finished_cb(), MessageBox, _("Your network configuration has been activated."), type = MessageBox.TYPE_INFO, timeout = 10)
			else:
				self.session.openWithCallback(self.ConfigfinishedCB, MessageBox, _("Your network configuration has been activated."), type = MessageBox.TYPE_INFO, timeout = 10)

	def ConfigfinishedCB(self,data):
		if data is not None:
			if data is True:
				if iNetwork.isWirelessInterface(self.iface):
					try:
						from Plugins.SystemPlugins.WirelessLan.Wlan import iStatus
					except:
						self.close('ok')
					else:
						iStatus.getDataForInterface(self.iface,self.getInfoCB)
				else:
					self.close('ok')

	def getInfoCB(self,data,status):
		if data is not None:
			if data is True:
				if status is not None:
					if status[self.iface]["essid"] == "off" or status[self.iface]["accesspoint"] == "Not-Associated" or status[self.iface]["accesspoint"] == False:
						pass
					else:
						self.SaveAP()
		self.close('ok')


	def keyCancelConfirm(self, result):
		if not result:
			return
		if SystemInfo["WakeOnLAN"]:
			config.network.wol.setValue(self.wolstartvalue)	
		if self.oldInterfaceState is False:
			iNetwork.deactivateInterface(self.iface,self.keyCancelCB)
		else:
			self.close('cancel')

	def keyCancel(self):
		self.hideInputHelp()
		if self["config"].isChanged() or (SystemInfo["WakeOnLAN"] and self.wolstartvalue != config.network.wol.value):
			self.session.openWithCallback(self.keyCancelConfirm, MessageBox, _("Really close without saving settings?"))
		else:
			self.close('cancel')

	def keyCancelCB(self,data):
		if data is not None:
			if data is True:
				self.close('cancel')

	def runAsync(self, finished_cb):
		self.finished_cb = finished_cb
		self.keySave()

	def NameserverSetupClosed(self, *ret):
		iNetwork.loadNameserverConfig()
		nameserver = (iNetwork.getNameserverList() + [[0,0,0,0]] * 2)[0:2]
		self.primaryDNS = NoSave(ConfigIP(default=nameserver[0]))
		self.secondaryDNS = NoSave(ConfigIP(default=nameserver[1]))
		self.createSetup()
		self.layoutFinished()

	def cleanup(self):
		iNetwork.stopLinkStateConsole()

	def hideInputHelp(self):
		current = self["config"].getCurrent()
		if current == self.wlanSSID:
			if current[1].help_window.instance is not None:
				current[1].help_window.instance.hide()
		elif current == self.encryptionKey and config.plugins.wlan.encryption.getValue() is not "Unencrypted":
			if current[1].help_window.instance is not None:
				current[1].help_window.instance.hide()


class AdapterSetupConfiguration(Screen, HelpableScreen):
	def __init__(self, session,iface):
		Screen.__init__(self, session)
		HelpableScreen.__init__(self)
		#Screen.setTitle(self, _("Network Setup"))
		self.session = session
		self.iface = iface
		self.restartLanRef = None
		self.LinkState = None
		self.onChangedEntry = [ ]
		self.mainmenu = ""
		self["menulist"] = MenuList(self.mainmenu)
		self["key_red"] = StaticText(_("Close"))
		self["description"] = StaticText()
		self["IFtext"] = StaticText()
		self["IF"] = StaticText()
		self["Statustext"] = StaticText()
		self["statuspic"] = MultiPixmap()
		self["statuspic"].hide()

		self.oktext = _("Press OK on your remote control to continue.")
		self.reboottext = _("Your receiver will restart after pressing OK on your remote control.")
		self.errortext = _("No working wireless network interface found.\n Please verify that you have attached a compatible WLAN device or enable your local network interface.")
		self.missingwlanplugintxt = _("The wireless LAN plugin is not installed!\nPlease install it.")

		self["WizardActions"] = HelpableActionMap(self, "WizardActions",
			{
			"up": (self.up, _("move up to previous entry")),
			"down": (self.down, _("move down to next entry")),
			"left": (self.left, _("move up to first entry")),
			"right": (self.right, _("move down to last entry")),
			})

		self["OkCancelActions"] = HelpableActionMap(self, "OkCancelActions",
			{
			"cancel": (self.close, _("exit networkadapter setup menu")),
			"ok": (self.ok, _("select menu entry")),
			})

		self["ColorActions"] = HelpableActionMap(self, "ColorActions",
			{
			"red": (self.close, _("exit networkadapter setup menu")),
			})

		self["actions"] = NumberActionMap(["WizardActions","ShortcutActions"],
		{
			"ok": self.ok,
			"back": self.close,
			"up": self.up,
			"down": self.down,
			"red": self.close,
			"left": self.left,
			"right": self.right,
		}, -2)

		self.updateStatusbar()
		self.onClose.append(self.cleanup)
		if not self.selectionChanged in self["menulist"].onSelectionChanged:
			self["menulist"].onSelectionChanged.append(self.selectionChanged)
		self.selectionChanged()

	def queryWirelessDevice(self,iface):
		try:
			from pythonwifi.iwlibs import Wireless
			import errno
		except ImportError:
			return False
		else:
			try:
				ifobj = Wireless(iface) # a Wireless NIC Object
				wlanresponse = ifobj.getAPaddr()
			except IOError, (error_no, error_str):
				if error_no in (errno.EOPNOTSUPP, errno.ENODEV, errno.EPERM):
					return False
				else:
					print "error: ",error_no,error_str
					return True
			else:
				return True

	def ok(self):
		self.cleanup()
		if self["menulist"].getCurrent()[1] == 'edit':
			if iNetwork.isWirelessInterface(self.iface):
				try:
					from Plugins.SystemPlugins.WirelessLan.plugin import WlanScan
				except ImportError:
					self.session.open(MessageBox, self.missingwlanplugintxt, type = MessageBox.TYPE_INFO,timeout = 10 )
				else:
					if self.queryWirelessDevice(self.iface):
						self.session.openWithCallback(self.AdapterSetupClosed, AdapterSetup,self.iface)
					else:
						self.showErrorMessage()	# Display Wlan not available Message
			else:
				self.session.openWithCallback(self.AdapterSetupClosed, AdapterSetup,self.iface)
		if self["menulist"].getCurrent()[1] == 'test':
			self.session.open(NetworkAdapterTest,self.iface)
		if self["menulist"].getCurrent()[1] == 'dns':
			self.session.open(NameserverSetup)
		if self["menulist"].getCurrent()[1] == 'scanwlan':
			try:
				from Plugins.SystemPlugins.WirelessLan.plugin import WlanScan
			except ImportError:
				self.session.open(MessageBox, self.missingwlanplugintxt, type = MessageBox.TYPE_INFO,timeout = 10 )
			else:
				if self.queryWirelessDevice(self.iface):
					self.session.openWithCallback(self.WlanScanClosed, WlanScan, self.iface)
				else:
					self.showErrorMessage()	# Display Wlan not available Message
		if self["menulist"].getCurrent()[1] == 'wlanstatus':
			try:
				from Plugins.SystemPlugins.WirelessLan.plugin import WlanStatus
			except ImportError:
				self.session.open(MessageBox, self.missingwlanplugintxt, type = MessageBox.TYPE_INFO,timeout = 10 )
			else:
				if self.queryWirelessDevice(self.iface):
					self.session.openWithCallback(self.WlanStatusClosed, WlanStatus,self.iface)
				else:
					self.showErrorMessage()	# Display Wlan not available Message
		if self["menulist"].getCurrent()[1] == 'lanrestart':
			self.session.openWithCallback(self.restartLan, MessageBox, (_("Are you sure you want to restart your network interfaces?\n\n") + self.oktext ) )
		if self["menulist"].getCurrent()[1] == 'openwizard':
			from Plugins.SystemPlugins.NetworkWizard.NetworkWizard import NetworkWizard
			self.session.openWithCallback(self.AdapterSetupClosed, NetworkWizard, self.iface)
		if self["menulist"].getCurrent()[1][0] == 'extendedSetup':
			self.extended = self["menulist"].getCurrent()[1][2]
			self.extended(self.session, self.iface)

	def up(self):
		self["menulist"].up()

	def down(self):
		self["menulist"].down()

	def left(self):
		self["menulist"].pageUp()

	def right(self):
		self["menulist"].pageDown()

	def createSummary(self):
		from Screens.PluginBrowser import PluginBrowserSummary
		return PluginBrowserSummary

	def selectionChanged(self):
		if self["menulist"].getCurrent()[1] == 'edit':
			self["description"].setText(_("Edit the network configuration of your %s %s.\n" ) % (getMachineBrand(), getMachineName()) + self.oktext )
		if self["menulist"].getCurrent()[1] == 'test':
			self["description"].setText(_("Test the network configuration of your %s %s.\n" ) % (getMachineBrand(), getMachineName()) + self.oktext )
		if self["menulist"].getCurrent()[1] == 'dns':
			self["description"].setText(_("Edit the Nameserver configuration of your %s %s.\n" ) % (getMachineBrand(), getMachineName()) + self.oktext )
		if self["menulist"].getCurrent()[1] == 'scanwlan':
			self["description"].setText(_("Scan your network for wireless access points and connect to them using your selected wireless device.\n" ) + self.oktext )
		if self["menulist"].getCurrent()[1] == 'wlanstatus':
			self["description"].setText(_("Shows the state of your wireless LAN connection.\n" ) + self.oktext )
		if self["menulist"].getCurrent()[1] == 'lanrestart':
			self["description"].setText(_("Restart your network connection and interfaces.\n" ) + self.oktext )
		if self["menulist"].getCurrent()[1] == 'openwizard':
			self["description"].setText(_("Use the network wizard to configure your Network\n" ) + self.oktext )
		if self["menulist"].getCurrent()[1][0] == 'extendedSetup':
			self["description"].setText(_(self["menulist"].getCurrent()[1][1]) + self.oktext )
		item = self["menulist"].getCurrent()
		if item:
			name = str(self["menulist"].getCurrent()[0])
			desc = self["description"].text
		else:
			name = ""
			desc = ""
		for cb in self.onChangedEntry:
			cb(name, desc)

	def updateStatusbar(self, data = None):
		self.mainmenu = self.genMainMenu()
		self["menulist"].l.setList(self.mainmenu)
		self["IFtext"].setText(_("Network:"))
		self["IF"].setText(iNetwork.getFriendlyAdapterName(self.iface))
		self["Statustext"].setText(_("Link:"))

		if iNetwork.isWirelessInterface(self.iface):
			try:
				from Plugins.SystemPlugins.WirelessLan.Wlan import iStatus
			except:
				self["statuspic"].setPixmapNum(1)
				self["statuspic"].show()
			else:
				iStatus.getDataForInterface(self.iface,self.getInfoCB)
		else:
			iNetwork.getLinkState(self.iface,self.dataAvail)

	def doNothing(self):
		pass

	def genMainMenu(self):
		menu = [(_("Adapter settings"), "edit"), (_("Nameserver settings"), "dns"), (_("Network test"), "test"), (_("Restart network"), "lanrestart")]

		self.extended = None
		self.extendedSetup = None
		for p in plugins.getPlugins(PluginDescriptor.WHERE_NETWORKSETUP):
			callFnc = p.__call__["ifaceSupported"](self.iface)
			if callFnc is not None:
				self.extended = callFnc
				if p.__call__.has_key("WlanPluginEntry"): # internally used only for WLAN Plugin
					menu.append((_("Scan wireless networks"), "scanwlan"))
					if iNetwork.getAdapterAttribute(self.iface, "up"):
						menu.append((_("Show WLAN status"), "wlanstatus"))
				else:
					if p.__call__.has_key("menuEntryName"):
						menuEntryName = p.__call__["menuEntryName"](self.iface)
					else:
						menuEntryName = _('Extended setup...')
					if p.__call__.has_key("menuEntryDescription"):
						menuEntryDescription = p.__call__["menuEntryDescription"](self.iface)
					else:
						menuEntryDescription = _('Extended network setup plugin...')
					self.extendedSetup = ('extendedSetup',menuEntryDescription, self.extended)
					menu.append((menuEntryName,self.extendedSetup))

		if fileExists(resolveFilename(SCOPE_PLUGINS, "SystemPlugins/NetworkWizard/networkwizard.xml")):
			menu.append((_("Network wizard"), "openwizard"))

		return menu

	def AdapterSetupClosed(self, *ret):
		if ret is not None and len(ret):
			if ret[0] == 'ok' and (iNetwork.isWirelessInterface(self.iface) and iNetwork.getAdapterAttribute(self.iface, "up") is True):
				try:
					from Plugins.SystemPlugins.WirelessLan.plugin import WlanStatus
				except ImportError:
					self.session.open(MessageBox, self.missingwlanplugintxt, type = MessageBox.TYPE_INFO,timeout = 10 )
				else:
					if self.queryWirelessDevice(self.iface):
						self.session.openWithCallback(self.WlanStatusClosed, WlanStatus,self.iface)
					else:
						self.showErrorMessage()	# Display Wlan not available Message
			else:
				self.updateStatusbar()
		else:
			self.updateStatusbar()

	def WlanStatusClosed(self, *ret):
		if ret is not None and len(ret):
			from Plugins.SystemPlugins.WirelessLan.Wlan import iStatus
			iStatus.stopWlanConsole()
			self.updateStatusbar()

	def WlanScanClosed(self,*ret):
		if ret[0] is not None:
			self.session.openWithCallback(self.AdapterSetupClosed, AdapterSetup, self.iface,ret[0])
		else:
			from Plugins.SystemPlugins.WirelessLan.Wlan import iStatus
			iStatus.stopWlanConsole()
			self.updateStatusbar()

	def restartLan(self, ret = False):
		if ret == True:
			iNetwork.restartNetwork(self.restartLanDataAvail)
			self.restartLanRef = self.session.openWithCallback(self.restartfinishedCB, MessageBox, _("Please wait while your network is restarting..."), type = MessageBox.TYPE_INFO, enable_input = False)

	def restartLanDataAvail(self, data):
		if data is True:
			iNetwork.getInterfaces(self.getInterfacesDataAvail)

	def getInterfacesDataAvail(self, data):
		if data is True:
			self.restartLanRef.close(True)

	def restartfinishedCB(self,data):
		if data is True:
			self.updateStatusbar()
			self.session.open(MessageBox, _("Finished restarting your network"), type = MessageBox.TYPE_INFO, timeout = 10, default = False)

	def dataAvail(self,data):
		self.LinkState = None
		for line in data.splitlines():
			line = line.strip()
			if 'Link detected:' in line:
				if "yes" in line:
					self.LinkState = True
				else:
					self.LinkState = False
		if self.LinkState:
			iNetwork.checkNetworkState(self.checkNetworkCB)
		else:
			self["statuspic"].setPixmapNum(1)
			self["statuspic"].show()

	def showErrorMessage(self):
		self.session.open(MessageBox, self.errortext, type = MessageBox.TYPE_INFO,timeout = 10 )

	def cleanup(self):
		iNetwork.stopLinkStateConsole()
		iNetwork.stopDeactivateInterfaceConsole()
		iNetwork.stopActivateInterfaceConsole()
		iNetwork.stopPingConsole()
		try:
			from Plugins.SystemPlugins.WirelessLan.Wlan import iStatus
		except ImportError:
			pass
		else:
			iStatus.stopWlanConsole()

	def getInfoCB(self,data,status):
		self.LinkState = None
		if data is not None:
			if data is True:
				if status is not None:
					if status[self.iface]["essid"] == "off" or status[self.iface]["accesspoint"] == "Not-Associated" or status[self.iface]["accesspoint"] == False:
						self.LinkState = False
						self["statuspic"].setPixmapNum(1)
						self["statuspic"].show()
					else:
						self.LinkState = True
						iNetwork.checkNetworkState(self.checkNetworkCB)

	def checkNetworkCB(self,data):
		if iNetwork.getAdapterAttribute(self.iface, "up") is True:
			if self.LinkState is True:
				if data <= 2:
					self["statuspic"].setPixmapNum(0)
				else:
					self["statuspic"].setPixmapNum(1)
				self["statuspic"].show()
			else:
				self["statuspic"].setPixmapNum(1)
				self["statuspic"].show()
		else:
			self["statuspic"].setPixmapNum(1)
			self["statuspic"].show()


class NetworkAdapterTest(Screen):
	def __init__(self, session,iface):
		Screen.__init__(self, session)
		#Screen.setTitle(self, _("Network Test"))
		self.iface = iface
		self.oldInterfaceState = iNetwork.getAdapterAttribute(self.iface, "up")
		self.setLabels()
		self.onClose.append(self.cleanup)
		self.onHide.append(self.cleanup)

		self["updown_actions"] = NumberActionMap(["WizardActions","ShortcutActions"],
		{
			"ok": self.KeyOK,
			"blue": self.KeyOK,
			"up": lambda: self.updownhandler('up'),
			"down": lambda: self.updownhandler('down'),
		}, -2)

		self["shortcuts"] = ActionMap(["ShortcutActions","WizardActions"],
		{
			"red": self.cancel,
			"back": self.cancel,
		}, -2)
		self["infoshortcuts"] = ActionMap(["ShortcutActions","WizardActions"],
		{
			"red": self.closeInfo,
			"back": self.closeInfo,
		}, -2)
		self["shortcutsgreen"] = ActionMap(["ShortcutActions"],
		{
			"green": self.KeyGreen,
		}, -2)
		self["shortcutsgreen_restart"] = ActionMap(["ShortcutActions"],
		{
			"green": self.KeyGreenRestart,
		}, -2)
		self["shortcutsyellow"] = ActionMap(["ShortcutActions"],
		{
			"yellow": self.KeyYellow,
		}, -2)

		self["shortcutsgreen_restart"].setEnabled(False)
		self["updown_actions"].setEnabled(False)
		self["infoshortcuts"].setEnabled(False)
		self.onClose.append(self.delTimer)
		self.onLayoutFinish.append(self.layoutFinished)
		self.steptimer = False
		self.nextstep = 0
		self.activebutton = 0
		self.nextStepTimer = eTimer()
		self.nextStepTimer.callback.append(self.nextStepTimerFire)

	def cancel(self):
		if self.oldInterfaceState is False:
			iNetwork.setAdapterAttribute(self.iface, "up", self.oldInterfaceState)
			iNetwork.deactivateInterface(self.iface)
		self.close()

	def closeInfo(self):
		self["shortcuts"].setEnabled(True)
		self["infoshortcuts"].setEnabled(False)
		self["InfoText"].hide()
		self["InfoTextBorder"].hide()
		self["key_red"].setText(_("Close"))

	def delTimer(self):
		del self.steptimer
		del self.nextStepTimer

	def nextStepTimerFire(self):
		self.nextStepTimer.stop()
		self.steptimer = False
		self.runTest()

	def updownhandler(self,direction):
		if direction == 'up':
			if self.activebutton >=2:
				self.activebutton -= 1
			else:
				self.activebutton = 6
			self.setActiveButton(self.activebutton)
		if direction == 'down':
			if self.activebutton <=5:
				self.activebutton += 1
			else:
				self.activebutton = 1
			self.setActiveButton(self.activebutton)

	def setActiveButton(self,button):
		if button == 1:
			self["EditSettingsButton"].setPixmapNum(0)
			self["EditSettings_Text"].setForegroundColorNum(0)
			self["NetworkInfo"].setPixmapNum(0)
			self["NetworkInfo_Text"].setForegroundColorNum(1)
			self["AdapterInfo"].setPixmapNum(1) 		  # active
			self["AdapterInfo_Text"].setForegroundColorNum(2) # active
		if button == 2:
			self["AdapterInfo_Text"].setForegroundColorNum(1)
			self["AdapterInfo"].setPixmapNum(0)
			self["DhcpInfo"].setPixmapNum(0)
			self["DhcpInfo_Text"].setForegroundColorNum(1)
			self["NetworkInfo"].setPixmapNum(1) 		  # active
			self["NetworkInfo_Text"].setForegroundColorNum(2) # active
		if button == 3:
			self["NetworkInfo"].setPixmapNum(0)
			self["NetworkInfo_Text"].setForegroundColorNum(1)
			self["IPInfo"].setPixmapNum(0)
			self["IPInfo_Text"].setForegroundColorNum(1)
			self["DhcpInfo"].setPixmapNum(1) 		  # active
			self["DhcpInfo_Text"].setForegroundColorNum(2) 	  # active
		if button == 4:
			self["DhcpInfo"].setPixmapNum(0)
			self["DhcpInfo_Text"].setForegroundColorNum(1)
			self["DNSInfo"].setPixmapNum(0)
			self["DNSInfo_Text"].setForegroundColorNum(1)
			self["IPInfo"].setPixmapNum(1)			# active
			self["IPInfo_Text"].setForegroundColorNum(2)	# active
		if button == 5:
			self["IPInfo"].setPixmapNum(0)
			self["IPInfo_Text"].setForegroundColorNum(1)
			self["EditSettingsButton"].setPixmapNum(0)
			self["EditSettings_Text"].setForegroundColorNum(0)
			self["DNSInfo"].setPixmapNum(1)			# active
			self["DNSInfo_Text"].setForegroundColorNum(2)	# active
		if button == 6:
			self["DNSInfo"].setPixmapNum(0)
			self["DNSInfo_Text"].setForegroundColorNum(1)
			self["EditSettingsButton"].setPixmapNum(1) 	   # active
			self["EditSettings_Text"].setForegroundColorNum(2) # active
			self["AdapterInfo"].setPixmapNum(0)
			self["AdapterInfo_Text"].setForegroundColorNum(1)

	def runTest(self):
		next = self.nextstep
		if next == 0:
			self.doStep1()
		elif next == 1:
			self.doStep2()
		elif next == 2:
			self.doStep3()
		elif next == 3:
			self.doStep4()
		elif next == 4:
			self.doStep5()
		elif next == 5:
			self.doStep6()
		self.nextstep += 1

	def doStep1(self):
		self.steptimer = True
		self.nextStepTimer.start(300)
		self["key_yellow"].setText(_("Stop test"))

	def doStep2(self):
		self["Adapter"].setText(iNetwork.getFriendlyAdapterName(self.iface))
		self["Adapter"].setForegroundColorNum(2)
		self["Adaptertext"].setForegroundColorNum(1)
		self["AdapterInfo_Text"].setForegroundColorNum(1)
		self["AdapterInfo_OK"].show()
		self.steptimer = True
		self.nextStepTimer.start(300)

	def doStep3(self):
		self["Networktext"].setForegroundColorNum(1)
		self["Network"].setText(_("Please wait..."))
		self.getLinkState(self.iface)
		self["NetworkInfo_Text"].setForegroundColorNum(1)
		self.steptimer = True
		self.nextStepTimer.start(1000)

	def doStep4(self):
		self["Dhcptext"].setForegroundColorNum(1)
		if iNetwork.getAdapterAttribute(self.iface, 'dhcp') is True:
			self["Dhcp"].setForegroundColorNum(2)
			self["Dhcp"].setText(_("enabled"))
			self["DhcpInfo_Check"].setPixmapNum(0)
		else:
			self["Dhcp"].setForegroundColorNum(1)
			self["Dhcp"].setText(_("disabled"))
			self["DhcpInfo_Check"].setPixmapNum(1)
		self["DhcpInfo_Check"].show()
		self["DhcpInfo_Text"].setForegroundColorNum(1)
		self.steptimer = True
		self.nextStepTimer.start(1000)

	def doStep5(self):
		self["IPtext"].setForegroundColorNum(1)
		self["IP"].setText(_("Please wait..."))
		iNetwork.checkNetworkState(self.NetworkStatedataAvail)

	def doStep6(self):
		self.steptimer = False
		self.nextStepTimer.stop()
		self["DNStext"].setForegroundColorNum(1)
		self["DNS"].setText(_("Please wait..."))
		iNetwork.checkDNSLookup(self.DNSLookupdataAvail)

	def KeyGreen(self):
		self["shortcutsgreen"].setEnabled(False)
		self["shortcutsyellow"].setEnabled(True)
		self["updown_actions"].setEnabled(False)
		self["key_yellow"].setText("")
		self["key_green"].setText("")
		self.steptimer = True
		self.nextStepTimer.start(1000)

	def KeyGreenRestart(self):
		self.nextstep = 0
		self.layoutFinished()
		self["Adapter"].setText("")
		self["Network"].setText("")
		self["Dhcp"].setText("")
		self["IP"].setText("")
		self["DNS"].setText("")
		self["AdapterInfo_Text"].setForegroundColorNum(0)
		self["NetworkInfo_Text"].setForegroundColorNum(0)
		self["DhcpInfo_Text"].setForegroundColorNum(0)
		self["IPInfo_Text"].setForegroundColorNum(0)
		self["DNSInfo_Text"].setForegroundColorNum(0)
		self["shortcutsgreen_restart"].setEnabled(False)
		self["shortcutsgreen"].setEnabled(False)
		self["shortcutsyellow"].setEnabled(True)
		self["updown_actions"].setEnabled(False)
		self["key_yellow"].setText("")
		self["key_green"].setText("")
		self.steptimer = True
		self.nextStepTimer.start(1000)

	def KeyOK(self):
		self["infoshortcuts"].setEnabled(True)
		self["shortcuts"].setEnabled(False)
		if self.activebutton == 1: # Adapter Check
			self["InfoText"].setText(_("This test detects your configured LAN adapter."))
			self["InfoTextBorder"].show()
			self["InfoText"].show()
			self["key_red"].setText(_("Back"))
		if self.activebutton == 2: #LAN Check
			self["InfoText"].setText(_("This test checks whether a network cable is connected to your LAN adapter.\nIf you get a \"disconnected\" message:\n- verify that a network cable is attached\n- verify that the cable is not broken"))
			self["InfoTextBorder"].show()
			self["InfoText"].show()
			self["key_red"].setText(_("Back"))
		if self.activebutton == 3: #DHCP Check
			self["InfoText"].setText(_("This test checks whether your LAN adapter is set up for automatic IP address configuration with DHCP.\nIf you get a \"disabled\" message:\n - then your LAN adapter is configured for manual IP setup\n- verify thay you have entered correct IP informations in the adapter setup dialog.\nIf you get an \"enabled\" message:\n-verify that you have a configured and working DHCP server in your network."))
			self["InfoTextBorder"].show()
			self["InfoText"].show()
			self["key_red"].setText(_("Back"))
		if self.activebutton == 4: # IP Check
			self["InfoText"].setText(_("This test checks whether a valid IP address is found for your LAN adapter.\nIf you get a \"unconfirmed\" message:\n- no valid IP address was found\n- please check your DHCP, cabling and adapter setup"))
			self["InfoTextBorder"].show()
			self["InfoText"].show()
			self["key_red"].setText(_("Back"))
		if self.activebutton == 5: # DNS Check
			self["InfoText"].setText(_("This test checks for configured nameservers.\nIf you get a \"unconfirmed\" message:\n- please check your DHCP, cabling and adapter setup\n- if you configured your nameservers manually please verify your entries in the \"Nameserver\" configuration"))
			self["InfoTextBorder"].show()
			self["InfoText"].show()
			self["key_red"].setText(_("Back"))
		if self.activebutton == 6: # Edit Settings
			self.session.open(AdapterSetup,self.iface)

	def KeyYellow(self):
		self.nextstep = 0
		self["shortcutsgreen_restart"].setEnabled(True)
		self["shortcutsgreen"].setEnabled(False)
		self["shortcutsyellow"].setEnabled(False)
		self["key_green"].setText(_("Restart test"))
		self["key_yellow"].setText("")
		self.steptimer = False
		self.nextStepTimer.stop()

	def layoutFinished(self):
		self.setTitle(_("Network test: ") + iNetwork.getFriendlyAdapterName(self.iface) )
		self["shortcutsyellow"].setEnabled(False)
		self["AdapterInfo_OK"].hide()
		self["NetworkInfo_Check"].hide()
		self["DhcpInfo_Check"].hide()
		self["IPInfo_Check"].hide()
		self["DNSInfo_Check"].hide()
		self["EditSettings_Text"].hide()
		self["EditSettingsButton"].hide()
		self["InfoText"].hide()
		self["InfoTextBorder"].hide()
		self["key_yellow"].setText("")

	def setLabels(self):
		self["Adaptertext"] = MultiColorLabel(_("LAN adapter"))
		self["Adapter"] = MultiColorLabel()
		self["AdapterInfo"] = MultiPixmap()
		self["AdapterInfo_Text"] = MultiColorLabel(_("Show info"))
		self["AdapterInfo_OK"] = Pixmap()

		if self.iface in iNetwork.wlan_interfaces:
			self["Networktext"] = MultiColorLabel(_("Wireless network"))
		else:
			self["Networktext"] = MultiColorLabel(_("Local network"))

		self["Network"] = MultiColorLabel()
		self["NetworkInfo"] = MultiPixmap()
		self["NetworkInfo_Text"] = MultiColorLabel(_("Show info"))
		self["NetworkInfo_Check"] = MultiPixmap()

		self["Dhcptext"] = MultiColorLabel(_("DHCP"))
		self["Dhcp"] = MultiColorLabel()
		self["DhcpInfo"] = MultiPixmap()
		self["DhcpInfo_Text"] = MultiColorLabel(_("Show info"))
		self["DhcpInfo_Check"] = MultiPixmap()

		self["IPtext"] = MultiColorLabel(_("IP address"))
		self["IP"] = MultiColorLabel()
		self["IPInfo"] = MultiPixmap()
		self["IPInfo_Text"] = MultiColorLabel(_("Show info"))
		self["IPInfo_Check"] = MultiPixmap()

		self["DNStext"] = MultiColorLabel(_("Nameserver"))
		self["DNS"] = MultiColorLabel()
		self["DNSInfo"] = MultiPixmap()
		self["DNSInfo_Text"] = MultiColorLabel(_("Show info"))
		self["DNSInfo_Check"] = MultiPixmap()

		self["EditSettings_Text"] = MultiColorLabel(_("Edit settings"))
		self["EditSettingsButton"] = MultiPixmap()

		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("Start test"))
		self["key_yellow"] = StaticText(_("Stop test"))

		self["InfoTextBorder"] = Pixmap()
		self["InfoText"] = Label()

	def getLinkState(self,iface):
		if iface in iNetwork.wlan_interfaces:
			try:
				from Plugins.SystemPlugins.WirelessLan.Wlan import iStatus
			except:
				self["Network"].setForegroundColorNum(1)
				self["Network"].setText(_("disconnected"))
				self["NetworkInfo_Check"].setPixmapNum(1)
				self["NetworkInfo_Check"].show()
			else:
				iStatus.getDataForInterface(self.iface,self.getInfoCB)
		else:
			iNetwork.getLinkState(iface,self.LinkStatedataAvail)

	def LinkStatedataAvail(self,data):
		for item in data.splitlines():
			if "Link detected:" in item:
				if "yes" in item:
					self["Network"].setForegroundColorNum(2)
					self["Network"].setText(_("connected"))
					self["NetworkInfo_Check"].setPixmapNum(0)
				else:
					self["Network"].setForegroundColorNum(1)
					self["Network"].setText(_("disconnected"))
					self["NetworkInfo_Check"].setPixmapNum(1)
				break
		else:
			self["Network"].setText(_("unknown"))
		self["NetworkInfo_Check"].show()

	def NetworkStatedataAvail(self,data):
		if data <= 2:
			self["IP"].setForegroundColorNum(2)
			self["IP"].setText(_("confirmed"))
			self["IPInfo_Check"].setPixmapNum(0)
		else:
			self["IP"].setForegroundColorNum(1)
			self["IP"].setText(_("unconfirmed"))
			self["IPInfo_Check"].setPixmapNum(1)
		self["IPInfo_Check"].show()
		self["IPInfo_Text"].setForegroundColorNum(1)
		self.steptimer = True
		self.nextStepTimer.start(300)

	def DNSLookupdataAvail(self,data):
		if data <= 2:
			self["DNS"].setForegroundColorNum(2)
			self["DNS"].setText(_("confirmed"))
			self["DNSInfo_Check"].setPixmapNum(0)
		else:
			self["DNS"].setForegroundColorNum(1)
			self["DNS"].setText(_("unconfirmed"))
			self["DNSInfo_Check"].setPixmapNum(1)
		self["DNSInfo_Check"].show()
		self["DNSInfo_Text"].setForegroundColorNum(1)
		self["EditSettings_Text"].show()
		self["EditSettingsButton"].setPixmapNum(1)
		self["EditSettings_Text"].setForegroundColorNum(2) # active
		self["EditSettingsButton"].show()
		self["key_yellow"].setText("")
		self["key_green"].setText(_("Restart test"))
		self["shortcutsgreen"].setEnabled(False)
		self["shortcutsgreen_restart"].setEnabled(True)
		self["shortcutsyellow"].setEnabled(False)
		self["updown_actions"].setEnabled(True)
		self.activebutton = 6

	def getInfoCB(self,data,status):
		if data is not None:
			if data is True:
				if status is not None:
					if status[self.iface]["essid"] == "off" or status[self.iface]["accesspoint"] == "Not-Associated" or status[self.iface]["accesspoint"] == False:
						self["Network"].setForegroundColorNum(1)
						self["Network"].setText(_("disconnected"))
						self["NetworkInfo_Check"].setPixmapNum(1)
						self["NetworkInfo_Check"].show()
					else:
						self["Network"].setForegroundColorNum(2)
						self["Network"].setText(_("connected"))
						self["NetworkInfo_Check"].setPixmapNum(0)
						self["NetworkInfo_Check"].show()

	def cleanup(self):
		iNetwork.stopLinkStateConsole()
		iNetwork.stopDNSConsole()
		try:
			from Plugins.SystemPlugins.WirelessLan.Wlan import iStatus
		except ImportError:
			pass
		else:
			iStatus.stopWlanConsole()

class NetworkMountsMenu(Screen,HelpableScreen):
	skin = """
	<screen name="NetworkMountsMenu" position="center,center" size="560,400" >
		<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
		<widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
		<ePixmap pixmap="skin_default/border_menu.png" position="5,45" zPosition="1" size="250,300" transparent="1" alphatest="on" />
		<widget name="menulist" position="15,55" size="230,260" zPosition="10" scrollbarMode="showOnDemand" />
		<widget source="introduction" render="Label" position="305,50" size="230,300" font="Regular;19" halign="center" valign="center" backgroundColor="#25062748" transparent="1" />
	</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		HelpableScreen.__init__(self)
		Screen.setTitle(self, _("Mounts Setup"))
		self.session = session
		self.onChangedEntry = [ ]
		self.mainmenu = self.genMainMenu()
		self["menulist"] = MenuList(self.mainmenu)
		self["key_red"] = StaticText(_("Close"))
		self["introduction"] = StaticText()

		self["WizardActions"] = HelpableActionMap(self, "WizardActions",
			{
			"up": (self.up, _("move up to previous entry")),
			"down": (self.down, _("move down to next entry")),
			"left": (self.left, _("move up to first entry")),
			"right": (self.right, _("move down to last entry")),
			})

		self["OkCancelActions"] = HelpableActionMap(self, "OkCancelActions",
			{
			"cancel": (self.close, _("exit mounts setup menu")),
			"ok": (self.ok, _("select menu entry")),
			})

		self["ColorActions"] = HelpableActionMap(self, "ColorActions",
			{
			"red": (self.close, _("exit networkadapter setup menu")),
			})

		self["actions"] = NumberActionMap(["WizardActions","ShortcutActions"],
		{
			"ok": self.ok,
			"back": self.close,
			"up": self.up,
			"down": self.down,
			"red": self.close,
			"left": self.left,
			"right": self.right,
		}, -2)

		if not self.selectionChanged in self["menulist"].onSelectionChanged:
			self["menulist"].onSelectionChanged.append(self.selectionChanged)
		self.selectionChanged()

	def createSummary(self):
		from Screens.PluginBrowser import PluginBrowserSummary
		return PluginBrowserSummary

	def selectionChanged(self):
		item = self["menulist"].getCurrent()
		if item:
			if item[1][0] == 'extendedSetup':
				self["introduction"].setText(_(item[1][1]))
			name = str(self["menulist"].getCurrent()[0])
			desc = self["introduction"].text
		else:
			name = ""
			desc = ""
		for cb in self.onChangedEntry:
			cb(name, desc)

	def ok(self):
		if self["menulist"].getCurrent()[1][0] == 'extendedSetup':
			self.extended = self["menulist"].getCurrent()[1][2]
			self.extended(self.session)

	def up(self):
		self["menulist"].up()

	def down(self):
		self["menulist"].down()

	def left(self):
		self["menulist"].pageUp()

	def right(self):
		self["menulist"].pageDown()

	def genMainMenu(self):
		menu = []
		self.extended = None
		self.extendedSetup = None
		for p in plugins.getPlugins(PluginDescriptor.WHERE_NETWORKMOUNTS):
			callFnc = p.__call__["ifaceSupported"](self)
			if callFnc is not None:
				self.extended = callFnc
				if p.__call__.has_key("menuEntryName"):
					menuEntryName = p.__call__["menuEntryName"](self)
				else:
					menuEntryName = _('Extended Setup...')
				if p.__call__.has_key("menuEntryDescription"):
					menuEntryDescription = p.__call__["menuEntryDescription"](self)
				else:
					menuEntryDescription = _('Extended Networksetup Plugin...')
				self.extendedSetup = ('extendedSetup',menuEntryDescription, self.extended)
				menu.append((menuEntryName,self.extendedSetup))
		return menu

class NetworkFtp(Screen):
	skin = """
		<screen position="center,center" size="560,310" >
			<widget name="lab1" position="20,90" size="150,30" font="Regular;20" valign="center" transparent="0"/>
			<widget name="labactive" position="180,90" size="250,30" font="Regular;20" valign="center" transparent="0"/>
			<widget name="lab2" position="20,160" size="150,30" font="Regular;20" valign="center" transparent="0"/>
			<widget name="labstop" position="180,160" size="100,30" font="Regular;20" valign="center" halign="center" backgroundColor="red"/>
			<widget name="labrun" position="180,160" size="100,30" zPosition="1" font="Regular;20" valign="center"  halign="center" backgroundColor="green"/>
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,260" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="140,260" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/yellow.png" position="280,260" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/blue.png" position="420,260" size="140,40" alphatest="on" />
			<widget name="key_red" position="0,260" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<widget name="key_green" position="140,260" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget name="key_yellow" position="280,260" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
			<widget name="key_blue" position="420,260" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("FTP Setup"))
		self.onChangedEntry = [ ]
		self['lab1'] = Label(_("Autostart:"))
		self['labactive'] = Label(_(_("Disabled")))
		self['lab2'] = Label(_("Current Status:"))
		self['labstop'] = Label(_("Stopped"))
		self['labrun'] = Label(_("Running"))
		self['key_green'] = Label(_("Start"))
		self["key_red"] = Label()
		self['key_yellow'] = Label(_("Autostart"))
		self["key_blue"] =  Label()
		self.Console = Console()
		self.my_ftp_active = False
		self.my_ftp_run = False
		self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.close, 'back': self.close, 'green': self.FtpStartStop, 'yellow': self.activateFtp})
		self.Console = Console()
		self.onLayoutFinish.append(self.updateService)

	def createSummary(self):
		return NetworkServicesSummary

	def FtpStartStop(self):
		commands = []
		if not self.my_ftp_run:
			commands.append('/etc/init.d/vsftpd start')
		elif self.my_ftp_run:
			commands.append('/etc/init.d/vsftpd stop')
		self.Console.eBatch(commands, self.StartStopCallback, debug=True)

	def StartStopCallback(self, result = None, retval = None, extra_args = None):
		time.sleep(3)
		self.updateService()

	def activateFtp(self):
		commands = []
		if fileExists('/etc/rc2.d/S20vsftpd'):
			commands.append('update-rc.d -f vsftpd remove')
		else:
			commands.append('update-rc.d -f vsftpd defaults')
		self.Console.eBatch(commands, self.StartStopCallback, debug=True)

	def updateService(self):
		import process
		p = process.ProcessList()
		ftp_process = str(p.named('vsftpd')).strip('[]')
		self['labrun'].hide()
		self['labstop'].hide()
		self['labactive'].setText(_("Disabled"))
		self.my_ftp_active = False
		if fileExists('/etc/rc2.d/S20vsftpd'):
			self['labactive'].setText(_("Enabled"))
			self['labactive'].show()
			self.my_ftp_active = True

		self.my_ftp_run = False
		if ftp_process:
			self.my_ftp_run = True
		if self.my_ftp_run:
			self['labstop'].hide()
			self['labactive'].show()
			self['labrun'].show()
			self['key_green'].setText(_("Stop"))
			status_summary = self['lab2'].text + ' ' + self['labrun'].text
		else:
			self['labrun'].hide()
			self['labstop'].show()
			self['labactive'].show()
			self['key_green'].setText(_("Start"))
			status_summary = self['lab2'].text + ' ' + self['labstop'].text
		title = _("FTP Setup")
		autostartstatus_summary = self['lab1'].text + ' ' + self['labactive'].text

		for cb in self.onChangedEntry:
			cb(title, status_summary, autostartstatus_summary)

class NetworkTelnet(Screen):
	skin = """
		<screen position="center,center" size="560,310" >
			<widget name="lab1" position="20,90" size="150,30" font="Regular;20" valign="center" transparent="0"/>
			<widget name="labactive" position="180,90" size="250,30" font="Regular;20" valign="center" transparent="0"/>
			<widget name="lab2" position="20,160" size="150,30" font="Regular;20" valign="center" transparent="0"/>
			<widget name="labstop" position="180,160" size="100,30" font="Regular;20" valign="center" halign="center" backgroundColor="red"/>
			<widget name="labrun" position="180,160" size="100,30" zPosition="1" font="Regular;20" valign="center"  halign="center" backgroundColor="green"/>
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,260" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="140,260" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/yellow.png" position="280,260" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/blue.png" position="420,260" size="140,40" alphatest="on" />
			<widget name="key_red" position="0,260" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<widget name="key_green" position="140,260" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget name="key_yellow" position="280,260" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
			<widget name="key_blue" position="420,260" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Telnet Setup"))
		self.onChangedEntry = [ ]
		self['lab1'] = Label(_("Autostart:"))
		self['labactive'] = Label(_(_("Disabled")))
		self['lab2'] = Label(_("Current Status:"))
		self['labstop'] = Label(_("Stopped"))
		self['labrun'] = Label(_("Running"))
		self['key_green'] = Label(_("Start"))
		self['key_red'] = Label(_("Remove Service"))
		self['key_yellow'] = Label(_("Autostart"))
		self['key_blue'] = Label(_("Show Log"))
		self.Console = Console()
		self.my_telnet_active = False
		self.my_telnet_run = False
		self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.close, 'back': self.close, 'green': self.TelnetStartStop, 'yellow': self.activateTelnet})

	def createSummary(self):
		return NetworkServicesSummary

	def TelnetStartStop(self):
		commands = []
		if fileExists('/etc/init.d/telnetd.busybox'):
			if self.my_telnet_run:
				commands.append('/etc/init.d/telnetd.busybox stop')
			else:
				commands.append('/bin/su -l -c "/etc/init.d/telnetd.busybox start"')
			self.Console.eBatch(commands, self.StartStopCallback, debug=True)

	def StartStopCallback(self, result = None, retval = None, extra_args = None):
		time.sleep(3)
		self.updateService()

	def activateTelnet(self):
		commands = []
		if fileExists('/etc/init.d/telnetd.busybox'):
			if fileExists('/etc/rc2.d/S20telnetd.busybox'):
				commands.append('update-rc.d -f telnetd.busybox remove')
			else:
				commands.append('update-rc.d -f telnetd.busybox defaults')
		self.Console.eBatch(commands, self.StartStopCallback, debug=True)

	def updateService(self):
		import process
		p = process.ProcessList()
		telnet_process = str(p.named('telnetd')).strip('[]')
		self['labrun'].hide()
		self['labstop'].hide()
		self['labactive'].setText(_("Disabled"))
		self.my_telnet_active = False
		self.my_telnet_run = False
		if fileExists('/etc/rc2.d/S20telnetd.busybox'):
			self['labactive'].setText(_("Enabled"))
			self['labactive'].show()
			self.my_telnet_active = True

		if telnet_process:
			self.my_telnet_run = True
		if self.my_telnet_run:
			self['labstop'].hide()
			self['labactive'].show()
			self['labrun'].show()
			self['key_green'].setText(_("Stop"))
			status_summary = self['lab2'].text + ' ' + self['labrun'].text
		else:
			self['labrun'].hide()
			self['labstop'].show()
			self['labactive'].show()
			self['key_green'].setText(_("Start"))
			status_summary = self['lab2'].text + ' ' + self['labstop'].text
		title = _("Telnet Setup")
		autostartstatus_summary = self['lab1'].text + ' ' + self['labactive'].text

		for cb in self.onChangedEntry:
			cb(title, status_summary, autostartstatus_summary)

class NetworkOpenvpn(Screen):
	skin = """
		<screen position="center,center" size="560,310" >
			<widget name="lab1" position="20,90" size="150,30" font="Regular;20" valign="center" transparent="0"/>
			<widget name="labactive" position="180,90" size="250,30" font="Regular;20" valign="center" transparent="0"/>
			<widget name="lab2" position="20,160" size="150,30" font="Regular;20" valign="center" transparent="0"/>
			<widget name="labstop" position="180,160" size="100,30" font="Regular;20" valign="center" halign="center" backgroundColor="red"/>
			<widget name="labrun" position="180,160" size="100,30" zPosition="1" font="Regular;20" valign="center" halign="center" backgroundColor="green"/>
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,260" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="140,260" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/yellow.png" position="280,260" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/blue.png" position="420,260" size="140,40" alphatest="on" />
			<widget name="key_red" position="0,260" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<widget name="key_green" position="140,260" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget name="key_yellow" position="280,260" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
			<widget name="key_blue" position="420,260" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("OpenVpn Setup"))
		self.onChangedEntry = [ ]
		self['lab1'] = Label(_("Autostart:"))
		self['labactive'] = Label(_(_("Disabled")))
		self['lab2'] = Label(_("Current Status:"))
		self['labstop'] = Label(_("Stopped"))
		self['labrun'] = Label(_("Running"))
		self['key_green'] = Label(_("Start"))
		self['key_red'] = Label(_("Remove Service"))
		self['key_yellow'] = Label(_("Autostart"))
		self['key_blue'] = Label(_("Show Log"))
		self.Console = Console()
		self.my_vpn_active = False
		self.my_vpn_run = False
		self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.close, 'back': self.close, 'red': self.UninstallCheck, 'green': self.VpnStartStop, 'yellow': self.activateVpn, 'blue': self.Vpnshowlog})
		self.service_name = 'openvpn'
		self.onLayoutFinish.append(self.InstallCheck)

	def InstallCheck(self):
		self.Console.ePopen('/usr/bin/opkg list_installed ' + self.service_name, self.checkNetworkState)

	def checkNetworkState(self, str, retval, extra_args):
		if 'Collected errors' in str:
			self.session.openWithCallback(self.close, MessageBox, _("A background update check is in progress, please wait a few minutes and try again."), type=MessageBox.TYPE_INFO, timeout=10, close_on_any_key=True)
		elif not str:
			self.feedscheck = self.session.open(MessageBox,_('Please wait whilst feeds state is checked.'), MessageBox.TYPE_INFO, enable_input = False)
			self.feedscheck.setTitle(_('Checking Feeds'))
			cmd1 = "opkg update"
			self.CheckConsole = Console()
			self.CheckConsole.ePopen(cmd1, self.checkNetworkStateFinished)
		else:
			self.updateService()

	def checkNetworkStateFinished(self, result, retval,extra_args=None):
		if 'bad address' in result:
			self.session.openWithCallback(self.InstallPackageFailed, MessageBox, _("Your %s %s is not connected to the internet, please check your network settings and try again.") % (getMachineBrand(), getMachineName()), type=MessageBox.TYPE_INFO, timeout=10, close_on_any_key=True)
		elif ('wget returned 1' or 'wget returned 255' or '404 Not Found') in result:
			self.session.openWithCallback(self.InstallPackageFailed, MessageBox, _("Sorry feeds are down for maintenance, please try again later."), type=MessageBox.TYPE_INFO, timeout=10, close_on_any_key=True)
		else:
			self.session.openWithCallback(self.InstallPackage, MessageBox, _('Ready to install %s ?') % self.service_name, MessageBox.TYPE_YESNO)

	def InstallPackage(self, val):
		if val:
			self.doInstall(self.installComplete, self.service_name)
		else:
			self.feedscheck.close()
			self.close()

	def InstallPackageFailed(self, val):
		self.feedscheck.close()
		self.close()

	def doInstall(self, callback, pkgname):
		self.message = self.session.open(MessageBox,_("please wait..."), MessageBox.TYPE_INFO, enable_input = False)
		self.message.setTitle(_('Installing Service'))
		self.Console.ePopen('/usr/bin/opkg install ' + pkgname, callback)

	def installComplete(self,result = None, retval = None, extra_args = None):
		self.message.close()
		self.feedscheck.close()
		self.updateService()

	def UninstallCheck(self):
		self.Console.ePopen('/usr/bin/opkg list_installed ' + self.service_name, self.RemovedataAvail)

	def RemovedataAvail(self, str, retval, extra_args):
		if str:
			self.session.openWithCallback(self.RemovePackage, MessageBox, _('Ready to remove %s ?') % self.service_name, MessageBox.TYPE_YESNO)
		else:
			self.updateService()

	def RemovePackage(self, val):
		if val:
			self.doRemove(self.removeComplete, self.service_name)

	def doRemove(self, callback, pkgname):
		self.message = self.session.open(MessageBox,_("please wait..."), MessageBox.TYPE_INFO, enable_input = False)
		self.message.setTitle(_('Removing Service'))
		self.Console.ePopen('/usr/bin/opkg remove ' + pkgname + ' --force-remove --autoremove', callback)

	def removeComplete(self,result = None, retval = None, extra_args = None):
		self.message.close()
		self.close()

	def createSummary(self):
		return NetworkServicesSummary

	def Vpnshowlog(self):
		self.session.open(NetworkVpnLog)

	def VpnStartStop(self):
		if not self.my_vpn_run:
			self.Console.ePopen('/etc/init.d/openvpn start', self.StartStopCallback)
		elif self.my_vpn_run:
			self.Console.ePopen('/etc/init.d/openvpn stop', self.StartStopCallback)

	def StartStopCallback(self, result = None, retval = None, extra_args = None):
		time.sleep(3)
		self.updateService()

	def activateVpn(self):
		if fileExists('/etc/rc2.d/S20openvpn'):
			self.Console.ePopen('update-rc.d -f openvpn remove', self.StartStopCallback)
		else:
			self.Console.ePopen('update-rc.d -f openvpn defaults', self.StartStopCallback)

	def updateService(self):
		import process
		p = process.ProcessList()
		openvpn_process = str(p.named('openvpn')).strip('[]')
		self['labrun'].hide()
		self['labstop'].hide()
		self['labactive'].setText(_("Disabled"))
		self.my_Vpn_active = False
		self.my_vpn_run = False
		if fileExists('/etc/rc2.d/S20openvpn'):
			self['labactive'].setText(_("Enabled"))
			self['labactive'].show()
			self.my_Vpn_active = True
		if openvpn_process:
			self.my_vpn_run = True
		if self.my_vpn_run:
			self['labstop'].hide()
			self['labrun'].show()
			self['key_green'].setText(_("Stop"))
			status_summary= self['lab2'].text + ' ' + self['labrun'].text
		else:
			self['labstop'].show()
			self['labrun'].hide()
			self['key_green'].setText(_("Start"))
			status_summary= self['lab2'].text + ' ' + self['labstop'].text
		title = _("OpenVpn Setup")
		autostartstatus_summary = self['lab1'].text + ' ' + self['labactive'].text

		for cb in self.onChangedEntry:
			cb(title, status_summary, autostartstatus_summary)

class NetworkVpnLog(Screen):
	skin = """
		<screen name="OpenVpnLog" position="center,center" size="590,410" >
			<widget name="infotext" position="10,10" size="590,410" font="Console;16" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("OpenVpn Log"))
		self['infotext'] = ScrollLabel('')
		self.Console = Console()
		self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.close, 'back': self.close, 'up': self['infotext'].pageUp, 'down': self['infotext'].pageDown})
		strview = ''
		self.Console.ePopen('tail /etc/openvpn/openvpn.log > /etc/openvpn/tmp.log')
		time.sleep(1)
		if fileExists('/etc/openvpn/tmp.log'):
			f = open('/etc/openvpn/tmp.log', 'r')
			for line in f.readlines():
				strview += line
			f.close()
			remove('/etc/openvpn/tmp.log')
		self['infotext'].setText(strview)

class NetworkInadyn(Screen):
	skin = """
		<screen position="center,center" size="590,410" >
			<widget name="autostart" position="10,0" size="100,24" font="Regular;20" valign="center" transparent="0" />
			<widget name="labdisabled" position="110,0" size="100,24" font="Regular;20" valign="center" halign="center" backgroundColor="red" zPosition="1" />
			<widget name="labactive" position="110,0" size="100,24" font="Regular;20" valign="center" halign="center" backgroundColor="green" zPosition="2" />
			<widget name="status" position="240,0" size="150,24" font="Regular;20" valign="center" transparent="0" />
			<widget name="labstop" position="390,0" size="100,24" font="Regular;20" valign="center" halign="center" backgroundColor="red" zPosition="1" />
			<widget name="labrun" position="390,0" size="100,24" font="Regular;20" valign="center" halign="center" backgroundColor="green" zPosition="2"/>
			<widget name="time" position="10,50" size="230,30" font="Regular;20" valign="center" transparent="1"/>
			<widget name="labtime" position="240,50" size="100,30" font="Regular;20" valign="center" backgroundColor="#4D5375"/>
			<widget name="username" position="10,100" size="150,30" font="Regular;20" valign="center" transparent="1"/>
			<widget name="labuser" position="160,100" size="310,30" font="Regular;20" valign="center" backgroundColor="#4D5375"/>
			<widget name="password" position="10,150" size="150,30" font="Regular;20" valign="center" transparent="1"/>
			<widget name="labpass" position="160,150" size="310,30" font="Regular;20" valign="center" backgroundColor="#4D5375"/>
			<widget name="alias" position="10,200" size="150,30" font="Regular;20" valign="center" transparent="1"/>
			<widget name="labalias" position="160,200" size="310,30" font="Regular;20" valign="center" backgroundColor="#4D5375"/>
			<widget name="sinactive" position="10,250" zPosition="1" pixmap="skin_default/icons/lock_off.png" size="32,32"  alphatest="on" />
			<widget name="sactive" position="10,250" zPosition="2" pixmap="skin_default/icons/lock_on.png" size="32,32"  alphatest="on" />
			<widget name="system" position="50,250" size="100,30" font="Regular;20" valign="center" transparent="1"/>
			<widget name="labsys" position="160,250" size="310,30" font="Regular;20" valign="center" backgroundColor="#4D5375"/>
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,360" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="150,360" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/yellow.png" position="300,360" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/blue.png" position="450,360" size="140,40" alphatest="on" />
			<widget name="key_red" position="0,360" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<widget name="key_green" position="150,360" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget name="key_yellow" position="300,360" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
			<widget name="key_blue" position="450,360" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Inadyn Setup"))
		self.onChangedEntry = [ ]
		self['autostart'] = Label(_("Autostart:"))
		self['labactive'] = Label(_(_("Active")))
		self['labdisabled'] = Label(_(_("Disabled")))
		self['status'] = Label(_("Current Status:"))
		self['labstop'] = Label(_("Stopped"))
		self['labrun'] = Label(_("Running"))
		self['time'] = Label(_("Time Update in Minutes:"))
		self['labtime'] = Label()
		self['username'] = Label(_("Username") + ":")
		self['labuser'] = Label()
		self['password'] = Label(_("Password") + ":")
		self['labpass'] = Label()
		self['alias'] = Label(_("Alias") + ":")
		self['labalias'] = Label()
		self['sactive'] = Pixmap()
		self['sinactive'] = Pixmap()
		self['system'] = Label(_("System") + ":")
		self['labsys'] = Label()
		self['key_red'] = Label(_("Remove Service"))
		self['key_green'] = Label(_("Start"))
		self['key_yellow'] = Label(_("Autostart"))
		self['key_blue'] = Label(_("Show Log"))
		self['actions'] = ActionMap(['WizardActions', 'ColorActions', 'SetupActions'], {'ok': self.setupinadyn, 'back': self.close, 'menu': self.setupinadyn, 'red': self.UninstallCheck, 'green': self.InadynStartStop, 'yellow': self.autostart, 'blue': self.inaLog})
		self.Console = Console()
		self.service_name = 'inadyn-mt'
		self.onLayoutFinish.append(self.InstallCheck)

	def InstallCheck(self):
		self.Console.ePopen('/usr/bin/opkg list_installed ' + self.service_name, self.checkNetworkState)

	def checkNetworkState(self, str, retval, extra_args):
		if 'Collected errors' in str:
			self.session.openWithCallback(self.close, MessageBox, _("A background update check is in progress, please wait a few minutes and try again."), type=MessageBox.TYPE_INFO, timeout=10, close_on_any_key=True)
		elif not str:
			self.feedscheck = self.session.open(MessageBox,_('Please wait whilst feeds state is checked.'), MessageBox.TYPE_INFO, enable_input = False)
			self.feedscheck.setTitle(_('Checking Feeds'))
			cmd1 = "opkg update"
			self.CheckConsole = Console()
			self.CheckConsole.ePopen(cmd1, self.checkNetworkStateFinished)
		else:
			self.updateService()

	def checkNetworkStateFinished(self, result, retval,extra_args=None):
		if 'bad address' in result:
			self.session.openWithCallback(self.InstallPackageFailed, MessageBox, _("Your %s %s is not connected to the internet, please check your network settings and try again.") % (getMachineBrand(), getMachineName()), type=MessageBox.TYPE_INFO, timeout=10, close_on_any_key=True)
		elif ('wget returned 1' or 'wget returned 255' or '404 Not Found') in result:
			self.session.openWithCallback(self.InstallPackageFailed, MessageBox, _("Sorry feeds are down for maintenance, please try again later."), type=MessageBox.TYPE_INFO, timeout=10, close_on_any_key=True)
		else:
			self.session.openWithCallback(self.InstallPackage, MessageBox, _('Ready to install %s ?') % self.service_name, MessageBox.TYPE_YESNO)

	def InstallPackage(self, val):
		if val:
			self.doInstall(self.installComplete, self.service_name)
		else:
			self.feedscheck.close()
			self.close()

	def InstallPackageFailed(self, val):
		self.feedscheck.close()
		self.close()

	def doInstall(self, callback, pkgname):
		self.message = self.session.open(MessageBox,_("please wait..."), MessageBox.TYPE_INFO, enable_input = False)
		self.message.setTitle(_('Installing Service'))
		self.Console.ePopen('/usr/bin/opkg install ' + pkgname, callback)

	def installComplete(self,result = None, retval = None, extra_args = None):
		self.message.close()
		self.feedscheck.close()
		self.updateService()

	def UninstallCheck(self):
		self.Console.ePopen('/usr/bin/opkg list_installed ' + self.service_name, self.RemovedataAvail)

	def RemovedataAvail(self, str, retval, extra_args):
		if str:
			self.session.openWithCallback(self.RemovePackage, MessageBox, _('Ready to remove %s ?') % self.service_name, MessageBox.TYPE_YESNO)
		else:
			self.updateService()

	def RemovePackage(self, val):
		if val:
			self.doRemove(self.removeComplete, self.service_name)

	def doRemove(self, callback, pkgname):
		self.message = self.session.open(MessageBox,_("please wait..."), MessageBox.TYPE_INFO, enable_input = False)
		self.message.setTitle(_('Removing Service'))
		self.Console.ePopen('/usr/bin/opkg remove ' + pkgname + ' --force-remove --autoremove', callback)

	def removeComplete(self,result = None, retval = None, extra_args = None):
		self.message.close()
		self.close()

	def createSummary(self):
		return NetworkServicesSummary

	def InadynStartStop(self):
		if not self.my_inadyn_run:
			self.Console.ePopen('/etc/init.d/inadyn-mt start', self.StartStopCallback)
		elif self.my_inadyn_run:
			self.Console.ePopen('/etc/init.d/inadyn-mt stop', self.StartStopCallback)

	def StartStopCallback(self, result = None, retval = None, extra_args = None):
		time.sleep(3)
		self.updateService()

	def autostart(self):
		if fileExists('/etc/rc2.d/S20inadyn-mt'):
			self.Console.ePopen('update-rc.d -f inadyn-mt remove', self.StartStopCallback)
		else:
			self.Console.ePopen('update-rc.d -f inadyn-mt defaults', self.StartStopCallback)

	def updateService(self):
		import process
		p = process.ProcessList()
		inadyn_process = str(p.named('inadyn-mt')).strip('[]')
		self['labrun'].hide()
		self['labstop'].hide()
		self['labactive'].hide()
		self['labdisabled'].hide()
		self['sactive'].hide()
		self.my_inadyn_active = False
		self.my_inadyn_run = False
		if fileExists('/etc/rc2.d/S20inadyn-mt'):
			self['labdisabled'].hide()
			self['labactive'].show()
			self.my_inadyn_active = True
			autostartstatus_summary = self['autostart'].text + ' ' + self['labactive'].text
		else:
			self['labactive'].hide()
			self['labdisabled'].show()
			autostartstatus_summary = self['autostart'].text + ' ' + self['labdisabled'].text
		if inadyn_process:
			self.my_inadyn_run = True
		if self.my_inadyn_run:
			self['labstop'].hide()
			self['labrun'].show()
			self['key_green'].setText(_("Stop"))
			status_summary = self['status'].text + ' ' + self['labrun'].text
		else:
			self['labstop'].show()
			self['labrun'].hide()
			self['key_green'].setText(_("Start"))
			status_summary = self['status'].text + ' ' + self['labstop'].text

		#self.my_nabina_state = False
		if fileExists('/etc/inadyn.conf'):
			f = open('/etc/inadyn.conf', 'r')
			for line in f.readlines():
				line = line.strip()
				if line.startswith('username '):
					line = line[9:]
					self['labuser'].setText(line)
				elif line.startswith('password '):
					line = line[9:]
					self['labpass'].setText(line)
				elif line.startswith('alias '):
					line = line[6:]
					self['labalias'].setText(line)
				elif line.startswith('update_period_sec '):
					line = line[18:]
					line = (int(line) / 60)
					self['labtime'].setText(str(line))
				elif line.startswith('dyndns_system ') or line.startswith('#dyndns_system '):
					if line.startswith('#'):
						line = line[15:]
						self['sactive'].hide()
					else:
						line = line[14:]
						self['sactive'].show()
					self['labsys'].setText(line)
			f.close()
		title = _("Inadyn Setup")

		for cb in self.onChangedEntry:
			cb(title, status_summary, autostartstatus_summary)

	def setupinadyn(self):
		self.session.openWithCallback(self.updateService, NetworkInadynSetup)

	def inaLog(self):
		self.session.open(NetworkInadynLog)

class NetworkInadynSetup(Screen, ConfigListScreen):
	skin = """
		<screen name="InadynSetup" position="center,center" size="440,350" >
			<widget name="config" position="10,10" size="420,240" scrollbarMode="showOnDemand" />
			<widget name="HelpWindow" pixmap="skin_default/vkey_icon.png" position="170,300" zPosition="1" size="440,350" transparent="1" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/red.png" position="130,310" size="140,40" alphatest="on" />
			<widget name="key_red" position="130,310" size="140,40" zPosition="1" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<ePixmap pixmap="skin_default/buttons/key_text.png" position="300,313" zPosition="4" size="35,25" alphatest="on" transparent="1" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		self.onChangedEntry = [ ]
		self.list = []
		ConfigListScreen.__init__(self, self.list, session = self.session, on_change = self.selectionChanged)
		Screen.setTitle(self, _("Inadyn Setup"))
		self['key_red'] = Label(_("Save"))
		self['actions'] = ActionMap(['WizardActions', 'ColorActions', 'VirtualKeyboardActions'], {'red': self.saveIna, 'back': self.close, 'showVirtualKeyboard': self.KeyText})
		self["HelpWindow"] = Pixmap()
		self["HelpWindow"].hide()
		self.updateList()
		if not self.selectionChanged in self["config"].onSelectionChanged:
			self["config"].onSelectionChanged.append(self.selectionChanged)

	def createSummary(self):
		from Screens.PluginBrowser import PluginBrowserSummary
		return PluginBrowserSummary

	def selectionChanged(self):
		item = self["config"].getCurrent()
		if item:
			name = str(item[0])
			desc = str(item[1].getValue())
		else:
			name = ""
			desc = ""
		for cb in self.onChangedEntry:
			cb(name, desc)

	def updateList(self):
		self.ina_user = NoSave(ConfigText(fixed_size=False))
		self.ina_pass = NoSave(ConfigText(fixed_size=False))
		self.ina_alias = NoSave(ConfigText(fixed_size=False))
		self.ina_period = NoSave(ConfigNumber())
		self.ina_sysactive = NoSave(ConfigYesNo(default='False'))
		self.ina_system = NoSave(ConfigSelection(default = "dyndns@dyndns.org", choices = [("dyndns@dyndns.org", "dyndns@dyndns.org"), ("statdns@dyndns.org", "statdns@dyndns.org"), ("custom@dyndns.org", "custom@dyndns.org"), ("default@no-ip.com", "default@no-ip.com")]))

		if fileExists('/etc/inadyn.conf'):
			f = open('/etc/inadyn.conf', 'r')
			for line in f.readlines():
				line = line.strip()
				if line.startswith('username '):
					line = line[9:]
					self.ina_user.value = line
					ina_user1 = getConfigListEntry(_("Username") + ":", self.ina_user)
					self.list.append(ina_user1)
				elif line.startswith('password '):
					line = line[9:]
					self.ina_pass.value = line
					ina_pass1 = getConfigListEntry(_("Password") + ":", self.ina_pass)
					self.list.append(ina_pass1)
				elif line.startswith('alias '):
					line = line[6:]
					self.ina_alias.value = line
					ina_alias1 = getConfigListEntry(_("Alias") + ":", self.ina_alias)
					self.list.append(ina_alias1)
				elif line.startswith('update_period_sec '):
					line = line[18:]
					line = (int(line) / 60)
					self.ina_period.value = line
					ina_period1 = getConfigListEntry(_("Time Update in Minutes") + ":", self.ina_period)
					self.list.append(ina_period1)
				elif line.startswith('dyndns_system ') or line.startswith('#dyndns_system '):
					if not line.startswith('#'):
						self.ina_sysactive.value = True
						line = line[14:]
					else:
						self.ina_sysactive.value = False
						line = line[15:]
					ina_sysactive1 = getConfigListEntry(_("Set System") + ":", self.ina_sysactive)
					self.list.append(ina_sysactive1)
					self.ina_value = line
					ina_system1 = getConfigListEntry(_("System") + ":", self.ina_system)
					self.list.append(ina_system1)

			f.close()
		self['config'].list = self.list
		self['config'].l.setList(self.list)

	def KeyText(self):
		sel = self['config'].getCurrent()
		if sel:
			if isinstance(self["config"].getCurrent()[1], ConfigText) or isinstance(self["config"].getCurrent()[1], ConfigPassword):
				if self["config"].getCurrent()[1].help_window.instance is not None:
					self["config"].getCurrent()[1].help_window.hide()
			self.vkvar = sel[0]
			if self.vkvar == _("Username") + ':' or self.vkvar == _("Password") + ':' or self.vkvar == _("Alias") + ':' or self.vkvar == _("System") + ':':
				from Screens.VirtualKeyBoard import VirtualKeyBoard
				self.session.openWithCallback(self.VirtualKeyBoardCallback, VirtualKeyBoard, title = self["config"].getCurrent()[0], text = self["config"].getCurrent()[1].getValue())

	def VirtualKeyBoardCallback(self, callback = None):
		if callback is not None and len(callback):
			self["config"].getCurrent()[1].setValue(callback)
			self["config"].invalidate(self["config"].getCurrent())

	def saveIna(self):
		if fileExists('/etc/inadyn.conf'):
			inme = open('/etc/inadyn.conf', 'r')
			out = open('/etc/inadyn.conf.tmp', 'w')
			for line in inme.readlines():
				line = line.replace('\n', '')
				if line.startswith('username '):
					line = ('username ' + self.ina_user.value.strip())
				elif line.startswith('password '):
					line = ('password ' + self.ina_pass.value.strip())
				elif line.startswith('alias '):
					line = ('alias ' + self.ina_alias.value.strip())
				elif line.startswith('update_period_sec '):
					strview = (self.ina_period.getValue() * 60)
					strview = str(strview)
					line = ('update_period_sec ' + strview)
				elif line.startswith('dyndns_system ') or line.startswith('#dyndns_system '):
					if self.ina_sysactive.getValue():
						line = ('dyndns_system ' + self.ina_system.value.strip())
					else:
						line = ('#dyndns_system ' + self.ina_system.value.strip())
				out.write((line + '\n'))
			out.close()
			inme.close()
		else:
			self.session.open(MessageBox, _("Sorry Inadyn Config is Missing"), MessageBox.TYPE_INFO)
			self.close()
		if fileExists('/etc/inadyn.conf.tmp'):
			rename('/etc/inadyn.conf.tmp', '/etc/inadyn.conf')
		self.myStop()

	def myStop(self):
		self.close()

class NetworkInadynLog(Screen):
	skin = """
		<screen name="InadynLog" position="center,center" size="590,410" >
			<widget name="infotext" position="10,10" size="590,410" font="Console;16" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Inadyn Log"))
		self['infotext'] = ScrollLabel('')
		self['actions'] = ActionMap(['WizardActions', 'DirectionActions', 'ColorActions'], {'ok': self.close,
		 'back': self.close,
		 'up': self['infotext'].pageUp,
		 'down': self['infotext'].pageDown})
		strview = ''
		if fileExists('/var/log/inadyn.log'):
			f = open('/var/log/inadyn.log', 'r')
			for line in f.readlines():
				strview += line
			f.close()
		self['infotext'].setText(strview)

class NetworkSamba(Screen):
	skin = """
		<screen position="center,center" size="560,310" >
			<widget name="lab1" position="20,90" size="150,30" font="Regular;20" valign="center" transparent="0"/>
			<widget name="labactive" position="180,90" size="250,30" font="Regular;20" valign="center" transparent="0"/>
			<widget name="lab2" position="20,160" size="150,30" font="Regular;20" valign="center" transparent="0"/>
			<widget name="labstop" position="180,160" size="100,30" font="Regular;20" valign="center" halign="center" backgroundColor="red"/>
			<widget name="labrun" position="180,160" size="100,30" zPosition="1" font="Regular;20" valign="center"  halign="center" backgroundColor="green"/>
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,260" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="140,260" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/yellow.png" position="280,260" size="140,40" alphatest="on" />
			<ePixmap pixmap="skin_default/buttons/blue.png" position="420,260" size="140,40" alphatest="on" />
			<widget name="key_red" position="0,260" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<widget name="key_green" position="140,260" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget name="key_yellow" position="280,260" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
			<widget name="key_blue" position="420,260" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#18188b" transparent="1" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Samba Setup"))
		self.onChangedEntry = [ ]
		self['lab1'] = Label(_("Autostart:"))
		self['labactive'] = Label(_(_("Disabled")))
		self['lab2'] = Label(_("Current Status:"))
		self['labstop'] = Label(_("Stopped"))
		self['labrun'] = Label(_("Running"))
		self['key_green'] = Label(_("Start"))
		self['key_red'] = Label(_("Remove Service"))
		self['key_yellow'] = Label(_("Autostart"))
		self['key_blue'] = Label(_("Show Log"))
		self.Console = Console()
		self.my_Samba_active = False
		self.my_Samba_run = False
		self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.close, 'back': self.close, 'red': self.UninstallCheck, 'green': self.SambaStartStop, 'yellow': self.activateSamba, 'blue': self.Sambashowlog})
		self.service_name = basegroup + '-samba'
		self.onLayoutFinish.append(self.InstallCheck)

	def InstallCheck(self):
		self.Console.ePopen('/usr/bin/opkg list_installed ' + self.service_name, self.checkNetworkState)

	def checkNetworkState(self, str, retval, extra_args):
		if 'Collected errors' in str:
			self.session.openWithCallback(self.close, MessageBox, _("A background update check is in progress, please wait a few minutes and try again."), type=MessageBox.TYPE_INFO, timeout=10, close_on_any_key=True)
		elif not str:
			self.feedscheck = self.session.open(MessageBox,_('Please wait whilst feeds state is checked.'), MessageBox.TYPE_INFO, enable_input = False)
			self.feedscheck.setTitle(_('Checking Feeds'))
			cmd1 = "opkg update"
			self.CheckConsole = Console()
			self.CheckConsole.ePopen(cmd1, self.checkNetworkStateFinished)
		else:
			self.updateService()

	def checkNetworkStateFinished(self, result, retval,extra_args=None):
		if 'bad address' in result:
			self.session.openWithCallback(self.InstallPackageFailed, MessageBox, _("Your %s %s is not connected to the internet, please check your network settings and try again.") % (getMachineBrand(), getMachineName()), type=MessageBox.TYPE_INFO, timeout=10, close_on_any_key=True)
		elif ('wget returned 1' or 'wget returned 255' or '404 Not Found') in result:
			self.session.openWithCallback(self.InstallPackageFailed, MessageBox, _("Sorry feeds are down for maintenance, please try again later."), type=MessageBox.TYPE_INFO, timeout=10, close_on_any_key=True)
		else:
			self.session.openWithCallback(self.QuestionCallback, MessageBox, _('Ready to install %s ?') % self.service_name, MessageBox.TYPE_YESNO)

	def QuestionCallback(self, val):
		if val:
			self.session.openWithCallback(self.InstallPackage, MessageBox, _('Do you want to also install samba client ?\nThis allows you to mount your windows shares on this device.'), MessageBox.TYPE_YESNO)
		else:
			self.feedscheck.close()
			self.close()

	def InstallPackage(self, val):
		if val:
			self.service_name = self.service_name + ' ' + basegroup + '-smbfs-client'
		self.doInstall(self.installComplete, self.service_name)

	def InstallPackageFailed(self, val):
		self.feedscheck.close()
		self.close()

	def doInstall(self, callback, pkgname):
		self.message = self.session.open(MessageBox,_("please wait..."), MessageBox.TYPE_INFO, enable_input = False)
		self.message.setTitle(_('Installing Service'))
		self.Console.ePopen('/usr/bin/opkg install ' + pkgname, callback)

	def installComplete(self,result = None, retval = None, extra_args = None):
		self.session.open(TryQuitMainloop, 2)

	def UninstallCheck(self):
		self.service_name = self.service_name + ' ' + basegroup + '-smbfs-client'
		self.Console.ePopen('/usr/bin/opkg list_installed ' + self.service_name, self.RemovedataAvail)

	def RemovedataAvail(self, str, retval, extra_args):
		if str:
			restartbox = self.session.openWithCallback(self.RemovePackage,MessageBox,_('Your %s %s will be restarted after the removal of service\nDo you want to remove now ?') % (getMachineBrand(), getMachineName()), MessageBox.TYPE_YESNO)
			restartbox.setTitle(_('Ready to remove "%s" ?') % self.service_name)
		else:
			self.updateService()

	def RemovePackage(self, val):
		if val:
			self.doRemove(self.removeComplete, self.service_name)

	def doRemove(self, callback, pkgname):
		self.message = self.session.open(MessageBox,_("please wait..."), MessageBox.TYPE_INFO, enable_input = False)
		self.message.setTitle(_('Removing Service'))
		self.Console.ePopen('/usr/bin/opkg remove ' + pkgname + ' --force-remove --autoremove', callback)

	def removeComplete(self,result = None, retval = None, extra_args = None):
		self.message.close()
		self.close()

	def createSummary(self):
		return NetworkServicesSummary

	def Sambashowlog(self):
		self.session.open(NetworkSambaLog)

	def SambaStartStop(self):
		commands = []
		if not self.my_Samba_run:
			commands.append('/etc/init.d/samba start')
		elif self.my_Samba_run:
			commands.append('/etc/init.d/samba stop')
			commands.append('killall nmbd')
			commands.append('killall smbd')
		self.Console.eBatch(commands, self.StartStopCallback, debug=True)

	def StartStopCallback(self, result = None, retval = None, extra_args = None):
		time.sleep(3)
		self.updateService()

	def activateSamba(self):
		commands = []
		if fileExists('/etc/rc2.d/S20samba'):
			commands.append('update-rc.d -f samba remove')
		else:
			commands.append('update-rc.d -f samba defaults')
		self.Console.eBatch(commands, self.StartStopCallback, debug=True)

	def updateService(self):
		import process
		p = process.ProcessList()
		samba_process = str(p.named('smbd')).strip('[]')
		self['labrun'].hide()
		self['labstop'].hide()
		self['labactive'].setText(_("Disabled"))
		self.my_Samba_active = False
		if fileExists('/etc/rc2.d/S20samba'):
			self['labactive'].setText(_("Enabled"))
			self['labactive'].show()
			self.my_Samba_active = True

		self.my_Samba_run = False
		if samba_process:
			self.my_Samba_run = True
		if self.my_Samba_run:
			self['labstop'].hide()
			self['labactive'].show()
			self['labrun'].show()
			self['key_green'].setText(_("Stop"))
			status_summary = self['lab2'].text + ' ' + self['labrun'].text
		else:
			self['labrun'].hide()
			self['labstop'].show()
			self['labactive'].show()
			self['key_green'].setText(_("Start"))
			status_summary = self['lab2'].text + ' ' + self['labstop'].text
		title = _("Samba Setup")
		autostartstatus_summary = self['lab1'].text + ' ' + self['labactive'].text

		for cb in self.onChangedEntry:
			cb(title, status_summary, autostartstatus_summary)

class NetworkSambaLog(Screen):
	skin = """
		<screen position="80,100" size="560,400" >
			<widget name="infotext" position="10,10" size="540,380" font="Regular;18" />
		</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Samba Log"))
		self['infotext'] = ScrollLabel('')
		self.Console = Console()
		self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.close, 'back': self.close, 'up': self['infotext'].pageUp, 'down': self['infotext'].pageDown})
		strview = ''
		self.Console.ePopen('tail /tmp/smb.log > /tmp/tmp.log')
		time.sleep(1)
		if fileExists('/tmp/tmp.log'):
			f = open('/tmp/tmp.log', 'r')
			for line in f.readlines():
				strview += line
			f.close()
			remove('/tmp/tmp.log')
		self['infotext'].setText(strview)

class NetworkServicesSummary(Screen):
	def __init__(self, session, parent):
		Screen.__init__(self, session, parent = parent)
		self["title"] = StaticText("")
		self["status_summary"] = StaticText("")
		self["autostartstatus_summary"] = StaticText("")
		self.onShow.append(self.addWatcher)
		self.onHide.append(self.removeWatcher)

	def addWatcher(self):
		self.parent.onChangedEntry.append(self.selectionChanged)
		self.parent.updateService()

	def removeWatcher(self):
		self.parent.onChangedEntry.remove(self.selectionChanged)

	def selectionChanged(self, title, status_summary, autostartstatus_summary):
		self["title"].text = title
		self["status_summary"].text = status_summary
		self["autostartstatus_summary"].text = autostartstatus_summary
