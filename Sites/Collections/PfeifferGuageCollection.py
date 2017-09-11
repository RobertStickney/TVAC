from Logging.Logging import Logging

from PfeifferGuage.PfeifferGuage import PfeifferGuage
from DataContracts.PfeifferGuageContract import PfeifferGuageContract

class PfeifferGuageCollection:
	"""
	docstring for PfeifferGuageCollection
	"""
	def __init__(self, num = 3):
		debugPrint(2, "Creating ThermocoupleCollection")
		self.pfGuageList = self.buildCollection(num)
		self.pfeiferGuage = PfeifferGuage()
		
	
	def buildCollection(self, num):
		guages = []
		for i in range(1, num+1):
			guages.append(PfeifferGuageContract(i))
		return guages

	def getPressure(self):
		return self.pfeiferGuage.getPressure


