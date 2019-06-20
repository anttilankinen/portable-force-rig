import os
import time
import redis
import threading
from flask import Flask, request
import smbus2
import numpy as np
import sys

REDIS_PORT = int(os.getenv('REDIS_PORT'))

app = Flask(__name__)
redis_client = redis.StrictRedis(host='redis', port=REDIS_PORT, db=0)
redis_channel = redis_client.pubsub()

OUT_FILE = None
INTERVAL = 25 # in ms
ELAPSED_TIME = 0
READ_THREAD = None
THREAD_IS_RUN = False
DEV_BUS = 1
DEV_CTX = None
ZEROED = False
BIAS = 0

def read_devices():
    global ELAPSED_TIME
    global ZEROED
    global BIAS

    while THREAD_IS_RUN:
        value, frameindex = 0, 0
        try:
            # read hardware
            data1 = DEV_CTX.read_i2c_block_data(DEV_ADDRESS, 0x00, 6)
            frameindex = data1[0] << 8 | data1[1]
            timestamp = data1[2] << 8 | data1[3]
            value = (data1[4] << 8 | data1[5]) - 255

        except IOError as e: # frequent
            continue

        if ZEROED:
            value = value - BIAS

        else:
            BIAS = value
            value = 0
            ZEROED = True

        value = max(0, value)

        if LOOKUP_TABLE is not None:
            if value >= len(LOOKUP_TABLE): # out of bounds
                value = LOOKUP_TABLE[-1, 0]
                print('Sensor out of bounds')
            else:
                value = LOOKUP_TABLE[value, 0]

        OUT_FILE.write('%.4f, %.2f\n' % (value, ELAPSED_TIME))
        redis_client.publish('sensor-data', "{:.3f}".format(value))
        time.sleep(INTERVAL / float(1000))
        ELAPSED_TIME = ELAPSED_TIME + INTERVAL

# start process to read from GPIO
@app.route('/start')
def start():
    # read from GPIO
    global THREAD_IS_RUN
    global READ_THREAD
    global ELAPSED_TIME
    global OUT_FILE

    if READ_THREAD is None:
        ELAPSED_TIME = 0
        THREAD_IS_RUN = True
        OUT_FILE = open('./saved-readings/' + str(int(time.time())) + '.txt', 'w')
        READ_THREAD = threading.Thread(target=read_devices)
        READ_THREAD.start()
        return 'Started reading from sensor..'
    return 'Sensor already running..'

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

if __name__ == '__main__':
    app.config.from_object('config.default')
    DEV_ADDRESS = app.config['DEV_ADDRESS']
    LOOKUP_TABLE = np.load(app.config['LOOKUP_TABLE'])

    # try to connect to sensor
    try:
        DEV_CTX = smbus2.SMBus(DEV_BUS)

    except IOError as e:
        print(e.message)
        sys.exit(1)

    app.run(host='0.0.0.0', port=80)
