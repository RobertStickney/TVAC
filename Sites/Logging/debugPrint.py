'''
This is a common reference file for any globals that might be used
across this program.
'''
def init():
	global verbos
	verbos = 0

def debugPrint(verbosLevel, string):
	if verbos >= verbosLevel: 
		if type(string) == type({}):
			for entry in string:
				print("  "*(verbosLevel-1) + '\033[94m' +"debug-" + str(verbosLevel) +": "+ '\033[0m'+ str(entry) + " --> " + str(string[entry]))
		else:
			for line in string.split("\n"):
				print("  "*(verbosLevel-1) + '\033[94m' +"debug-" + str(verbosLevel) +": "+ '\033[0m'+ line)
