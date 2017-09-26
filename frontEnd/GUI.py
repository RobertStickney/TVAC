import tkinter as tk
from tkinter import *
from tkinter import messagebox
import datetime
import requests
import json



class GUI():
	"""
	docstring for GUI
	"""
	def __init__(self):
		self.root = Tk()
		self.widthpixels = int(1024*1.5)
		self.heightpixels = int(1024*1.5/1.618)
		self.statusFrameWidth = 400
		self.root.geometry('{}x{}'.format(self.widthpixels, self.heightpixels))
		
		self.addStaticElememts()
		self.update()

		self.root.mainloop()

	def sendGetToServer(self, path):
		host = "localhost"
		port = "8000"
		url = "http://{}:{}/{}".format(host,port,path)
		try:
			r = requests.get(url)
		except Exception as e:
			returnStr = "Can't send request to sever\nCheck to make sure it's turned on and connected"
			print("Error, can't connect")
			popupError(returnStr)
			return returnStr
		if "success" not in r.text:
			errorCode = r.text.split(",")[0]
			if "1062" in errorCode:
				returnStr = "There is already a profile of this name in the database.\nPlease rename the profile or run profile in Database"
			else:
				returnStr = r.text
		else:
			returnStr = r.text
		return returnStr

	def update(self):
		time = datetime.datetime.now().strftime("Time: %H:%M:%S")
		status = self.sendGetToServer("getEventList")
		statuses = json.loads(status)
		out = ""
		# print("JSON: "+strstatuses)
		for status in reversed(statuses):
			print("String: '{}'".format(status))
			status = json.loads(status.replace("'","\""))
			print("JSON: '{}'".format(status))
			out += "{}: {} - {}\n".format(status[0].upper(),status[1],status[2])
			
		# status = 
		# if status

		# self.statusMessage.config(text=status)
		self.statusMessage.config(state=NORMAL)
		self.statusMessage.insert('1.0', out)
		self.statusMessage.config(state=DISABLED)

		#lab['text'] = time
		self.root.after(1000, self.update) # run itself again after 1000 ms

	def SaveProfile(self):
		print("Load Profile!")

	def RunProfile(self):
		print("Runing profile!")

	def addStaticElememts(self):
		header = Label(self.root, text="TVAC Control Unit",relief="ridge")
		header.grid(row=0,pady=10,sticky="n", column=1,columnspan=5)
		self.root.grid_rowconfigure(0, minsize=30)
		# self.root.grid_columnconfigure(2, minsize=self.widthpixels-self.statusFrameWidth)

		menu = Frame(master=self.root, colormap="new", relief="ridge")
		menu.grid(row=1,column=0,sticky="nw")
		b = Button(menu, text="Save Profile", command=self.SaveProfile)
		b.grid(row=0,column=0)
		b = Button(menu, text="Run Profile", command=self.RunProfile)
		b.grid(row=0,column=1)
		
		self.root.grid_columnconfigure(14, minsize=self.statusFrameWidth)
		self.statusFrame = Frame(master=self.root,bg="#f7f7f7", colormap="new")
		self.statusFrame.grid(row=1,column=14, sticky="ne")
		# self.root.grid_columnconfigure(2, minsize=20)
		self.statusMessage = Message(self.statusFrame, text="", width=self.statusFrameWidth)
		m = Message(self.statusFrame)
		self.statusMessage = Text(self.statusFrame, background=m.cget("background"), )
		self.statusMessage.pack()



# Helper function
def closeErrorWindow(root): 
    root.destroy()

def popupError(message):
	errorBox = tk.Tk()
	errorBox.title("Error")
	l = Label(text=message).grid(padx=20, pady=30)
	button = Button(errorBox, text="Close", command=errorBox.destroy)
	button.grid(pady=10)


	center(errorBox)
	messagebox.showerror("Error", message)


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


if __name__ == '__main__':
	GUI()