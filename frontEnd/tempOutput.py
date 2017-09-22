import time
import pymysql

from warnings import filterwarnings

class MySQlConnect:


    def __init__(self):
        user = "tvac_user"
        host = "localhost"
        password = "Go2Mars!"
        database = "tvac"

        filterwarnings('ignore', category = pymysql.Warning)
        self.conn = pymysql.connect(host=host, user=user, passwd=password, db=database)
        self.cur = self.conn.cursor(pymysql.cursors.DictCursor)

        

def main():

    mysql = MySQlConnect()
    # These two can be combined into one sql statement...if I have time look into that
    sql = "SELECT * FROM tvac.Real_Temperture ORDER BY time DESC LIMIT 1;"
    mysql.cur.execute(sql)
    mysql.conn.commit()
    profile_I_ID = mysql.cur.fetchone()["profile_I_ID"]
    sql = "SELECT * FROM tvac.Real_Temperture WHERE profile_I_ID=\"{}\";".format(profile_I_ID)

    mysql.cur.execute(sql)
    mysql.conn.commit()
    for row in mysql.cur:
        print("{},{},{},zone".format(row["time"],row["thermocouple"],row["temperture"]))

if __name__ == '__main__':
	main()