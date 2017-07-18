import pymysql

class MySQlConnect:

    @staticmethod
    def pushProfile():
        from DataContracts.ProfileInstance import ProfileInstance
        profile = ProfileInstance.getInstance()
        conn = pymysql.connect(host='localhost', user='root', passwd='mysql', db='Cryogenics')
        cur = conn.cursor()
        sql = "insert into profiles values ('%s');"%profile.zoneProfiles.getJson()

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
        sql = "insert into events values ('%s');" % data

        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
