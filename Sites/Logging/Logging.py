class Logging(object):
	"""
	Logging is a static class that will take and filter every kind of
	output this program does
	"""
	verbos = 0

	@staticmethod
	def logEvent(category, logType, data):
		# category can be "Error", or "Event", or "Debug"
		# Type can be different string based on Category
		# Data is a dictionary of different information depending on the category and type
		if category is "Error":
			if "Hardware Interface Thread" in logType:
				# in here check if 'type' is a buffer error, if so suggest checking connection to device
				print("Error: Thread '{}' has had an error of type {}. Restarting thread now...".format(data['thread'],data['type']))
		elif category is "Event":
			if "Thread Start" in logType:
				print("Event- {}: {}".format(logType,data.get("thread")))
			elif "ThermoCouple Reading" in logType:
				Logging.logThermoCouples(data)
			elif "Thermal Profile Update" in logType:
				Logging.logThermalProfile(data)
			else:
				print("Event- {}: {}".format(logType,data.get("message")))
		elif category is "Debug":
			if "Status Update" in logType:
				Logging.debugPrint(data["level"],data['message'])
			elif "Data Dump" in logType:
				Logging.debugPrint(data["level"],data['message'], data["dict"])

	@staticmethod
	def debugPrint(verbosLevel, string, dictionary=None):
		if Logging.verbos >= verbosLevel: 
			spacing = "  "*(verbosLevel-1)
			BLUE_START = "\033[94m"
			COLOR_END = "\033[0m"
			prefix = "{}{}debug-{}: {}".format(spacing,BLUE_START,verbosLevel,COLOR_END)
			if dictionary:
				print("{}{}".format(prefix,string))
				for i, entry in enumerate(dictionary):
					if type(dictionary) == type({}):
						print("{}  {} --> {}".format(prefix,entry,dictionary[entry]))
					elif type(dictionary) == type([]):
						print("{}  {}".format(prefix,entry))
			else:
				with open('./debugLog.txt','a') as filer:
					for line in string.split("\n"):
						filer.write("{}{}".format(prefix,line)+"\n")
						print("{}{}".format(prefix,line))

	@staticmethod
	def logThermoCouples(data):
		'''
		data = {
			"time":		TCs['time'],
			"tcList":	TCs['tcList'],
		}
		TCs is a list of dicitations ordered like this....
		{
		'Thermocouple': tc_num,
		'time': tc_time_offset,
		'temp': tc_tempK,
		'working': tc_working,
		'alarm': tc_alarm
		}
		'''
		testList = [7,9,10,11,12,91,92,100,105,110,115,120]
		with open('./TempLog.txt','a') as filer:
			for tc in data['tcList']:
				if tc['working']:
					output = ("LOG: TIME {} TC-{}: {} (k)".format(data["time"].time(),tc["Thermocouple"], tc["temp"]))
					filer.write("{},{},{}".format(data["time"].time(),tc["Thermocouple"],tc["temp"])+"\n")
					if tc["Thermocouple"] in testList:
						print("TC-{}: {} (k)".format(tc["Thermocouple"], tc["temp"]))
		filer.close()
		# print("LOG: This is the current ThermoCouple Reading")
		# print("commented out because it was too much data")
		# for tc in data['tcList']:
		# 	print("LOG: TC: {} == {}(k)".format(tc['Thermocouple'],tc['temp']))

	@staticmethod
	def logThermalProfile(data):
		'''
		{
			"zone": 1,
			"average": 1,
			"thermocouples": [1, 2, 3, 4, 5],
			"thermalprofiles":
			[
					{
				  "thermalsetpoint": 0,
				  "tempgoal": 10,
				  "ramp": 10,
				  "soakduration": 1
				},
				{
				  "thermalsetpoint": 1,
				  "tempgoal": 5,
				  "ramp": 5,
				  "soakduration": 1
				},
				{
				  "thermalsetpoint": 2,
				  "tempgoal": 7,
				  "ramp": 5,
				  "soakduration": 1
				}
			]
		},
		{
			"zone": 2,
			"average": 2,
			"thermocouples": [6, 7, 8, 9, 10],
			"thermalprofiles":[
			{
			    "thermalsetpoint": 0,
			    "tempgoal": 5,
			    "ramp": 10,
			    "soakduration": 1
			},
			{
				"thermalsetpoint": 1,
				  "tempgoal": 10,
				"ramp": 5,
				"soakduration": 1
			}, {
				"thermalsetpoint": 2,
				"tempgoal": 5,
				"ramp": 1,
				"soakduration": 1
				}
			]
		}
		'''
		# Prints are here for testing
		print("LOG: This is the current ThermalProfile")
		for zone in data['profiles']:
			print("LOG: zone {}".format(zone['zone']))
			print("LOG: thermocouples {}".format(zone['thermocouples']))
			print("LOG: thermalprofiles...")
			for setpoint in zone['thermalprofiles']:
				print("LOG: setpoint: {}".format(setpoint))

        # commenting out while testing
        # MySQlConnect.pushProfile()