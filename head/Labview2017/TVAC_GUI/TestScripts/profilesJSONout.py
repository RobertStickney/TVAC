#import matplotlib.pyplot as plt
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
			userName="user"
		if "root" in userName or (len(sys.argv) > 1 and sys.argv[1] =="--live"):
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


def getProfilesfromDB():
	mysql = MySQlConnect()
	sql = "SELECT DISTINCT profile_name FROM tvac.Thermal_Profile"


	mysql.cur.execute(sql)
	mysql.conn.commit()
	results = []
	for row in mysql.cur:
		results.append(row["profile_name"])
		# print("{},{},{},zone".format(row["time"],row["thermocouple"],row["temperature"]))
	return results

def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


def main(args):
	# Get live data
	results = getProfilesfromDB()
	profiles = []
	# tc_data = {}
	# if results:
	# 	firstTime = sorted(results)[0]
	# 	for profile in sorted(results):
	# 		profiles.append()
			# time_values.append(utc_to_local(time_value))
			# time_values.append(time_value)
			# print("{} -> {}".format(time_value, results[time_value]))
			# for thermocouple in results[time_value]:
			# 	tmp = tc_data.get(thermocouple[0], [])
			# 	tmp.append(thermocouple[1])
			# 	tc_data[thermocouple[0]] = tmp
		# print("time,tc,temp")
		# for i, time in enumerate(time_values):
		# 	for tc in tc_data:
		# 		print("{},{},{}".format(time_values[i],tc,tc_data[tc][i]))

	# out = {"time_values:":str(time_values),
	# 		"tc_data": tc_data}
	print(JSON.dumps(results))


if __name__ == '__main__':
	main(sys.argv)