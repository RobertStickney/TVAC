import matplotlib.pyplot as plt
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

def unwrapJSON(json):
	# print(json)
	return json['profiles'][0]['thermalprofiles']



def closeErrorWindow(root): 
    root.destroy()

def popupError(message):
	root = tk.Tk()
	root.title("Error")
	l = Label(text=message).pack(padx=20, pady=30)
	button = Button(root, text="Close", command=root.destroy)
	button.pack(pady=10)


	center(root)

	root.mainloop()

	quit()

def center(toplevel):
	'''
	https://stackoverflow.com/questions/3352918/how-to-center-a-window-on-the-screen-in-tkinter
	'''
	toplevel.update_idletasks()
	w = toplevel.winfo_screenwidth()
	h = toplevel.winfo_screenheight()
	size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
	x = w/2 - size[0]/2
	y = h/2 - size[1]/2
	toplevel.geometry("%dx%d+%d+%d" % (size + (x, y)))

def generateJSON(fileName):
	try:
		with open(fileName) as f:
			header = f.readline().strip()
			averages = f.readline().strip().split(",")
			thermocouples = f.readline().strip().split(",")
			heatErrors = f.readline().strip().split(",")
			# Skip any blank lines
			tempString = ""
			while not tempString:
				tempString = f.readline().split(",")[0]
			# tempString holds header, we can ignore
			setpoints = []
			i = 0
			while True:
				line = f.readline().split(",")
				# print(line)
				# print(zone)
				if len(line) <= 5:
					break

				if i > 0:
					oldGoalTemp = goalTemp

				zone = line[0]
				setPoint = line[1]
				rampTime = line[2]
				soakTime = line[3]
				goalTemp = line[4]


				tempSetpoint = {
				"zone":zone,
				"setPoint":setPoint,
				"rampTime":rampTime,
				"soakTime":soakTime,
				"goalTemp":goalTemp,
				}
				setpoints.append(tempSetpoint)

				if i > 0:
					rampRatePerMin = (float(oldGoalTemp) - float(goalTemp))/float(rampTime) * 60
					if abs(rampRatePerMin) > 1.2:
						popupError("Zone {}, Setpoint {} has ramp rate over 1.2 C per minute. ({}c/min)".format(zone, setPoint, rampRatePerMin))
				i += 1
	except (OSError) as e:
		popupError("File named:\n\n{}\n\nCan not be opened, check to make sure file is there and is readable.".format(fileName))
		quit()

	# header
	output = "{\n"
	output += "  \"name\" : \"{}\",".format(fileName.split(".")[0])
	output += "  \"profiles\": [\n"
	for zone in range(8):
		if averages[zone] == "":
			continue

		output += "    {\n"
		output += "      \"zone\": {},\n".format(zone+1)
		output += "      \"average\": \"{}\",\n".format(averages[zone])
		if heatErrors[zone] == "":
			popupError("Missing Heat Error on zone {}".format(zone+1))
		output += "      \"heatError\": \"{}\",\n".format(heatErrors[zone])
		if thermocouples[zone] == "":
			popupError("Missing Thermo Couples on zone {}".format(zone+1))
		output += "      \"thermocouples\": [{}],\n".format(thermocouples[zone].replace(" ",","))
		output += "      \"thermalprofiles\":\n"
		output += "      [\n"
		for setPoint in setpoints:
			# Why is this here?
			if int(setPoint["zone"]) != int(zone)+1:
				continue
			output += "        {\n"
			output += "          \"thermalsetpoint\": {},\n".format(int(setPoint["setPoint"])-1)
			output += "          \"tempgoal\": {},\n".format(setPoint["goalTemp"])
			output += "          \"ramp\": {},\n".format(setPoint["rampTime"])
			output += "          \"soakduration\": {}\n".format(setPoint["soakTime"])
			output += "        },\n"
		# This takes the comma on the last line
		output = output[:-2] + "\n"
		output += "      ]\n"
		output += "    },\n"
	output = output[:-2] + "\n"
	output += "  ]\n"
	output += "}"
	return output


def createExpectedValues(setPoints,startTime=None):
	intervalTime = 5
	if startTime:
		currentTime = int(startTime)
	else:
		currentTime = int(time.time())
	currentTemp = 300
	expected_temp_values = []
	expected_time_values = []
	setpoint_ramp_start_time = []
	setpoint_soak_start_time = []
	for setPoint in setPoints:
		# print(setPoint)
		goalTemp = setPoint["tempgoal"]
		rampTime = setPoint["ramp"]
		soakTime = setPoint["soakduration"]


		# skip ramp section if rampTime == 0
		if rampTime:
			TempDelta = goalTemp-currentTemp
			numberOfJumps = rampTime/intervalTime
			intervalTemp = TempDelta/numberOfJumps
			rampEndTime = currentTime+rampTime

			# setting all values all for ramp
			for i, tempSetPoint in enumerate(range(currentTime,rampEndTime, intervalTime)):
				x = tempSetPoint
				y = currentTemp + (i*intervalTemp)
				expected_time_values.append(tempSetPoint)
				expected_temp_values.append(y)
		else:
			rampEndTime = currentTime
		setpoint_ramp_start_time.append(currentTime)


		#Setting all soak values
		setpoint_soak_start_time.append(rampEndTime)
		for tempSetPoint in range(rampEndTime, rampEndTime+soakTime, intervalTime):
			x = tempSetPoint
			y = goalTemp
			expected_time_values.append(tempSetPoint)
			expected_temp_values.append(y)
			# print("{},{}".format(x,y))


		currentTime = rampEndTime+soakTime
		currentTemp = goalTemp
	# end of for loop, end generating outputs


	return expected_temp_values, expected_time_values

