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
import pandas as pd
from operator import itemgetter

import calendar
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

def getLiveTempFromDB(startingPoint,endingPoint,time_start):
	mysql = MySQlConnect()
	sql = "SELECT * FROM tvac.real_temperature WHERE (time > \"{}\") AND (time<\"{}\");".format(startingPoint,endingPoint)

	mysql.cur.execute(sql)
	mysql.conn.commit()

	time_two=time.time()
	#print("Time to Query (s): ",time_two-time_start)

	data_csv = dict(time=[],thermocouple=[],temperature=[])
	results={}
	for row in mysql.cur:
		
		tmp=dates.date2num(datetime.strptime(str(row["time"]),'%Y-%m-%d %H:%M:%S'))
		data_csv["time"].append(tmp)
		data_csv["thermocouple"].append(row["thermocouple"])
		data_csv["temperature"].append(float(row["temperature"]))

		tmp = results.get(row["time"], [])
		tmp.append([row["thermocouple"], float(row["temperature"])])
		results[row['time']] = tmp

	return "Temp since {}".format(startingPoint), results, data_csv

def getPressureDataFromDB(startingPoint,endingPoint):
	mysql = MySQlConnect()
	# These two can be combined into one sql statement...if I have time look into that
	sql = "SELECT * FROM tvac.Pressure WHERE (time > \"{}\") AND (time<\"{}\");".format(startingPoint,endingPoint)	
	mysql.cur.execute(sql)
	mysql.conn.commit()

	data_csv = dict(time=[],guage=[],pressure=[])
	results = {}
	for row in mysql.cur:

		tmp=dates.date2num(datetime.strptime(str(row["time"]),'%Y-%m-%d %H:%M:%S'))
		data_csv["time"].append(tmp)
		data_csv["guage"].append(row["guage"])
		data_csv["pressure"].append(float(row["pressure"]))

		tmp = results.get(row["time"], [])
		tmp.append([row["guage"], float(row["pressure"])])
		results[row['time']] = tmp
		#print("{},{},{},zone".format(row["time"],row["guage"],row["pressure"]))
	#print(results)
	return results, data_csv	

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
	time_start=time.time()

	startTime = args[1]
	endTime = args[2]

	if len(args)>4:
		temp_file=args[3]
		pressure_file=args[4]

	#print(args[1])
	#print(args[2])
	print("Querying Temperatures...")
	profile_I_ID, results, tdata_csv = getLiveTempFromDB(startTime,endTime,time_start)
	print("Querying Pressures...")
	pressure, pdata_csv=getPressureDataFromDB(startTime,endTime)

	# print(results)
	time_values = []
	ptime_values = []

	tc_data = {}
	guage_data = {}	
	#firstTime = sorted(results)[0]

	print("Time to Pressure End ",time.time()-time_start)

	if len(args)>4:
		a=np.array(tdata_csv["time"])
		b=np.array(tdata_csv["thermocouple"])
		c=np.array(tdata_csv["temperature"])
		#print(results)
		df = pd.DataFrame({"time" : a, "thermocouple" : b, "temperature": c})
		df=df[['time','thermocouple','temperature']]
		df.to_csv(temp_file, index=False)

	pTime=np.array(pdata_csv["time"])
	pGuage=np.array(pdata_csv["guage"])
	pPressure=np.array(pdata_csv["pressure"])
		#print(np.size(d), np.size(e),np.size(f))
		#print(results)
	if len(args)>4:
		df2 = pd.DataFrame({"time" : pTime, "guage" : pGuage, "pressure": pPressure})
		df2=df2[['time','guage','pressure']]
		df2.to_csv(pressure_file, index=False)


	for time_value in sorted(results):

		time_values.append(dates.date2num(datetime.strptime(str(time_value),'%Y-%m-%d %H:%M:%S')))
		for thermocouple in results[time_value]:
			tmp = tc_data.get(thermocouple[0], [])
			tmp.append(thermocouple[1])
			tc_data[thermocouple[0]] = tmp

# 	for time_value in sorted(pressure):

# 		utc_epoch = calendar.timegm(time.strptime(str(time_value),'%Y-%m-%d %H:%M:%S'))

# #		if utc_epoch < 1509472800:
# #			ptime_values.append(dates.date2num(datetime.strptime(str(time_value),'%Y-%m-%d %H:%M:%S')))
		
# 		ptime_values.append(dates.date2num(datetime.strptime(str(time_value),'%Y-%m-%d %H:%M:%S')))

# 		for guage in pressure[time_value]:
# 			#print(pressure[time_value])
# 			tmp = guage_data.get(guage[0], [])
# 			tmp.append(guage[1])
# 			guage_data[guage[0]] = tmp
	master_pressure=[pTime,pGuage,pPressure]

	guage1=np.empty([2,len(pTime)])
	guage2=np.empty([2,len(pGuage)])
	guage3=np.empty([2,len(pPressure)])
	master_pressure=sorted(master_pressure,key=itemgetter(0))

	for time_value in range(0,len(pTime)):
		if pGuage[time_value] == 1:
			guage1[0,time_value] = pTime[time_value]
			guage1[1,time_value] = pPressure[time_value]
		if pGuage[time_value] == 2:
			guage2[0,time_value] = pTime[time_value]
			guage2[1,time_value] = pPressure[time_value]
		if pGuage[time_value] == 3:
			guage3[0,time_value] = pTime[time_value]
			guage3[1,time_value] = pPressure[time_value]


	fig,(ax1,ax2)=plt.subplots(1,2,figsize=(9,7))

	for tc in tc_data:
		#if tc in importantTCs:
		ax1.plot_date(time_values,tc_data[tc], '.',label=str(tc))
		ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M:%S'))
		plt.gcf().autofmt_xdate()
		length=len(tc_data[tc])
		#print(tc)


	ax2.plot(guage1[0,:],guage1[1,:],'.', label=str('Guage 1'))
	ax2.plot(guage2[0,:],guage2[1,:],'.', label=str("Guage 2"))
	ax2.plot(guage3[0,:],guage3[1,:],'.', label=str("Guage 3"))
	ax2.set_yscale('log')
	#ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M:%S'))
	plt.gcf().autofmt_xdate()


	keys = tc_data.keys()

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