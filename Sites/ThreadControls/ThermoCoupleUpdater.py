from threading import Thread
import os
import time
from datetime import datetime

from Keysight_34980A import Kesight_34980A_TC_Scan
from HouseKeeping.globalVars import debugPrint

from Collections.HardwareStatusInstance import HardwareStatusInstance

class ThermoCoupleUpdater(Thread):

	"""
	docstring for ThermoCoupleUpdater
	"""
	__instance = None
	def __init__(self):
		if ThermoCoupleUpdater.__instance != None:
			raise Exception("This class is a singleton!")
		else:
			debugPrint(2,"Creating ThermoCoupleUpdater")
			ThermoCoupleUpdater.__instance = self
			self.hardwareStatusInstance = HardwareStatusInstance
			super(ThermoCoupleUpdater, self).__init__()



	def run(self):
			# some start up stuff here
			SLEEP_TIME = 5 # will be 30 seconds
			ipAddr_34980A = '192.168.99.3'
			Channel_List = "(@1001:1020,2036:2040,3001:3040)"
			hwStatus = self.hardwareStatusInstance

			userName = os.environ['LOGNAME']

			if "root" in userName:
				# Hasn't been tested yet
				Tharsis = Kesight_34980A_TC_Scan.Keysight34980A_TC(ipAddr_34980A, ChannelList = Channel_List)
				Tharsis.init_sys()

			# stop when the program ends
			while True: 


				if "root" in userName:
					debugPrint(4,"Pulling live data for TC")
					# Hasn't been tested yet
					TCs = Tharsis.getTC_Values()

				'''
				TCs is a list of dicitations ordered like this....
				{
				  'Thermocouple': tc_num,
	              'time': tc_time_offset,
	              'temp': tc_tempK,
	              'working': tc_working,
                  'alarm': tc_alarm
                 }
                '''
                
                # uncomment if you want to test updating temps
				# TCs = {
				# 	'time': datetime.now(),
				# 	'tcList': [
				# 		{'Thermocouple': 2, 'temp': hwStatus.Thermocouples.getTC(2).getTemp() + 1},
				# 	]
				# }
				hwStatus.Thermocouples.update(TCs)					

				time.sleep(SLEEP_TIME)