def getLiveTempFromDB():
	mysql = MySQlConnect()
	# These two can be combined into one sql statement...if I have time look into that
	sql = "SELECT profile_name, startTime, endTime FROM tvac.Profile_Instance WHERE profile_name like \"acceptanceProfile\";"
	mysql = MySQlConnect()
	try:
		mysql.cur.execute(sql)
		mysql.conn.commit()
	except Exception as e:
		raise e
		return False

	result = mysql.cur.fetchone()
	if not result:
		return False

	sql = "SELECT * FROM tvac.Real_Temperture WHERE time>\"{}\";".format(result['startTime'],result['endTime'])

	mysql.cur.execute(sql)
	mysql.conn.commit()
	results = {}
	for row in mysql.cur:
		tmp = results.get(row["time"], [])
		tmp.append([row["thermocouple"], float(row["temperture"])])
		results[row['time']] = tmp
		# print("{},{},{},zone".format(row["time"],row["thermocouple"],row["temperture"]))
	return result['profile_name'], results

def getExpectedFromDB():
	mysql = MySQlConnect()
	# These two can be combined into one sql statement...if I have time look into that
	sql = "SELECT profile_name, startTime, endTime FROM tvac.Profile_Instance WHERE profile_name like \"acceptanceProfile\";"
	mysql = MySQlConnect()
	try:
		mysql.cur.execute(sql)
		mysql.conn.commit()
	except Exception as e:
		return False

	result = mysql.cur.fetchone()
	if not result:
		return False

	sql = "SELECT * FROM tvac.Expected_Temperture WHERE time>\"{}\";".format(result['startTime'])

	mysql.cur.execute(sql)
	mysql.conn.commit()
	results = {}
	for row in mysql.cur:
		# print(row)
		tmp = results.get(row["time"], [])
		tmp.append([row["zone"], float(row["temperture"])])
		results[row['time']] = tmp
	return result['profile_name'], results

def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)


def main(args):
	# Get live data
	importantTCs = [1,2,3,4,5]
	importantTCs = [6]
	importantTCs.extend(list(range(76,80)))
	overlay = False
	secondsShown = 50000
	secondsShown *= -1
	if len(args) == 3:
		overlay = True
	if overlay:
		fileName = args[2]
		json = generateJSON(fileName)
		json = JSON.loads(json)

		expected_temp_values, expected_time_values = createExpectedValues(unwrapJSON(json))
		firstTime = expected_time_values[0]
		for i in range(len(expected_time_values)):
			expected_time_values[i] -= firstTime
			expected_time_values[i] /= 60
			expected_temp_values[i] += 272.15

	while True:
		if overlay:
			plt.plot(expected_time_values,expected_temp_values, label="Expected Results")
			plt.legend(loc='upper left')
		profile_I_ID, results = getLiveTempFromDB()
		# print(results)
		time_values = []
		tc_data = {}
		firstTime = sorted(results)[0]
		for time_value in sorted(results):
			# diff = time_value - firstTime
			# time_values.append(diff.total_seconds()/60)
			# print(diff)

			time_values.append(utc_to_local(time_value))
			# time_values.append(time_value)
			# print("{} -> {}".format(time_value, results[time_value]))
			for thermocouple in results[time_value]:
				tmp = tc_data.get(thermocouple[0], [])
				tmp.append(thermocouple[1])
				tc_data[thermocouple[0]] = tmp
		print("time,tc,temp")
		for i, time in enumerate(time_values):
			for tc in tc_data:
				print("{},{},{}".format(time_values[i],tc,tc_data[tc][i]))
		for tc in tc_data:
			# if tc in importantTCs:
			plt.plot(time_values[secondsShown:],tc_data[tc][secondsShown:], label=str(tc))
		# print("times: {}".format(len(time_values)))
		# print("tcs: {}".format(len(tc_data)))
		# print("total: {}".format(len(time_values)*len(tc_data)))

		# get expected data
		# profile_I_ID, results = getExpectedFromDB()
		# time_values = []
		# expected_data = {}
		# for time_value in sorted(results):
		# 	diff = time_value - firstTime

		# 	time_values.append(diff.total_seconds()/60)
		# 	# time_values.append(time_value)
		# 	# print("{} -> {}".format(time_value, results[time_value]))
		# 	for zone in results[time_value]:
		# 		tmp = expected_data.get(zone[0], [])
		# 		tmp.append(zone[1])
		# 		expected_data[zone[0]] = tmp
		# for zone in expected_data:
		# 	plt.plot(time_values[secondsShown:],expected_data[zone][secondsShown:], label="zone"+str(zone))


		# print("Done gathering data")
			# plt.plot(real_time_values,real_temp_values)
		plt.legend(loc='upper left')

		plt.ylabel('Temperture')
		plt.xlabel('Time')
		plt.title(profile_I_ID)
		# plt.pause(5)
		# plt.clf()

		# plt.xticks(np.arange(min(0), max(diff.total_seconds())+1, 1.0))
		plt.show(block=False)
		input()


if __name__ == '__main__':
	main(sys.argv)