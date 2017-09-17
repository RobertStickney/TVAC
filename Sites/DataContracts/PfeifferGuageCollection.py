import time
import math
from datetime import datetime
from DataContracts.PfeifferGuageContract import PfeifferGuageContract

class PfeifferGuageCollection:

    def __init__(self):
        self.time = datetime.now()


        pass #fill this in

    def getParmValues(self, Address):
        ParmDict = {"041": self.Pfeiffer_GenCmdRead(Address, Parm=41),
                    "049": self.Pfeiffer_GenCmdRead(Address, Parm=49),
                    "303": self.Pfeiffer_GenCmdRead(Address, Parm=303),
                    "312": self.Pfeiffer_GenCmdRead(Address, Parm=312),
                    "349": self.Pfeiffer_GenCmdRead(Address, Parm=349),
                    "730": self.Pfeiffer_GenCmdRead(Address, Parm=730),
                    "732": self.Pfeiffer_GenCmdRead(Address, Parm=732),
                    "740": self.Pfeiffer_GenCmdRead(Address, Parm=740),
                    "741": self.Pfeiffer_GenCmdRead(Address, Parm=741),
                    "742": self.Pfeiffer_GenCmdRead(Address, Parm=742)}
        return ParmDict

    def getPressureValue(self, Address):
        PressureDict = {"pressure": self.Pfeiffer_GenCmdRead(Address, Parm=740)}
        return PressureDict
