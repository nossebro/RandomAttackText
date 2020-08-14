#---------------------------------------
#   Import Libraries
#---------------------------------------
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import json
import codecs

#---------------------------------------
#   [Required] Script Information
#---------------------------------------
ScriptName = 'SLCBTemplate'
Website = 'https://github.com/nossebro/SLCBTemplate'
Creator = 'nossebro'
Version = '0.0.1'
Description = 'Streamlabs Chatbot Template'

#---------------------------------------
#   Script Variables
#---------------------------------------
Logger = None
ScriptSettings = None
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

#---------------------------------------
#   Chatbot Script Unload Function
#---------------------------------------
def Unload():
	global Logger
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

#---------------------------------------
#   Chatbot Execute Function
#---------------------------------------
def Execute(data):
	pass

#---------------------------------------
#   Chatbot Tick Function
#---------------------------------------
def Tick():
	pass
