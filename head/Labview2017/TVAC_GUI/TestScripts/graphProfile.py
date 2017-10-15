#!/usr/bin/env python
import sys
#import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import *
import json as JSON
import requests
import time

import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt

def createExpectedValues(setPoints,startTime=None):
	#print(setPoints)
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
		#print(setPoint)
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


def unwrapJSON(json,zone):
	#print(json)
	return json[zone]['thermalprofiles']



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
			maxTemp = f.readline().strip().split(",")
			minTemp = f.readline().strip().split(",")
			maxSlope = f.readline().strip().split(",")

			# Skip any blank lines
			tempString = ""
			while not tempString:
				tempString = f.readline().split(",")[0]
			# tempString holds header, we can ignore
			setpoints = []
			i = 0

			while True:
				line = f.readline().split(",")
				#print(line)
				# print(zone)
				if len(line) <= 11:
					break

				if i > 0:
					oldGoalTemp = goalTemp

				for j in range(0,9):
					zone = line[j+3]

					if zone!="":

						zone = j+1
						setPoint = line[0]
						rampTime = line[1]
						soakTime = line[2]
						goalTemp = line[3+j]
						goalTemp=goalTemp.rstrip()

						# print(setPoint)
						# print(rampTime)
						# print(soakTime)
						# print(goalTemp)


						tempSetpoint = {
						"zone":zone,
						"setPoint":setPoint,
						"rampTime":rampTime,
						"soakTime":soakTime,
						"goalTemp":goalTemp,
						}
						setpoints.append(tempSetpoint)

						#print(tempSetpoint)
				if i > 0:
					rampRatePerMin = (float(oldGoalTemp) - float(goalTemp))/float(rampTime) * 60
					if abs(rampRatePerMin) > 12:
						popupError("Zone {}, Setpoint {} has ramp rate over 1.2 C per minute. ({}c/min)".format(zone, setPoint, rampRatePerMin))
				i += 1
	except (OSError) as e:
		popupError("File named:\n\n{}\n\nCan not be opened, check to make sure file is there and is readable.".format(fileName))
		quit()

	header
	output = "{\n"
	#output += "  \"name\" : \"{}\",".format(fileName.split(".")[0])
	output += "  \"profiles\": [\n"
	for zone in range(9):
		if averages[zone] == "":
			continue

		output += "    {\n"
		output += "      \"zone\": {},\n".format(zone+1)
		output += "      \"average\": \"{}\",\n".format(averages[zone])
		if maxTemp[zone] == "":
			popupError("Missing maxTemp Error on zone {}".format(zone+1))
		output += "      \"maxTemp\": \"{}\",\n".format(maxTemp[zone])
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
	#print(output)
	return output

def main(args):
	if len(args) < 2:
		popupError("Error calling profile Importer")
	jsonLabview = args[1]
#	json = generateJSON(fileName)
	#print(json)
	#json = JSON.loads(jsonLabview)

	with open(jsonLabview) as json_file:
		json = JSON.load(json_file)

	demo = False

	expected_temps=dict(time=[],zone1=[],zone2=[],zone3=[],zone4=[],zone5=[],zone6=[],zone7=[],zone8=[],zone9=[])

	#expected_temp_values, expected_time_values = createExpectedValues(unwrapJSON(json,0))
#	expected_temp_values2, expected_time_values = createExpectedValues(unwrapJSON(json,1))

	for i in range(0,8):
		try:
			expected_temp_values, expected_time_values = createExpectedValues(unwrapJSON(json,i))
			
			for j in range(0,len(expected_temp_values)):
				zonestr="zone"+str(i+1)
				expected_temps[zonestr].append(expected_temp_values[j])
				if i==0:
					expected_temps["time"].append(expected_time_values[j])
		except:
			continue	

	print(JSON.dumps(expected_temps))
	# print(expected_time_values)
	#print("Program worked!")


main(sys.argv)
