import matplotlib.pyplot as plt
import time
import sys
import random
import os
import pymysql
from warnings import filterwarnings
import json as JSON
from datetime import datetime
import matplotlib.dates as mdates
from matplotlib import dates
import numpy as np
import csv

import matplotlib

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

def unwrapJSON(json):
	# print(json)
	return json['profiles'][0]['thermalprofiles']

def getLiveTempFromDB(startingPoint,endingPoint):
	mysql = MySQlConnect()
	sql = "SELECT * FROM tvac.real_temperature WHERE (time > \"{}\") AND (time<\"{}\");".format(startingPoint,endingPoint)
	#sql = "SELECT * FROM tvac.real_temperature WHERE (time > \"{}\");".format(startingPoint)
	#print(sql)
	mysql.cur.execute(sql)
	mysql.conn.commit()
	results = {}
	for row in mysql.cur:
		tmp = results.get(row["time"], [])
		tmp.append([row["thermocouple"], float(row["temperature"])])
		results[row['time']] = tmp
		#print("{},{},{}".format(row["time"],row["thermocouple"],row["temperature"]))
	return "Temp since {}".format(startingPoint), results

def getPressureDataFromDB(startingPoint,endingPoint):
	mysql = MySQlConnect()
	# These two can be combined into one sql statement...if I have time look into that
	sql = "SELECT * FROM tvac.Pressure WHERE (time > \"{}\") AND (time<\"{}\");".format(startingPoint,endingPoint)	
	mysql.cur.execute(sql)
	mysql.conn.commit()

	results = {}
	for row in mysql.cur:
		#print(row)
		tmp = results.get(row["time"], [])
		tmp.append([row["guage"], float(row["pressure"])])
		results[row['time']] = tmp
		#print("{},{},{},zone".format(row["time"],row["guage"],row["pressure"]))
	#print(results)
	return results	

def getExpectedFromDB():
	mysql = MySQlConnect()
	# These two can be combined into one sql statement...if I have time look into that
	sql = "SELECT profile_name, startTime, endTime FROM tvac.Profile_Instance WHERE profile_name like \"coldRampAndSoak\";"
	mysql = MySQlConnect()
	try:
		mysql.cur.execute(sql)
		mysql.conn.commit()
	except Exception as e:
		return False

	result = mysql.cur.fetchone()
	if not result:
		return False

	sql = "SELECT * FROM tvac.Expected_Temperature WHERE time>\"{}\";".format(result['startTime'])

	mysql.cur.execute(sql)
	mysql.conn.commit()
	results = {}
	for row in mysql.cur:
		# print(row)
		tmp = results.get(row["time"], [])
		tmp.append([row["zone"], float(row["temperature"])])
		results[row['time']] = tmp
	return result['profile_name'], results

def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


def main(args):

	startTime = args[1]
	endTime = args[2]

	#print(args[1])
	#print(args[2])

	profile_I_ID, results = getLiveTempFromDB(startTime,endTime)
	pressure=getPressureDataFromDB(startTime,endTime)
	# print(results)
	time_values = []
	ptime_values = []

	tc_data = {}
	guage_data = {}	
	#firstTime = sorted(results)[0]
	for time_value in sorted(results):

		time_values.append(dates.date2num(datetime.strptime(str(time_value),'%Y-%m-%d %H:%M:%S')))

		for thermocouple in results[time_value]:
			tmp = tc_data.get(thermocouple[0], [])
			tmp.append(thermocouple[1])
			tc_data[thermocouple[0]] = tmp

	for time_value in sorted(pressure):
		
		ptime_values.append(dates.date2num(datetime.strptime(str(time_value),'%Y-%m-%d %H:%M:%S')))

		for guage in pressure[time_value]:
			tmp = guage_data.get(guage[0], [])
			tmp.append(guage[1])
			guage_data[guage[0]] = tmp	
	#print("time,tc,temp")
	# for i, time in enumerate(time_values):
	# 	for tc in tc_data:
	# 		print("{},{},{}".format(time_values[i],tc,tc_data[tc][i]))
	fig,(ax1,ax2)=plt.subplots(1,2,figsize=(9,7))

	for tc in tc_data:
		#if tc in importantTCs:
		ax1.plot_date(time_values,tc_data[tc], '.',label=str(tc))
		ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M:%S'))
		plt.gcf().autofmt_xdate()
		length=len(tc_data[tc])
		#print(tc)

	for guage in guage_data:
		ax2.plot(ptime_values,guage_data[guage],'.', label=str(guage))
		ax2.set_yscale('log')
		ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M:%S'))
		plt.gcf().autofmt_xdate()	

	keys = tc_data.keys()

	print(length)

	print(len(keys))

	outputData=np.empty([len(keys),length,2])
	increment=0
	for tc in tc_data:
		for j in range(0,length):
			outputData[increment,j,0]=time_values[j]
			temp=tc_data[tc]
			outputData[increment,j,1]=temp[j]

		increment+=1	

	# print(outputData)

	# temp=outputData.reshape(1,length*len(keys)*2)
	# print(temp)

	# np.savetxt('test.csv',temp,fmt='%5s',delimiter=',')

	ax1.legend()
	ax2.legend()
	#ax1.legend(bbox_to_anchor=(-.01, 0, 1, 1), bbox_transform=plt.gcf().transFigure)

	ax1.set_ylabel('Temperature [K]')
	ax1.set_xlabel('Time')	
	ax1.set_title(profile_I_ID)

	ax2.set_ylabel('Pressure [Torr]')
	ax2.set_xlabel('Time')
	ax2.set_title("Pressure")


	#plt.savefig('graph1.png')
	plt.show()

if __name__ == '__main__':
	main(sys.argv)