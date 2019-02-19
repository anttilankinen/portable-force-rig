import picamera
import subprocess
from picamera import PiCamera
from subprocess import CalledProcessError

#Conversion code
def convert(video, id):
    #Setting the name of the video
    path = '~/Repositories/portable-force-rig/sensor/service.video-stream/recordings/' + id
    print('Converting..')
    command = 'MP4Box -add {} {}.mp4'.format(video, path)

    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        print('FAIL:\ncmd:{}\noutput:{}'.format(e.cmd, e.output))

    print('Finished')

#Delete code
def delete(video):
    #delete the temporary temp_video
    command = 'rm ~/Repositories/portable-force-rig/sensor/service.video-stream/' + video
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as e:
        print('FAIL:\ncmd:{}\noutput:{}'.format(e.cmd, e.output))
