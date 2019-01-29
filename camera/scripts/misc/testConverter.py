import picamera
import subprocess
import os.path
from picamera import PiCamera

# To install PiCamera
# '$ sudo apt-get install python-pip'
# '$ sudo pip install picamera'
temp_video = 'v.h264'
#converting h.264 to mp4
print('Converting')
from subprocess import CalledProcessError
command = "MP4Box -add {} {}.mp4".format(temp_video, 'con_video') # To install MP4Box use 'sudo apt-get install -y gpac'
try:
    output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
except subprocess.CalledProcessError as e:
    print('FAIL:\ncmd:{}\noutput:{}'.format(e.cmd, e.output))
print('Finished')
