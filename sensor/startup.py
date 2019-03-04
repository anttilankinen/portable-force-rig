from threading import Thread
import time
import os

def startprgm(i):
    if (i == 0):
        time.sleep(1)
        print('Running: service.video-stream')
        os.system('sudo python3 /home/pi/Repositories/portable-force-rig/sensor/service.video-stream/main.py')
    elif (i == 1):
        time.sleep(1)
        print('Running: service.calibration')
        os.system('sudo python3 /home/pi/Repositories/portable-force-rig/sensor/service.calibration/main.py')
    else:
        pass

for i in range(2):
    t = Thread(target=startprgm, args=(i,))
    t.start()
