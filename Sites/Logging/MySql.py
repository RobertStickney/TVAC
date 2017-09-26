import time
import os
import pymysql

from warnings import filterwarnings

class MySQlConnect:


    def __init__(self):
        userName = os.environ['LOGNAME']
        if "root" in userName:
            user = "TVAC_Admin"
            host = "192.168.99.10"
            password = "People 2 Space"
        else:
            user = "tvac_user"
            host = "localhost"
            password = "Go2Mars!"
        database = "tvac"

        filterwarnings('ignore', category = pymysql.Warning)
        self.conn = pymysql.connect(host=host, user=user, passwd=password, db=database)
        self.cur = self.conn.cursor(pymysql.cursors.DictCursor)

        

if __name__ == '__main__':
    mysql = MySQlConnect()


    sql = "SELECT * FROM tvac.Real_Temperture ORDER BY time DESC LIMIT 1;"
    # print(sql)

    mysql.cur.execute(sql)
    mysql.conn.commit()

    # Profile_Instance
    # print(mysql.cur.fetchone()["profile_I_ID"])
    profile_I_ID = mysql.cur.fetchone()["profile_I_ID"]
    sql = "SELECT * FROM tvac.Real_Temperture WHERE profile_I_ID=\"{}\";".format(profile_I_ID)

    mysql.cur.execute(sql)
    mysql.conn.commit()
    for row in mysql.cur:
        print("{},{},{},zone".format(row["time"],row["thermocouple"],row["temperture"]))