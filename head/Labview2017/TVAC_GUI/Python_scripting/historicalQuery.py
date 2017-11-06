import matplotlib
import matplotlib.pyplot as plt
import time
import sys
import os
import pymysql
from warnings import filterwarnings
import json as JSON
from datetime import datetime, timezone
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
from operator import itemgetter

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

def getLiveTempFromDB(startingPoint,endingPoint,time_start,tcSelection):
	data_csv = dict(time=[],thermocouple=[],temperature=[])
	results={}
	if tcSelection !='000':
		mysql = MySQlConnect()
		if tcSelection == '111':
			sql = "SELECT * FROM tvac.real_temperature WHERE (time > \"{}\") AND (time<\"{}\");".format(startingPoint,endingPoint)
		if tcSelection == '100':
			sql = "SELECT * FROM tvac.real_temperature WHERE (time > \"{}\") AND (time<\"{}\") AND thermocouple<76;".format(startingPoint,endingPoint)
		if tcSelection == '110':
			sql = "SELECT * FROM tvac.real_temperature WHERE (time > \"{}\") AND (time<\"{}\") AND (thermocouple<76 or thermocouple>95);".format(startingPoint,endingPoint)
		if tcSelection == '101':
			sql = "SELECT * FROM tvac.real_temperature WHERE (time > \"{}\") AND (time<\"{}\") AND (thermocouple<81);".format(startingPoint,endingPoint)
		if tcSelection == '010':
			sql = "SELECT * FROM tvac.real_temperature WHERE (time > \"{}\") AND (time<\"{}\") AND (thermocouple>95);".format(startingPoint,endingPoint)
		if tcSelection == '011':
			sql = "SELECT * FROM tvac.real_temperature WHERE (time > \"{}\") AND (time<\"{}\") AND ((thermocouple>75 and thermocouple<81) or thermocouple>95);".format(startingPoint,endingPoint)
		if tcSelection == '001':
			sql = "SELECT * FROM tvac.real_temperature WHERE (time > \"{}\") AND (time<\"{}\") AND (thermocouple>75 and thermocouple<81);".format(startingPoint,endingPoint)


		mysql.cur.execute(sql)
		mysql.conn.commit()
		time_two=time.time()
		#print("Time to Query (s): ",time_two-time_start)


		for row in mysql.cur:
			
			tmp=mdates.date2num(datetime.strptime(str(row["time"]),'%Y-%m-%d %H:%M:%S'))
			data_csv["time"].append(tmp)
			data_csv["thermocouple"].append(row["thermocouple"])
			data_csv["temperature"].append(float(row["temperature"]))

			tmp = results.get(row["time"], [])
			tmp.append([row["thermocouple"], float(row["temperature"])])
			results[row['time']] = tmp
	return "Temp since {}".format(startingPoint), results, data_csv

def getPressureDataFromDB(startingPoint,endingPoint,gaugeSelection):
	data_csv = dict(time=[],guage=[],pressure=[])
	results = {}
	#1=rough,2=cryo,3=chamber
	#results guage1=cryo, guage2=chamber, guage3=roughing
	if gaugeSelection !='000':
		mysql = MySQlConnect()
		# These two can be combined into one sql statement...if I have time look into that
		if gaugeSelection == '111':
			sql = "SELECT * FROM tvac.Pressure WHERE (time > \"{}\") AND (time<\"{}\");".format(startingPoint,endingPoint)	
		if gaugeSelection == '100':
			sql = "SELECT * FROM tvac.Pressure WHERE (time > \"{}\") AND (time<\"{}\") AND guage=3;".format(startingPoint,endingPoint)	
		if gaugeSelection == '110':
			sql = "SELECT * FROM tvac.Pressure WHERE (time > \"{}\") AND (time<\"{}\") AND (guage=3 OR guage=1);".format(startingPoint,endingPoint)	
		if gaugeSelection == '101':
			sql = "SELECT * FROM tvac.Pressure WHERE (time > \"{}\") AND (time<\"{}\") AND (guage=3 OR guage=2);".format(startingPoint,endingPoint)	
		if gaugeSelection == '010':
			sql = "SELECT * FROM tvac.Pressure WHERE (time > \"{}\") AND (time<\"{}\") AND guage=1;".format(startingPoint,endingPoint)	
		if gaugeSelection == '011':
			sql = "SELECT * FROM tvac.Pressure WHERE (time > \"{}\") AND (time<\"{}\") AND (guage=1 OR guage=2);".format(startingPoint,endingPoint)	
		if gaugeSelection == '001':
			sql = "SELECT * FROM tvac.Pressure WHERE (time > \"{}\") AND (time<\"{}\") AND guage=2;".format(startingPoint,endingPoint)	

		mysql.cur.execute(sql)
		mysql.conn.commit()

		for row in mysql.cur:

			tmp=mdates.date2num(datetime.strptime(str(row["time"]),'%Y-%m-%d %H:%M:%S'))
			data_csv["time"].append(tmp)
			#print(row["guage"])
			data_csv["guage"].append(row["guage"])
			data_csv["pressure"].append(float(row["pressure"]))

			tmp = results.get(row["time"], [])
			tmp.append([row["guage"], float(row["pressure"])])
			results[row['time']] = tmp
			#print("{},{},{},zone".format(row["time"],row["guage"],row["pressure"]))
	#print(results)
	return "Pressure since {}".format(startingPoint), results, data_csv	

