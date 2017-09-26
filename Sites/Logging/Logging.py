from Logging.MySql import MySQlConnect
import math
import datetime

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
				Logging.logLiveTempertureData(data)
			elif "Expected Temp Update" in logType:
				Logging.logExpectedTempertureData(data)
			elif "Thermal Profile Update" in logType:
				Logging.logThermalProfile(data)

			try:
				systemStatusQueue = data["ProfileInstance"].systemStatusQueue
				systemStatusQueue.append("[ '{}','{}', '{}' ]".format(category,logType, data.get("thread")))
			except Exception as e:
				print("pass")
				# raise e
			coloums = "( event_type, details )"
			values = "( \"{}\",\"{}\" )".format(category,logType)
			sql = "INSERT INTO tvac.Event {} VALUES {};".format(coloums, values)
			mysql = MySQlConnect()
			mysql.cur.execute(sql)
			mysql.conn.commit()
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
				coloums = "( message, time )"
				values = "( \"{}\",\"{}\" )".format("{}{}".format(prefix,string),time.time())
				sql = "INSERT INTO tvac.Debug {} VALUES {};".format(coloums, values)
				# print(sql)
				mysql = MySQlConnect()
				try:
					mysql.cur.execute(sql)
					mysql.conn.commit()
				except Exception as e:
					pass
				with open('./debugLog.txt','a') as filer:
					for line in string.split("\n"):
						filer.write("{}{}".format(prefix,line)+"\n")
						print("{}{}".format(prefix,line))

	@staticmethod
	def logExpectedTempertureData(data):
		'''
		data = {
	  		 "expected_temp_values": expected_temp_values,
	         "expected_time_values": expected_time_values,
	         "Zone"                : self.args[0],
	         "profileUUID"         : self.zoneProfile.profileUUID,
		'''
		expected_temp_values = data["expected_temp_values"]
		expected_time_values = data["expected_time_values"]
		zone 				 = data["zone"]
		profile 			 = data["profileUUID"]

		print("expected_temp_values")
		coloums = "( profile_I_ID, time, zone, temperture )"
		values = ""
		for i in range(len(expected_temp_values)):
			time = expected_time_values[i]
			time = datetime.datetime.fromtimestamp(time)

			temperture = expected_temp_values[i]
			values += "( \"{}\", \"{}\", {}, {} ),\n".format(profile, time.strftime('%Y-%m-%d %H:%M:%S'), int(zone[4:]), temperture)

		sql = "INSERT INTO tvac.Expected_Temperture {} VALUES {};".format(coloums, values[:-2])

		mysql = MySQlConnect()
		try:
			mysql.cur.execute(sql)
			mysql.conn.commit()
		except Exception as e:
			raise e


	@staticmethod
	def logLiveTempertureData(data):
		'''
		data = {
			"time":		TCs['time'],
			"tcList":	TCs['tcList'],
			"ProfileUUID": ProfileUUID,
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

		time = data["time"]
		profile = data["profileUUID"]
		coloums = "( profile_I_ID, time, thermocouple, temperture )"
		values = ""

		for tc in data['tcList']:
			thermocouple = tc["Thermocouple"]
			temperture = tc["temp"]
			if math.isnan(tc["temp"]):
				continue
			values += "( \"{}\", \"{}\", {}, {} ),\n".format(profile, time.strftime('%Y-%m-%d %H:%M:%S'), thermocouple, temperture)
		sql = "INSERT INTO tvac.Real_Temperture {} VALUES {};".format(coloums, values[:-2])
		
		sql.replace("nan", "NULL")
		mysql = MySQlConnect()
		try:
			mysql.cur.execute(sql)
			mysql.conn.commit()
		except Exception as e:
			raise e


	@staticmethod
	def logThermalProfile(data):
		'''
		{
			"name": "demo"
			"zone": 1,
			"average": Maz,
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
		# print(data["zoneProfile"])
		# print(data["profileUUID"])
		# for i in data:
		# 	print(i)
		# print("LOG: This is the current ThermalProfile")

		
