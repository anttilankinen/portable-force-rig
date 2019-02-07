import os
import time
import redis
import threading
from flask import Flask
import smbus2
import numpy as np
import sys

REDIS_PORT = int(os.getenv('REDIS_PORT'))

app = Flask(__name__)
redis_client = redis.StrictRedis(host='redis', port=REDIS_PORT, db=0)
reddis_channel = redis_client.pubsub()

INTERVAL = 25 # in ms
ELAPSED_TIME = 0
READ_THREAD = None
THREAD_IS_RUN = False
DEV1_BUS = 1
DEV1_ADDRESS = 0x04
DEV1_CTX = None
ZEROED = False
BIAS1 = 0

#Function to be done (Change this to clipping code (whilst start) + compiling the final video (Once stopped))
def read_devices():
    global ELAPSED_TIME
    global THREAD_IS_RUN
    global DEV1_ADDRESS
    global DEV1_CTX
    global ZEROED
    global BIAS1
    global LOOKUP_TABLE
    global OUT_FILE
    timestamp = 1
    previous_value1 = 0
    previous_value2 = 0

    while THREAD_IS_RUN:
        value, frameindex = 0, 0
        try:
            # read hardware
            data1 = DEV1_CTX.read_i2c_block_data(DEV1_ADDRESS, 0x00, 6)

            frameindex1 = data1[0] << 8 | data1[1]
            timestamp1 = data1[2] << 8 | data1[3]
            value1 = (data1[4] << 8 | data1[5]) - 255

        except IOError as e: # frequent
            continue

        if value1 is -255:
            value1 = previous_value1

        if ZEROED:
            value1 = value1 - BIAS1

        else
            BIAS1 = value1
            value1 = 0
            ZEROED = True

        if value1 < 0
            value1 = 0

        previous_value1 = value1

        if LOOKUP_TABLE is not None:
            if value1 > 768:
                print('Warning: sensor 1 out of bounds')
                value1 = -1

            else:
                value1 = LOOKUP_TABLE[0, value1]

        out_file.write('%i, %.2f\n' % (value1, ELAPSED_TIME))
        redis_client.publish('sensor-data', f'{value1}')
        time.sleep(INTERVAL / float(1000))
        ELAPSED_TIME = ELAPSED_TIME + INTERV

# Start of process (Change to initiating the camera clipping)
# start process to read from GPIO
@app.route('/start')
def start():
    # read from GPIO
    global THREAD_IS_RUN
    global READ_THREAD
    global ELAPSED_TIME

    if READ_THREAD is None:
        ELAPSED_TIME = 0
        THREAD_IS_RUN = True
        READ_THREAD = threading.Thread(target=read_devices)
        READ_THREAD.start()
        return 'Started reading from sensor..'
    return 'Sensor already running..'

#Ending of process (Change so that the variable ends the clipping)
# stop process to read from GPIO
@app.route('/stop')
def stop():
    # stop reading
    global THREAD_IS_RUN
    global READ_THREAD
    if READ_THREAD is not None:
        THREAD_IS_RUN = False
        READ_THREAD.join()
        READ_THREAD = None
        return 'Stopped reading from sensor..'
return 'Sensor not running..'

#Possible to remove
if __name__ == '__main__':
    # open file to write data
    LOOKUP_TABLE = np.load('lookup.npy')
    OUT_FILE= open(int(time.time()) + '.txt', 'w')
    # try to connect to sensor
    try:
        DEV1_CTX = smbus.SMBus(DEV1_BUS)

    except IOError as e:
        print e.message
sys.exit(1)

#Running from the host ...
app.run(host='0.0.0.0', port=80)
