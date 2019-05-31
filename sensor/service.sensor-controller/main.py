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
lookup_table = None

def read_devices():
    global ELAPSED_TIME
    global ZEROED
    global BIAS

    while THREAD_IS_RUN:
        value, frameindex = 0, 0
        try:
            # read hardware
            data1 = DEV_CTX.read_i2c_block_data(DEV1_ADDRESS, 0x00, 6)
            frameindex1 = data1[0] << 8 | data1[1]
            timestamp1 = data1[2] << 8 | data1[3]
            value1 = (data1[4] << 8 | data1[5]) - 255

        except IOError as e: # frequent
            continue

        if ZEROED:
            value1 = value1 - BIAS

        else:
            BIAS = value1
            value1 = 0
            ZEROED = True

        value1 = max(0, value1)

        if lookup_table1 is not None:
            if value1 >= len(lookup_table1): # out of bounds
                value1 = lookup_table1[-1, 0]
                print('Sensor 1 out of bounds')
            else:
                value1 = lookup_table1[value1, 0]

        OUT_FILE.write('%.4f, %.4f, %.2f\n' % (value1, ELAPSED_TIME))
        redis_client.publish('sensor-data', "{:.3f}".format(value1))
        time.sleep(INTERVAL / float(1000))
        ELAPSED_TIME = ELAPSED_TIME + INTERVAL

# start process to read from GPIO
@app.route('/start', methods=['POST'])
def start():
    # read from GPIO
    global THREAD_IS_RUN
    global READ_THREAD
    global ELAPSED_TIME
    global OUT_FILE
    global lookup_table

    data = request.get_json()
    size = data['size']

    if data is not None and lookup_table is None:
        lookup_table = np.load('./lookup/' + size + '_' + str(DEV_ADDRESS) + '.npy')

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
    global lookup_table

    if READ_THREAD is not None:
        THREAD_IS_RUN = False
        READ_THREAD.join()
        READ_THREAD = None
        lookup_table = None
        return 'Stopped reading from sensor..'
    return 'Sensor not running..'

if __name__ == '__main__':
    app.config.from_object('config.default')
    DEV_ADDRESS = app.config['DEV_ADDRESS']

    # try to connect to sensor
    try:
        DEV_CTX = smbus2.SMBus(DEV_BUS)

    except IOError as e:
        print(e.message)
        sys.exit(1)

    app.run(host='0.0.0.0', port=80)
