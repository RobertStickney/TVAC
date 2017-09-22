import sys
import requests

def main(args):
	'''
	Starts the preloaded profile, assumes one is in server state already, if nothing is load, nothing will happen
	'''
	host = "localhost"
	port = "8000"
	path = "runProfile"

	url = "http://{}:{}/{}".format(host,port,path)

	try:
		r = requests.get(url)
	except Exception as e:
		raise e
		popupError("Can't send request to sever\nCheck to make sure it's turned on and connected")
	print(r.text)


if __name__ == '__main__':
	main(sys.argv)