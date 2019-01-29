import picamera
import subprocess
import os.path
import datetime as dt
from picamera import PiCamera

# To install PiCamera
# '$ sudo apt-get install python-pip'
# '$ sudo pip install picamera'

# Name of the temporary video
temp_video = 'temp.h264'

# Settings of the PiCamera
camera = picamera.PiCamera()
camera.framerate = 90
camera.resolution = (640, 480)
exposure_mode = 'sports'
#Checking the highest framerate
print(camera.framerate)

#Setting up timestamp
camera.annotate_background = picamera.Color('black')
#Setting the name of the video
name = "'/home/pi/Videos/" + dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "'"
camera.annotate_text = dt.datetime.now().strftime('%M:%S:%f')

# Recording script
camera.start_recording(temp_video)
print("Camera Recording")

start = dt.datetime.now()
while (dt.datetime.now() - start).seconds < 30:
    camera.annotate_text = dt.datetime.now().strftime('%M:%S:%f')

    camera.wait_recording(30)
camera.stop_recording()

#converting h264 to mp4
print('Camera finished recording...')
print('Converting to mp4')
from subprocess import CalledProcessError
command = "MP4Box -fps 90 -add {} {}.mp4".format(temp_video, name) # To install MP4Box use 'sudo apt-get install -y gpac'
try:
    output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
except subprocess.CalledProcessError as e:
    print('FAIL:\ncmd:{}\noutput:{}'.format(e.cmd, e.output))
print('Success')

#delete the temporary temp_video
command = "rm /home/pi/Documents/temp.h264"
try:
    output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
except subprocess.CalledProcessError as e:
    print('FAIL:\ncmd:{}\noutput:{}'.format(e.cmd, e.output))
