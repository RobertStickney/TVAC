import time
import sys
import random
import os
import pymysql
from warnings import filterwarnings
import json as JSON
from datetime import timezone

class MySQlConnect:


	def __init__(self):
		if os.name == "posix":
			userName = os.environ['LOGNAME']
		else:
			userName=os.getlogin()
		if "admin" in userName or (len(sys.argv) > 1 and sys.argv[1] =="--live"):
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


def renameProfile(oldName,newName):
	mysql = MySQlConnect()
	affected_rows = 0
	sql = "UPDATE tvac.Thermal_Profile SET profile_name=\"{}\" WHERE profile_name=\"{}\"".format(newName,oldName)
	affected_rows += mysql.cur.execute(sql)
	mysql.conn.commit()
	sql = "UPDATE tvac.Profile_Instance SET profile_name=\"{}\" WHERE profile_name=\"{}\"".format(newName,oldName)
	affected_rows += mysql.cur.execute(sql)
	mysql.conn.commit()
	sql = "UPDATE tvac.TC_Profile SET profile_name=\"{}\" WHERE profile_name=\"{}\"".format(newName,oldName)
	affected_rows += mysql.cur.execute(sql)
	mysql.conn.commit()
	sql = "UPDATE tvac.Thermal_Zone_Profile SET profile_name=\"{}\" WHERE profile_name=\"{}\"".format(newName,oldName)
	affected_rows += mysql.cur.execute(sql)
	mysql.conn.commit()
	# results = []
	# for row in mysql.cur:
	# 	results.append(row["profile_name"])
	# 	# print("{},{},{},zone".format(row["time"],row["thermocouple"],row["temperature"]))
	return affected_rows

def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


def main(args):
	# Get live data
	oldName = None
	newName = None
	if len(args) > 1:
		oldName = args[1]
		if len(args) > 2: 
			newName = args[2]
	if not oldName or not newName:
		print(JSON.dumps({"Error":"Input not given"}))
		quit()
	affected_rows = renameProfile(oldName,newName)
	if affected_rows != 0:
		out = "Successfully changed name to: " + str(newName)
	else:
		out = "Error while renaming profile " + str(oldName) + " to " +str(newName)
	print(JSON.dumps(out))


if __name__ == '__main__':
	main(sys.argv)