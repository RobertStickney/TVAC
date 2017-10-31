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

		d=np.array(pdata_csv["time"])
		e=np.array(pdata_csv["guage"])
		f=np.array(pdata_csv["pressure"])
		#print(np.size(d), np.size(e),np.size(f))
		#print(results)
		df2 = pd.DataFrame({"time" : d, "guage" : e, "pressure": f})
		df2=df2[['time','guage','pressure']]
		df2.to_csv(pressure_file, index=False)


	for time_value in sorted(results):

		time_values.append(dates.date2num(datetime.strptime(str(time_value),'%Y-%m-%d %H:%M:%S')))
		for thermocouple in results[time_value]:
			tmp = tc_data.get(thermocouple[0], [])
			tmp.append(thermocouple[1])
			tc_data[thermocouple[0]] = tmp

	for time_value in sorted(pressure):

		utc_epoch = calendar.timegm(time.strptime(str(time_value),'%Y-%m-%d %H:%M:%S'))

#		if utc_epoch < 1509472800:
#			ptime_values.append(dates.date2num(datetime.strptime(str(time_value),'%Y-%m-%d %H:%M:%S')))
		
		ptime_values.append(dates.date2num(datetime.strptime(str(time_value),'%Y-%m-%d %H:%M:%S')))

		for guage in pressure[time_value]:
			#print(pressure[time_value])
			tmp = guage_data.get(guage[0], [])
			tmp.append(guage[1])
			guage_data[guage[0]] = tmp

	#data=data.decode('utf-8')



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
		try:
			ax2.plot(ptime_values,guage_data[guage],'.', label=str(guage))
			ax2.set_yscale('log')
			ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M:%S'))
			plt.gcf().autofmt_xdate()
		except:
			print("Pressure Plotting Error")

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