def getExpectedTempFromDB(startingPoint,endingPoint):
	data_csv = dict(time=[],zone=[],temperature=[])
	results={}

	mysql = MySQlConnect()
	sql = "SELECT * FROM tvac.expected_temperature WHERE (time > \"{}\") AND (time<\"{}\");".format(startingPoint,endingPoint)


	mysql.cur.execute(sql)
	mysql.conn.commit()
	time_two=time.time()
	#print("Time to Query (s): ",time_two-time_start)


	for row in mysql.cur:
		tmp=mdates.date2num(datetime.strptime(str(row["time"]),'%Y-%m-%d %H:%M:%S'))
		data_csv["time"].append(tmp)
		data_csv["zone"].append(row["zone"])
		data_csv["temperature"].append(float(row["temperature"]))

		tmp = results.get(row["time"], [])
		tmp.append([row["zone"], float(row["temperature"])])
		results[row['time']] = tmp
	return "Expected Temp since {}".format(startingPoint), results, data_csv

def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


def main(args):

	filterwarnings("error")

	time_start=time.time()

	startTime = args[1]
	endTime =args[2]

	gaugeSelection=args[3]
	tcSelection=args[4]
	expectedSelection=args[5]


	if len(args)>7:
		temp_file=args[6]
		pressure_file=args[7]


	print("Querying Temperatures...")
	profile_I_ID, results, tdata_csv = getLiveTempFromDB(startTime,endTime,time_start,tcSelection)
	print("Rows returned: ", len(results))

	if expectedSelection=='1':
		print("Querying Expected Temperatures...")
		profile_expTemp, expectedT, expdata_csv=getExpectedTempFromDB(startTime,endTime)
		print("Rows returned: ", len(expectedT))


	print("Querying Pressures...")
	pressureID, pressure, pdata_csv=getPressureDataFromDB(startTime,endTime,gaugeSelection)
	print("Rows returned: ", len(pressure))

	time_values = []
	ptime_values = []
	etime_values = []

	exp_data={}
	tc_data = {}
	guage_data = {}	

	print("Time to Pressure End ",time.time()-time_start)

	if len(args)>7:
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

	if len(args)>7:
		df2 = pd.DataFrame({"time" : pTime, "guage" : pGuage, "pressure": pPressure})
		df2=df2[['time','guage','pressure']]
		df2.to_csv(pressure_file, index=False)

	for time_value in sorted(results):
		converted_time=mdates.date2num(datetime.strptime(str(time_value),'%Y-%m-%d %H:%M:%S'))
		time_values.append(converted_time)
		# print(converted_time)
		for thermocouple in results[time_value]:
			tmp = tc_data.get(thermocouple[0], [])
			tmp.append(thermocouple[1])
			tc_data[thermocouple[0]] = tmp
	if expectedSelection == '1':

		eTime=np.array(expdata_csv["time"])
		eZone=np.array(expdata_csv["zone"])
		eTemp=np.array(expdata_csv["temperature"])

		eYaxis=dict(zone1=[],zone2=[],zone3=[],zone4=[],zone5=[],zone6=[],zone7=[],zone8=[],zone9=[])
		eXaxis=dict(zone1=[],zone2=[],zone3=[],zone4=[],zone5=[],zone6=[],zone7=[],zone8=[],zone9=[])

		for time_value in range(0,len(eTime)):
			if eZone[time_value] == 1:
				eYaxis["zone1"].append(eTemp[time_value])
				eXaxis["zone1"].append(eTime[time_value])
			if eZone[time_value] == 2:
				eYaxis["zone2"].append(eTemp[time_value])
				eXaxis["zone2"].append(eTime[time_value])
			if eZone[time_value] == 3:
				eYaxis["zone3"].append(eTemp[time_value])
				eXaxis["zone3"].append(eTime[time_value])
			if eZone[time_value] == 4:
				eYaxis["zone4"].append(eTemp[time_value])
				eXaxis["zone4"].append(eTime[time_value])	
			if eZone[time_value] == 5:
				eYaxis["zone5"].append(eTemp[time_value])
				eXaxis["zone5"].append(eTime[time_value])
			if eZone[time_value] == 6:
				eYaxis["zone6"].append(eTemp[time_value])
				eXaxis["zone6"].append(eTime[time_value])
			if eZone[time_value] == 7:
				eYaxis["zone7"].append(eTemp[time_value])
				eXaxis["zone7"].append(eTime[time_value])	
			if eZone[time_value] == 8:
				eYaxis["zone8"].append(eTemp[time_value])
				eXaxis["zone8"].append(eTime[time_value])
			if eZone[time_value] == 9:
				eYaxis["zone9"].append(eTemp[time_value])
				eXaxis["zone9"].append(eTime[time_value])	

	guage1=[]
	xg1=[]
	guage2=[]
	xg2=[]	
	guage3=[]
	xg3=[]

	for time_value in range(0,len(pTime)):
		#print(pTime[time_value])
		if pGuage[time_value] == 1:
			xg1.append(pTime[time_value])
			guage1.append(pPressure[time_value])
		if pGuage[time_value] == 2:
			xg2.append(pTime[time_value])
			guage2.append(pPressure[time_value])
		if pGuage[time_value] == 3:
			xg3.append(pTime[time_value])
			guage3.append(pPressure[time_value])

	fig,(ax1,ax2)=plt.subplots(1,2,figsize=(14,8),sharex=False)


	for tc in tc_data:
		try:
			ax1.plot_date(time_values,tc_data[tc], '-',label=str(tc))
			ax1.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M:%S'))
			plt.gcf().autofmt_xdate()
			length=len(tc_data[tc])
			ax1.legend(bbox_to_anchor=(0., 1.075, 1., .102), loc=3,
           ncol=5, mode="expand", borderaxespad=0.2)
		except:
			print("No TC Data")
		#print(tc)
	if expectedSelection == '1':
		for zone in range(0,9):
			zoneStr="zone"+str(zone+1)
			if len(eXaxis[zoneStr]) != 0:
				ax1.plot_date(eXaxis[zoneStr],eYaxis[zoneStr], '-',label=("Zone "+str(zone+1)))

		ax1.legend(bbox_to_anchor=(0., 1.075, 1., .102), loc=3,			
       ncol=5, mode="expand", borderaxespad=0.2)
			#except:
				#print("No Expected Temp Data")

	#print(min(pTime),max(pTime))

	ax2.plot(xg1,guage1,'-', label=str('Cryopump'))
	ax2.plot(xg2,guage2,'-', label=str("Chamber"))
	ax2.plot(xg3,guage3,'-', label=str("Roughing"))

	# Use a DateFormatter to set the data to the correct format.
	ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M:%S'))

	# Sets the tick labels diagonal so they fit easier.
	plt.gcf().autofmt_xdate()

	try:
		ax2.set_yscale('log')
	except Warning:
		print("Log Plotting Error")
		ax2.set_yscale('linear')
	#ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d %H:%M:%S'))
	#plt.gcf().autofmt_xdate()


	ax2.legend()
	#ax1.legend(bbox_to_anchor=(-.01, 0, 1, 1), bbox_transform=plt.gcf().transFigure)

	ax1.set_ylabel('Temperature [K]')
	ax1.set_xlabel('Time')	
	ax1.set_title(profile_I_ID)

	ax2.set_ylabel('Pressure [Torr]')
	ax2.set_xlabel('Time')
	ax2.set_title(pressureID)

	#plt.savefig('graph1.png')
	plt.show()
		

if __name__ == '__main__':
	main(sys.argv)