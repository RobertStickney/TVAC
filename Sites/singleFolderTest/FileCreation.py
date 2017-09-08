import os
import time


class FileCreation:

    @staticmethod
    def pushFile(eventname,dataIdentifier,data):
        fileDir = os.path.dirname(os.path.realpath('__file__'))
        timeCreated = None
        while not timeCreated:
            timeCreated = int(time.time())
        name = '%s.%s.%s.log'%(eventname,dataIdentifier,timeCreated)
        relDir = '/LogFiles/%s'%name
        filename = '%s%s'%(fileDir, relDir)
        file = open(filename,'w')
        file.write(data)
        file.close()
