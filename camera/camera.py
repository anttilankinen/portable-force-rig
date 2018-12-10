import picamera
import subprocess
import os.path
from picamera import PiCamera

# To install PiCamera
# '$ sudo apt-get install python-pip'
# '$ sudo pip install picamera'

# Name of the temporary video
temp_video = 'test.h264'

# Capture 30 seconds of 640p
camera = picamera.PiCamera()
camera.framerate = 60
camera.resolution = (640, 480)
camera.start_recording(temp_video)
print("Camera Recording")
camera.wait_recording(30)
camera.stop_recording()

#converting h.264 to mp4
print('Camera finished recording...')
from subprocess import CalledProcessError
command = "MP4Box -add {} {}.mp4".format(temp_video, 'test') # To install MP4Box use 'sudo apt-get install -y gpac'
try:
    output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
except subprocess.CalledProcessError as e:
    print('FAIL:\ncmd:{}\noutput:{}'.format(e.cmd, e.output))
