import picamera
import subprocess
import os.path
import datetime as dt
from picamera import PiCamera

#Conversion code
def convert(videoName):
    # To install PiCamera
    # '$ sudo apt-get install python-pip'
    # '$ sudo pip install picamera'
    #converting h.264 to mp4

    #Setting the name of the video
    name = "'/home/pi/Videos/" + dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "'"

    print('Converting')
    from subprocess import CalledProcessError
    command = "MP4Box -add {} {}.mp4".format(videoName, name) # To install MP4Box use 'sudo apt-get install -y gpac'
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        print('FAIL:\ncmd:{}\noutput:{}'.format(e.cmd, e.output))
    print('Finished')

#Delete code
def delete(videoName):
    #delete the temporary temp_video
    command = "rm /home/pi/Documents/" + videoName
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        print('FAIL:\ncmd:{}\noutput:{}'.format(e.cmd, e.output))
