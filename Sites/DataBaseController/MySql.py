import time
import pymysql


class MySQlConnect:

    @staticmethod
    def pushProfile():
        from DataContracts.ProfileInstance import ProfileInstance
        profile = ProfileInstance.getInstance()
        conn = pymysql.connect(host='localhost', user='root', passwd='mysql', db='Cryogenics')
        cur = conn.cursor()
        sql = "insert into profiles (jdoc,profileUUID) values ('%s','%s');"%(profile.zoneProfiles.getJson(),profile.zoneProfiles.profileUUID)
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def pushEvent(data):
        from DataContracts.ProfileInstance import ProfileInstance
        profile = ProfileInstance.getInstance()
        conn = pymysql.connect(host='localhost', user='root', passwd='mysql', db='Cryogenics')
        cur = conn.cursor()
        sql = "insert into events (jdoc) values ('%s');" % data

        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()

    @staticmethod
    def pushError(data):
        from DataContracts.ProfileInstance import ProfileInstance
        profile = ProfileInstance.getInstance()
        conn = pymysql.connect(host='localhost', user='root', passwd='mysql', db='Cryogenics')
        cur = conn.cursor()
        sql = "insert into errors (jdoc) values ('%s');" % data

        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
