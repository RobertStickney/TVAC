 #!/usr/bin/env python3
from Testing_mmap import TS_Registers

class PC_104_Instance:
    # Here will be the instance stored.
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if PC_104_Instance.__instance == None:
            PC_104_Instance()
        return PC_104_Instance.__instance

    def __init__(self):
        if PC_104_Instance.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            self.digIO = TS_Registers()
            PC_104_Instance.__instance = self