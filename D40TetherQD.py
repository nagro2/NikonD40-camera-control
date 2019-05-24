
# Nick Agro 9/17/2015
# This is a very quick and dirty controller for the Nikon D40 Camera. I wanted a simple
# tethering controller for my camera and decided to throw together a Python script.
# It controls the camera through gphoto2 bash shell commands.
# Currently it controls shutter speed and aperture. It obtains the initial values from
# the camera. Currently, all values that can be set for shutter speed, iso, and aperture
# are stored in this script. In future versions I may pull these values directly from the
# camera.

# 5/22/19 add Camera_Settings class, begin refactoring

import gtk
import os
import subprocess
import time
import gobject

from Tkinter import *
master = Tk()
master.title("D40 Tether Quick and Dirty v1")
master.minsize(width=600, height=240)
master.maxsize(width=600, height=240)



class Camera_Settings:
	shutter_speed = -1
	aperture = -1
	iso = -1
	fstop_vals = (
'f/1.8',
'f/2',
'f/2.2',
'f/2.5',
'f/2.8',
'f/3.2',
'f/3.5',
'f/4',
'f/4.5',
'f/5',
'f/5.6',
'f/6.3',
'f/7.1',
'f/8',
'f/9',
'f/10',
'f/11',
'f/13',
'f/14',
'f/16',
'f/18',
'f/20',
'f/22'
	)
	shutterspeed_vals = (
'30.0000s',
'25.0000s',
'20.0000s',
'15.0000s',
'13.0000s',
'10.0000s',
'8.0000s',
'6.0000s',
'5.0000s',
'4.0000s',
'3.0000s',
'2.5000s',
'2.0000s',
'1.6000s',
'1.3000s',
'1.0000s',
'0.7692s',
'0.6250s',
'0.5000s',
'0.4000s',
'0.3333s',
'0.2500s',
'0.2000s',
'0.1666s',
'0.1250s',
'0.1000s',
'0.0769s',
'0.0666s',
'0.0500s',
'0.0400s',
'0.0333s',
'0.0250s',
'0.0200s',
'0.0166s',
'0.0125s',
'0.0100s',
'0.0080s',
'0.0062s',
'0.0050s',
'0.0040s',
'0.0031s',
'0.0025s',
'0.0020s',
'0.0015s',
'0.0012s',
'0.0010s',
'0.0008s',
'0.0006s',
'0.0005s',
'0.0004s',
'0.0003s',
'429496.7295s'
)

	iso_vals=(
'3200',
'1600',
'800',
'400',
'200'
)

	def connect_to_camera(self):
		print "Scan for camera..."
		cmd1='gvfs-mount -s gphoto2'
		#print cmd1
		subprocess.Popen(cmd1, shell=True)

		cmd2='gphoto2 --auto-detect > gphoto2-auto-detect-results'
		#print cmd2
		subprocess.Popen(cmd2, shell=True)

		time.sleep(1)

		fo = open("gphoto2-auto-detect-results", "rw+")
		line = fo.readline()
		line = fo.readline()
		line = fo.readline()
		if line.find("PTP") > 0:
			print "connected to: " + line

			# get apeture
			cmd1='gphoto2 --get-config /main/capturesettings/f-number > gphoto2-auto-detect-fnumber-results'
			subprocess.Popen(cmd1, shell=True)
			time.sleep(0.5)
			fo = open("gphoto2-auto-detect-fnumber-results", "rw+")
			line = fo.readline()
			line = fo.readline()
			line = fo.readline()
			print line[9:]
			label_apeture_val.configure(text=line[9:])
			fo.close()

			# get shutter speed
			time.sleep(0.5)
			cmd1='gphoto2 --get-config /main/capturesettings/shutterspeed > gphoto2-auto-detect-shutterspeed-results'
			subprocess.Popen(cmd1, shell=True)
			time.sleep(1)
			fo = open("gphoto2-auto-detect-shutterspeed-results", "rw+")
			line = fo.readline()
			line = fo.readline()
			line = fo.readline()
			print line[9:]
			label_shutterspeed_val.configure(text=line[9:])
			cam.shutter_speed = float(line[9:len(line)-2])

			# get iso
			time.sleep(0.5)
			cmd1='gphoto2 --get-config /main/imgsettings/iso > gphoto2-auto-detect-iso-results'
			subprocess.Popen(cmd1, shell=True)
			time.sleep(1)
			fo = open("gphoto2-auto-detect-iso-results", "rw+")
			line = fo.readline()
			line = fo.readline()
			line = fo.readline()
			print line[9:]
			label_iso_val.configure(text=line[9:])

		else: 
			print "no camera found"
			label_apeture_val.configure(text="xx")
			label_shutterspeed_val.configure(text="xx")
		
		fo.close()

	def capture_photos(self):
		print "Start capturing..."

		current_time = (time.strftime("%Y-%m-%d--%H-%M-%S"))
		print current_time

		if multicapture.get() == 1: # capture multi is selected
			xcmd = "gphoto2 --capture-image-and-download --filename 'image-%y%m%d-%H%M%S.jpg'"
			xcmd = xcmd + " -F" + frames.get()
			xcmd = xcmd + " -I" + interval.get() 
			print xcmd
			subprocess.Popen(xcmd, shell=True)

		if multicapture.get() == 0: # Capture multi not selected
			xcmd = "gphoto2 --capture-image-and-download --filename 'image-" + current_time + ".jpg'"
			print xcmd
			subprocess.Popen(xcmd, shell=True)
			if showphoto.get() == 1: # show photo is selected
				xcmd="eog image-" + current_time + ".jpg"
				# note 5 seconds + shutter speed works ok for iso 800 and low shutter speeds
				# but for high iso and some long shutter speeds combined with lower iso, the camera
				# takes much longer than 5 seconds to process frames. Unfortunately the camera's processing
				# time varies with iso and shutter speed. So it is best not to use auto display at higher isos and shutter speeds.
				print "waiting " + str(5 + cam.shutter_speed) + " seconds before displaying photo"
				time.sleep(5 + cam.shutter_speed)
				print xcmd
				subprocess.Popen(xcmd, shell=True)

	


	def set_aperture(self,aperture_in):
		print "Set apeture..."
		label_apeture_val.configure(text=aperture_in)
		xcmd="gphoto2 --set-config /main/capturesettings/f-number=" + aperture_in
		print xcmd
		subprocess.Popen(xcmd, shell=True)

	def set_shutter_speed(self, shutter_in):
		print "Set shutter speed..."
		xcmd="gphoto2 --set-config /main/capturesettings/shutterspeed=" + shutterspeed.get()
		label_shutterspeed_val.configure(text=shutter_in)
		cam.shutter_speed = float(suhtter_in[:len(shutter_in)-2])
		print "new cam.shutter_speed= "
		print cam.shutter_speed
		print xcmd
		subprocess.Popen(xcmd, shell=True)

	def set_iso(self, iso_in):
		print "Set iso..."
		xcmd="gphoto2 --set-config /main/imgsettings/iso=" + iso_in
		label_iso_val.configure(text=iso_in)
		print xcmd
		subprocess.Popen(xcmd, shell=True)
