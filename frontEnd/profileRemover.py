import sys

def main(args):
	if len(args) < 2:
		popupError("Error calling profile Importer")
	fileName = args[1]



if __name__ == '__main__':
	main(sys.argv)


	sql = "DELETE FROM tvac.Thermal_Profile WHERE profile_name=\"{}\""
	sql = "DELETE FROM tvac.Thermal_Zone_Profile WHERE profile_name=\"{}\""
	sql = "DELETE FROM tvac.TC_Profile WHERE profile_name=\"{}\""

