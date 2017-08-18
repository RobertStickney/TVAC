from ThreadControls.ThreadCollection import ThreadCollection

from HouseKeeping.globalVars import debugPrint

class ThreadCollectionInstance:
    # Here will be the instance stored.
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if ThreadCollectionInstance.__instance == None:
            ThreadCollectionInstance()
        return ThreadCollectionInstance.__instance

    def __init__(self):
        if ThreadCollectionInstance.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            debugPrint(2,"Creating ThreadCollectionInstance")
            self.threadCollection = ThreadCollection()
            ThreadCollectionInstance.__instance = self