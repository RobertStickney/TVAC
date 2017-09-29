import matplotlib.pyplot as plt
import time
import sys
import random
import os
import pymysql
from warnings import filterwarnings

class MySQlConnect:


	def __init__(self):
		userName = os.environ['LOGNAME']
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


def getDataFromDB():
	mysql = MySQlConnect()
	# These two can be combined into one sql statement...if I have time look into that
	sql = "SELECT * FROM tvac.Pressure ORDER BY time DESC LIMIT 1;"
	mysql.cur.execute(sql)
	mysql.conn.commit()
	profile_I_ID = mysql.cur.fetchone()["profile_I_ID"]
	sql = "SELECT * FROM tvac.Pressure WHERE profile_I_ID=\"{}\";".format(profile_I_ID)

	mysql.cur.execute(sql)
	mysql.conn.commit()
	results = {}
	for row in mysql.cur:
		print(row)
		tmp = results.get(row["time"], [])
		tmp.append([row["guage"], float(row["pressure"])])
		results[row['time']] = tmp
		print("{},{},{},zone".format(row["time"],row["guage"],row["pressure"]))
	print(results)
	return results


def createExpectedValues(setPoints,startTime=None):
	intervalTime = 5
	if startTime:
		currentTime = int(startTime)
	else:
		currentTime = int(time.time())
	currentTemp = 300
	expected_temp_values = []
	expected_time_values = []
	for setPoint in setPoints:
		goalTemp = setPoint["goalTemp"]
		rampTime = setPoint["rampTime"]
		soakTime = setPoint["soakTime"]


		# rampTime = int(abs(currentTemp-goalTemp)*(1.2*60))
		TempDelta = goalTemp-currentTemp
		numberOfJumps = rampTime/intervalTime
		intervalTemp = TempDelta/numberOfJumps
		rampEndTime = currentTime+rampTime

		# Debug prints
		print("currentTime: {}".format(currentTime))
		print("rampTime: {}".format(rampTime))
		print("TempDelta: {}".format(TempDelta))
		print("soakTime: {}".format(soakTime))
		print("numberOfJumps: {}".format(numberOfJumps))
		print("intervalTemp: {}".format(intervalTemp))

		# setting all values all for ramp
		for i, tempSetPoint in enumerate(range(currentTime,rampEndTime, intervalTime)):
			x = tempSetPoint
			y = currentTemp + (i*intervalTemp)
			expected_time_values.append(tempSetPoint)
			expected_temp_values.append(y)
			print("{},{}".format(x,y))

		#Setting all soak values
		for tempSetPoint in range(rampEndTime, rampEndTime+soakTime, intervalTime):
			x = tempSetPoint
			y = goalTemp
			expected_time_values.append(tempSetPoint)
			expected_temp_values.append(y)
		print("{},{}".format(x,y))


		currentTime = rampEndTime+soakTime
		currentTemp = goalTemp

	return expected_temp_values, expected_time_values


def main():

	results = getDataFromDB()
	# return
	time_values = []
	guage_data = {}
	for time_value in sorted(results):
		time_values.append(time_value)
		print("{} -> {}".format(time_value, results[time_value]))
		for guage in results[time_value]:
			tmp = guage_data.get(guage[0], [])
			tmp.append(guage[1])
			guage_data[guage[0]] = tmp
	for guage in guage_data:
		plt.plot(time_values,guage_data[guage], label=str(guage))
	print("Done gathering data")
		# plt.plot(real_time_values,real_temp_values)
	plt.legend(loc='upper left')

	# plt.pause(1)
	# plt.clf()
	plt.ylabel('Pressure')
	plt.xlabel('Time')
	plt.show(block=True)


if __name__ == '__main__':
	main()