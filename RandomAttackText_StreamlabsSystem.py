#---------------------------------------
#   Import Libraries
#---------------------------------------
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import json
import codecs
import re
import random
from ConfigParser import ConfigParser

#---------------------------------------
#   [Required] Script Information
#---------------------------------------
ScriptName = 'RandomAttackText'
Website = 'https://github.com/nossebro/RandomAttackText'
Creator = 'nossebro'
Version = '0.0.2'
Description = 'Streamlabs Chatbot Template'

#---------------------------------------
#   Script Variables
#---------------------------------------
Logger = None
ScriptSettings = None
Commands = None
ConfigFile = os.path.join(os.path.dirname(__file__), "Config.ini")
SettingsFile = os.path.join(os.path.dirname(__file__), "Settings.json")
UIConfigFile = os.path.join(os.path.dirname(__file__), "UI_Config.json")

#---------------------------------------
#   Script Classes
#---------------------------------------
class StreamlabsLogHandler(logging.StreamHandler):
	def emit(self, record):
		try:
			message = self.format(record)
			Parent.Log(ScriptName, message)
			self.flush()
		except (KeyboardInterrupt, SystemExit):
			raise
		except:
			self.handleError(record)

class Settings(object):
	def __init__(self, settingsfile=None):
		defaults = self.DefaultSettings(UIConfigFile)
		try:
			with codecs.open(settingsfile, encoding="utf-8-sig", mode="r") as f:
				settings = json.load(f, encoding="utf-8")
			self.__dict__ = MergeLists(defaults, settings)
		except:
			self.__dict__ = defaults

	def DefaultSettings(self, settingsfile=None):
		defaults = dict()
		with codecs.open(settingsfile, encoding="utf-8-sig", mode="r") as f:
			ui = json.load(f, encoding="utf-8")
		for key in ui:
			try:
				defaults[key] = ui[key]['value']
			except:
				if key != "output_file":
					Parent.Log(ScriptName, "DefaultSettings(): Could not find key {0} in settings".format(key))
		return defaults

	def Reload(self, jsondata):
		self.__dict__ = MergeLists(self.DefaultSettings(UIConfigFile), json.loads(jsondata, encoding="utf-8"))

#---------------------------------------
#   Script Functions
#---------------------------------------
def GetLogger():
	log = logging.getLogger(ScriptName)
	log.setLevel(logging.DEBUG)

	sl = StreamlabsLogHandler()
	sl.setFormatter(logging.Formatter("%(funcName)s(): %(message)s"))
	sl.setLevel(logging.INFO)
	log.addHandler(sl)

	fl = TimedRotatingFileHandler(filename=os.path.join(os.path.dirname(__file__), "info"), when="w0", backupCount=8, encoding="utf-8")
	fl.suffix = "%Y%m%d"
	fl.setFormatter(logging.Formatter("%(asctime)s  %(funcName)s(): %(levelname)s: %(message)s"))
	fl.setLevel(logging.INFO)
	log.addHandler(fl)

	if ScriptSettings.DebugMode:
		dfl = TimedRotatingFileHandler(filename=os.path.join(os.path.dirname(__file__), "debug"), when="h", backupCount=24, encoding="utf-8")
		dfl.suffix = "%Y%m%d%H%M%S"
		dfl.setFormatter(logging.Formatter("%(asctime)s  %(funcName)s(): %(levelname)s: %(message)s"))
		dfl.setLevel(logging.DEBUG)
		log.addHandler(dfl)

	log.debug("Logger initialized")
	return log

def MergeLists(x = dict(), y = dict()):
	z = dict()
	for attr in x:
		if attr not in y:
			z[attr] = x[attr]
		else:
			z[attr] = y[attr]
	return z

#---------------------------------------
#   Chatbot Initialize Function
#---------------------------------------
def Init():
	global ScriptSettings
	ScriptSettings = Settings(SettingsFile)
	global Logger
	Logger = GetLogger()
	global Commands
	Commands = dict()
	config = ConfigParser()
	Logger.debug(config.readfp(codecs.open(ConfigFile, encoding="utf-8-sig", mode="r")))
	for x in config.sections():
		Commands[x.lower()] = dict()
		Commands[x.lower()].update(config.items(x))

#---------------------------------------
#   Chatbot Script Unload Function
#---------------------------------------
def Unload():
	global Logger
	if Logger:
		for handler in Logger.handlers[:]:
			Logger.removeHandler(handler)
		Logger = None

#---------------------------------------
#   Chatbot Save Settings Function
#---------------------------------------
def ReloadSettings(jsondata):
	ScriptSettings.Reload(jsondata)
	Logger.debug("Settings reloaded")
	Parent.BroadcastWsEvent('{0}_UPDATE_SETTINGS'.format(ScriptName.upper()), json.dumps(ScriptSettings.__dict__))
	global Commands
	Commands = dict()
	config = ConfigParser()
	Logger.debug(config.readfp(codecs.open(ConfigFile, encoding="utf-8-sig", mode="r")))
	for x in config.sections():
		Commands[x.lower()] = dict()
		Commands[x.lower()].update(config.items(x))

#---------------------------------------
#   Chatbot Execute Function
#---------------------------------------
def Execute(data):
	global Commands
	if data.IsChatMessage() and data.IsFromTwitch():
		if data.GetParamCount() == 1:
			Target = "ananonymouscheerer"
			BlackList = [ "ananonymouscheerer", "streamelements", "streamlabs", "stay_hydrated_bot", ScriptSettings.Blacklist.lower().split(",") ]
			while Target.lower() in BlackList:
				try:
					Target = Parent.GetDisplayName(Parent.GetRandomActiveUser())
				except:
					Target = "ananonymouscheerer"
		else:
			try:
				Target = Parent.GetDisplayName(data.GetParam(1).replace("@", ""))
			except:
				Target = data.GetParam(1).replace("@", "")
		Level = 0
		if Parent.HasPermission(data.User, "regular", ""):
			Level = 1
		if Parent.HasPermission(data.User, "subscriber", ""):
			Level = 2
		if Parent.HasPermission(data.User, "moderator", ""):
			Level = 3
		if Parent.HasPermission(data.User, "caster", ""):
			Level = 4
		match = re.match(r"!(?P<command>[\w]+)", data.GetParam(0))
		if match and match.group("command").lower() in Commands:
			if ("level" in Commands[match.group("command")] and Level >= int(Commands[match.group("command")]["level"])) or ("user" in Commands[match.group("command")] and Commands[match.group("command")]["user"].lower() == data.User) and "response" in Commands[match.group("command")]:
				Logger.debug("Replacing {{user}} with {0}".format(data.User))
				Logger.debug("Replacing {{target}} with {0}".format(Target))
				Text = Commands[match.group("command")]["response"].replace("{target}", Target).replace("{user}", data.User)
				for x in Commands[match.group("command")]:
					if x in [ "command", "user", "level", "response" ]:
						continue
					Options = Commands[match.group("command")][x].split("|")
					Random = random.SystemRandom().randrange(0, len(Options))
					Logger.debug("Replacing {{{0}}} with {1}".format(x, Options[Random]))
					Text = Text.replace("{{{0}}}".format(x), Options[Random])
				Logger.debug(Text)
				Parent.SendTwitchMessage(Text)

#---------------------------------------
#   Chatbot Tick Function
#---------------------------------------
def Tick():
	pass
