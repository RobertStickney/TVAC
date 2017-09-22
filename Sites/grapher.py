import matplotlib.pyplot as plt
import time
import random

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

	setPoints = [
		{
		"goalTemp":310,
		"rampTime": 10,
		"soakTime": 6,
		},
		{
		"goalTemp":315,
		"rampTime": 20,
		"soakTime": 30,
		},
		# {
		# "goalTemp":250,
		# "rampTime": 7200,
		# "soakTime": 1800,
		# },
		# {
		# "goalTemp":300,
		# "rampTime": 3600,
		# "soakTime": 900,
		# }
		]

	setPointsNew = [
		{
		"goalTemp":310,
		"rampTime": 10,
		"soakTime": 5,
		},
		{
		"goalTemp":250,
		"rampTime": 20,
		"soakTime": 30,
		},
		# {
		# "goalTemp":250,
		# "rampTime": 7200,
		# "soakTime": 1800,
		# },
		# {
		# "goalTemp":300,
		# "rampTime": 3600,
		# "soakTime": 900,
		# }
		]


	# generate expected values
	expected_temp_values, expected_time_values = createExpectedValues(setPoints)

	

	# testing stuff
	time_values_test = expected_time_values
	expected_temp_values_test = expected_temp_values
	real_temp_values = []
	real_time_values = []
	time_creep = 0
	newProfile = False

	inHold = False
	inHoldFlag = False
	startTime = time.time()
	while True:
		# find value for the current time
		currentTime = time.time() + time_creep 
		# time_creep += .1
	 
		while inHold:
			if not inHoldFlag:
				# first time through hold loop
				print("in hold for first time")
				startHoldTime = int(time.time())
				inHoldFlag = True
			pass

			currentTime = time.time() + time_creep 
			# time_creep += .1

			# for testing
			if currentTime > startHoldTime  + time_creep+ 10:
				inHold = False

		# just got out of hold
		if inHoldFlag:
			print("leaving hold for the first time")
			endHoldTime = int(time.time())
			holdTime = endHoldTime - startHoldTime
			startTime = startTime + holdTime
			expected_temp_values, expected_time_values = createExpectedValues(setPoints, startTime=startTime)
			inHoldFlag = False

			# for testing
			time_values_test = expected_time_values
			expected_temp_values_test = expected_temp_values

		if len(expected_time_values) <= 0:
			break
		while currentTime > expected_time_values[0]:
			print("At time {} temp should be: {}".format(expected_time_values[0],expected_temp_values[0]))
			temp_temp = expected_temp_values[0]
			expected_temp_values = expected_temp_values[1:]
			expected_time_values = expected_time_values[1:]
			if len(expected_time_values) <= 0:
				break
		real_temp_values.append(temp_temp)
		real_time_values.append(currentTime)


		# Testing setting a new profile
		if not newProfile and currentTime > startTime + 10:
			inHold = True
			# setPoints = setPointsNew
			# expected_temp_values, expected_time_values = createExpectedValues(setPoints, startTime=startTime)
			# time_values_test = expected_time_values
			# expected_temp_values_test = expected_temp_values
			newProfile = True





		plt.plot(time_values_test,expected_temp_values_test)
		plt.plot(real_time_values,real_temp_values)
		plt.pause(1)
		plt.clf()
		plt.ylabel('Temperture')
		plt.xlabel('Time')
		plt.show(block=False)


if __name__ == '__main__':
	main()