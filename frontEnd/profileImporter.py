import sys, os
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import *
import json as JSON
import requests
import time


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
		print(setPoint)
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

def main(args):
	if len(args) < 2:
		popupError("Error calling profile Importer")
	fileName = args[1]
	json = generateJSON(fileName)
	json = JSON.loads(json)

	userName = os.environ['LOGNAME']
	if "root" in userName or (len(sys.argv) > 1 and sys.argv[2] =="--live"):
		host = "192.168.99.1"
	else:
		host = "localhost"
	port = "8000"
	path = "saveProfile"

	url = "http://{}:{}/{}".format(host,port,path)
	data = json
	headers = {'Content-type': 'application/json'}

	try:
		r = requests.post(url, data=JSON.dumps(data), headers=headers)
	except Exception as e:
		popupError("Can't send request to sever\nCheck to make sure it's turned on and connected")
	print(r.text)
	if "success" not in r.text:
		errorCode = r.text.split(",")[0]
		if "1062" in errorCode:
			popupError("There is already a profile of this name in the database.\nPlease rename the profile or run profile in Database")	
		else:
			popupError(r.text)

	expected_temp_values, expected_time_values = createExpectedValues(unwrapJSON(json))
	plt.plot(expected_time_values,expected_temp_values, label="Expected Results")
	plt.legend(loc='upper left')

	# plt.pause(1)
	# plt.clf()
	plt.ylabel('Temperture')
	plt.xlabel('Time')
	plt.show(block=True)
	print("Program worked!")






if __name__ == '__main__':
	main(sys.argv)