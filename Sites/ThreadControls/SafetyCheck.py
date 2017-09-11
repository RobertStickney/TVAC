from threading import Thread
import time
from datetime import datetime
import os

from Collections.HardwareStatusInstance import HardwareStatusInstance

from Logging.Logging import Logging


class SafetyCheck(Thread):
	"""
	SafetyCheck is the thread that runs the sainty and safety checks over the system. 
	If it finds anything wrong with the the system it makes an error report and stores it in a queue 
	to be seen by the client. 
	"""
	__instance = None





	def __init__(self,parent):
		if SafetyCheck.__instance != None:
			raise Exception("This class is a singleton!")
		else:
			Logging.logEvent("Debug","Status Update", 
				{"message": "Creating SafetyCheck",
				 "level":2})
			self.errorList = []
			self.errorDict = {
				"System Alarm: High Temperature": False,
				"Product Saver Alarm: High Temperature": False,
				"Product Saver Alarm: Low Temperature": False,
				"Human Touch Alarm: High Temperature": False,
				"Human Touch Alarm: Low Temperature": False
			}

			SafetyCheck.__instance = self
			self.parent = parent
			super(SafetyCheck, self).__init__()

			self.heartbeats={
			"TsRegistersControlStub":time.time(),
			"ThermoCoupleUpdater":time.time(),
			}

	def run(self):
		# some start up stuff here
		# Temps are in Celsius
		MAX_OPERATING_TEMP = 151
		# safe at all lower bounds
		# MIN_OPERATING_TEMP 

		MAX_TOUCH_TEMP = 318.15
		MIN_TOUCH_TEMP = 269.15

		# TODO, make this user defined
		# These are test values, they will change when the code is written to change them
		MAX_UUT_TEMP = 363.15 
		MIN_UUT_TEMP = 224.15

		SLEEP_TIME = 1 # in seconds
		
		hardwareStatusInstance = HardwareStatusInstance.getInstance()

		Logging.logEvent("Debug","Status Update", 
				{"message": "Starting Safety Checker Thread",
				 "level":3})
		# stop when the program ends
		while True: 
			Logging.logEvent("Debug","Status Update", 
			{"message": "Running Safety Checker Thread",
			 "level":4})

			tempErrorDict = {
				"System Alarm: High Temperature": False,
				"Product Saver Alarm: High Temperature": False,
				"Product Saver Alarm: Low Temperature": False,
				"Human Touch Alarm: High Temperature": False,
				"Human Touch Alarm: Low Temperature": False
			}


			TCs = hardwareStatusInstance.Thermocouples.tcList
			for tc in TCs:
				# if there are any TC's higher than max temp
				if tc.temp > MAX_OPERATING_TEMP:
					errorDetail = "TC # {} is above MAX_OPERATING_TEMP ({}). Currently {}c".format(tc.Thermocouple,MAX_OPERATING_TEMP,tc.temp)
					error = {
						"time" : datetime.now(),
						"event":"System Alarm: High Temperature",
						"Thermocouple": tc.Thermocouple,
						"details": errorDetail,
						"actions": ["Turned off heater", "Log Event"]
						}
					errorInList = False
					for tempError in self.errorList:
						if error["event"] == tempError["event"]:
							if error["Thermocouple"] == tempError["Thermocouple"]:
								errorInList = True

					if not errorInList: 
						self.logEvent(error)
						tempErrorDict[error['event']] = True

				if tc.userDefined:
					if tc.temp > MAX_UUT_TEMP:
						errorDetail = "TC # {} is above MAX_UUT_TEMP ({}). Currently {}c".format(tc.Thermocouple,MAX_UUT_TEMP,tc.temp)
						error = {
							"time" : datetime.now(),
							"event":"Product Saver Alarm: High Temperature",
							"Thermocouple": tc.Thermocouple,
							"details": errorDetail,
							"actions": ["Turned off heater", "Log Event"]
							}
						self.logEvent(error)
						tempErrorDict[error['event']] = True

					if tc.temp < MIN_UUT_TEMP:
						errorDetail = "TC # {} is below MIN_UUT_TEMP ({}). Currently {}c".format(tc.Thermocouple,MIN_UUT_TEMP,tc.temp)
						error = {
							"time" : datetime.now(),
							"event":"Product Saver Alarm: Low Temperature",
							"Thermocouple": tc.Thermocouple,
							"details": errorDetail,
							"actions": ["Turned off LN flow", "Log Event"]
							}
						self.logEvent(error)
						tempErrorDict[error['event']] = True
				
				if tc.temp > MAX_TOUCH_TEMP:
					errorDetail = "TC # {} is above MAX_TOUCH_TEMP ({}). Currently {}c".format(tc.Thermocouple,MAX_TOUCH_TEMP,tc.temp)
					error = {
						"time" : datetime.now(),
						"event":"Human Touch Alarm: High Temperature",
						"Thermocouple": tc.Thermocouple,
						"details": errorDetail,
						"actions": ["Log Event"]
						}
					self.logEvent(error)
					tempErrorDict[error['event']] = True

				if tc.temp < MIN_TOUCH_TEMP:
					errorDetail = "TC # {} is below MIN_TOUCH_TEMP ({}). Currently {}c".format(tc.Thermocouple,MIN_TOUCH_TEMP,tc.temp)
					error = {
						"time" : datetime.now(),
						"event":"Human Touch Alarm: Low Temperature",
						"Thermocouple": tc.Thermocouple,
						"details": errorDetail,
						"actions": ["Log Event"]
						}
					self.logEvent(error)
					tempErrorDict[error['event']] = True
			# End of TC for loop

			for errorType in self.errorDict:
				# for every type of error
				if self.errorDict[errorType] and not tempErrorDict[errorType]:
					# It was true and now is not, log it. 

					# make a event log
					errorLog = {
						"time" : datetime.now(),
						"event": errorType,
						"Thermocouple": tc.Thermocouple,
						"details": "The current event has ended",
						"actions": ["Log Event"]
						}
					self.logEvent(errorLog)
						

			self.errorDict = tempErrorDict

			# Check if heaters turned on, start timer, wait 30 (x) seconds and check temp
			# if no change in temp, send error

			# for hb in self.heartbeats:
			# 	if time.time() - self.heartbeats[hb] > 5:
			# 		# self.parent.hardwareInterfaceThreadDict[hb].start()
			# 		print("ERROR: in {}".format(hb))


			time.sleep(SLEEP_TIME)
		# end of while true loop


	def logEvent(self, error):
		errorInList = False
		if self.errorList:
			for tempError in self.errorList:
				if error["event"] == tempError["event"]:
					if error["Thermocouple"] == tempError["Thermocouple"]:
						errorInList = True

		if not errorInList: 
			debugPrint(1, error["details"])
			self.errorList.append(error)
			# print(self.errorList)

		Logging.logEvent("Error","", 
			{"message": "Running Safety Checker Thread",
			 "level":3})
		# Not sure what to do with this
		if not self.errorDict[error["event"]]:
			# The error has not been on, and is now on
			# Log SQL stuff 
			pass
