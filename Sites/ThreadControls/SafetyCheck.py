from threading import Thread
import time
import os

from DataContracts.HardwareStatusInstance import HardwareStatusInstance

from HouseKeeping.globalVars import debugPrint

class SafetyCheck(Thread):
	"""
	docstring for SafetyCheck
	"""
	__instance = None



	def __init__(self):
		if SafetyCheck.__instance != None:
			raise Exception("This class is a singleton!")
		else:
			debugPrint(2,"Creating SafetyCheck")
			SafetyCheck.__instance = self
			super(SafetyCheck, self).__init__()

	def run(self):
		# some start up stuff here
		MAX_TEMP_FOR_TC = 1
		MIN_TEMP_FOR_TC = -1
		SLEEP_TIME = 1 # in seconds
		
		hardwareStatusInstance = HardwareStatusInstance.getInstance()

		# stop when the program ends
		while os.getppid() != 1: 
			TCs = hardwareStatusInstance.Thermocouples.tcList
			for tc in TCs:
				# if there are any TC's higher than max temp
				if tc.temp > MAX_TEMP_FOR_TC:
					print("TC # {} is too hot at temp {}".format(tc.Thermocouple,tc.temp))
				if tc.temp < MIN_TEMP_FOR_TC:
					print(tc.temp)

			# Check if heaters turned on, start timer, wait 30 (x) seconds and checp temp
			# if no change in temp, send error

			


			time.sleep(SLEEP_TIME)


