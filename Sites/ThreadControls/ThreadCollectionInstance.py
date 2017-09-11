from ThreadControls.ThreadCollection import ThreadCollection

from Logging.Logging import Logging

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
            Logging.logEvent("Debug","Status Update", 
                {"message": "Creating ThreadCollectionInstance",
                 "level":2})
            self.threadCollection = ThreadCollection()
            ThreadCollectionInstance.__instance = self