cam = Camera_Settings()


#set up main window gui

def menu_about():
	print "running menu About"
	c1 = Toplevel(master)
	c1.title("About: D40 Tether")
	c1.transient(master)
	Label(c1, text="\n     D40 Tether Quick and Dirty ver 1.0.0 9/16/2015      \n\n Copyright 2015 Nicholas Agro.\n").grid()

menubar = Menu(master)

# create a pulldown menu, and add it to the menu bar
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Exit", command=master.destroy)
menubar.add_cascade(label="File", menu=filemenu)

helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="About", command=menu_about)
menubar.add_cascade(label="Help", menu=helpmenu)

# display the menu
master.config(menu=menubar)

labelt = Label( master, text="D40 Tether QD", font=("courier", 12, "bold"), fg="salmon4")
labelt.grid(row=0, column=1)

label_apeture = Label( master, text="Apeture:" )
label_apeture.grid(row=11, column=0)

label_apeture_val = Label( master, text="xx",  bg="SkyBlue1" )
label_apeture_val.grid(row=11, column=1)

label_shutterspeed = Label( master, text="Shutter speed:" )
label_shutterspeed.grid(row=12, column=0)

label_shutterspeed_val = Label( master, text="xx",  bg="SkyBlue1" )
label_shutterspeed_val.grid(row=12, column=1)

label_iso = Label( master, text="iso:" )
label_iso.grid(row=13, column=0)

label_iso_val = Label( master, text="xx",  bg="SkyBlue1" )
label_iso_val.grid(row=13, column=1)

multicapture = IntVar()
showphoto = IntVar()
C1 = Checkbutton(master, text = "Multi capture:", variable = multicapture, \
                 onvalue = 1, offvalue = 0, height=1, \
                 width = 10)
C1.grid(row=2, column=0) # was 0

C2 = Checkbutton(master, text = "Show photo on capture:", variable = showphoto, \
                 onvalue = 1, offvalue = 0, height=1, \
                 width = 25)
C2.grid(row=15, column=1)


label2 = Label(master, text="Num of photos", relief=FLAT )
label2.grid(row=3, column=0)

var = StringVar(master)
var.set("3")
frames = Spinbox(master, from_=2, to=99, width=3, textvariable=var)
frames.grid(row=3, column=1)
print "\ninitial value of frames.get() =",frames.get()

label5 = Label(master, text="Interval", relief=FLAT )
label5.grid(row=3, column=2)

interval = Spinbox(master, from_=1, to=99, width=3)
interval.grid(row=3, column=3)

print "\ninitial value of interval.get() =", interval.get()

fstops = Spinbox(master, values= cam.fstop_vals)
fstops.grid(row=11, column=2)
print "\ninitial value of fstops.get() =",fstops.get()

shutterspeed = Spinbox(master, values=cam.shutterspeed_vals)
shutterspeed.grid(row=12, column=2)
print "\ninitial value of shutterspeed.get() =",shutterspeed.get()

iso = Spinbox(master, values=cam.iso_vals)
iso.grid(row=13, column=2)
print "\ninitial value of iso.get() =",iso.get()

def callback_set_aperture():
	apertureval = fstops.get()
	cam.set_aperture(apertureval)

def callback_set_shutter_speed():
	shutterval = shutterspeed.get()
	cam.set_shutter_speed(shutterval)

def callback_set_iso():
	isoval = iso.get()
	cam.set_iso(isoval)

def callback_connect_to_camera():
	cam.connect_to_camera()

def callback_capture_photos():
    cam.capture_photos()

f = Button(master, text="set", command=callback_set_aperture, bg="SkyBlue2")
g = Button(master, text="set", command=callback_set_shutter_speed, bg="SkyBlue2")
h = Button(master, text="set", command=callback_set_iso, bg="SkyBlue2")
c = Button(master, text="Connect to camera", command=callback_connect_to_camera, bg="SkyBlue2")
e = Button(master, text="Capture photo(s)", command=callback_capture_photos, bg="SkyBlue2")

c.grid(row=1, column =0)
e.grid(row=1, column =2)
f.grid(row=11, column =3)
g.grid(row=12, column =3)
h.grid(row=13, column =3)

mainloop()




