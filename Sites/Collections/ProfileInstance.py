from Collections.ZoneCollection import ZoneCollection
from Logging.Logging import Logging
from Logging.MySql import MySQlConnect


class ProfileInstance:
    # Here will be the instance stored.
    __instance = None

    @staticmethod
    def getInstance():
        """ Static access method. """
        if ProfileInstance.__instance == None:
            ProfileInstance()
        return ProfileInstance.__instance

    def __init__(self):
        if ProfileInstance.__instance != None:
            raise Exception("This class is a singleton!")
        else:
            Logging.logEvent("Debug","Status Update", 
                {"message": "Creating ProfileInstance",
                 "level":2})
            self.zoneProfiles = ZoneCollection(self)



            # System Wide stats
            self.activeProfile = False
            self.vacuumWanted = False
            self.currentSetpoint = None
            self.recordData = False
            self.inRamp = False
            self.inHold = False
            self.inPause = False

            self.getStatusFromDB()            

            self.systemStatusQueue = []
            
            ProfileInstance.__instance = self

    def getStatusFromDB(self):
        sql = "SELECT * FROM tvac.System_Status;"
        mysql = MySQlConnect()
        try:
            mysql.cur.execute(sql)
            mysql.conn.commit()
        except Exception as e:
            Logging.debugPrint(3,"sql: {}".format(sql))
            Logging.debugPrint(1, "Error in profileInstance, getStatus: {}".format(str(e)))
            if Logging.debug:
                raise e

        results = mysql.cur.fetchone()
        self.inHold = results["in_hold"]
        self.inPause = results["in_pause"]
        self.inRamp = results["in_ramp"]
        self.recordData = results["record_data"]
        self.vacuumWanted = results["vacuum_wanted"]
        self.setpoint = results["setpoint"]
