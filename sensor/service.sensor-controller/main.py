#!/usr/bin/env python3

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
DEV2_BUS = 1
DEV2_ADDRESS = 0x04
DEV2_CTX = None
ZEROED = False
BIAS1 = 0
BIAS2 = 0

def read_devices():
    global ELAPSED_TIME
    global THREAD_IS_RUN
    global DEV1_ADDRESS
    global DEV2_ADDRESS
    global DEV1_CTX
    global DEV2_CTX
    global ZEROED
    global BIAS1
    global BIAS2
    global LOOKUP_TABLE
    global OUT_FILE
    timestamp = 1
    previous_value1 = 0
    previous_value2 = 0
    # force readings are written as follows:
    # if the sensor reading is 0<=x<=768, mapped directly with look-up table
    # if reading is <0, set to zero and map
    # if reading is >768, return -1 as the sensor is out of bounds
    while THREAD_IS_RUN:
        value, frameindex = 0, 0

            # SingleTac manual section 2.4.3 I2C Read Operation:
            # Where a Read operation is not preceded by a Read Request
            # operation the read location defaults to 128
            # (the sensor output location) and consecutive reads will
            # therefore simply read the default 32 bytes
            # of the sensor data region.
            # Here we read only 6 bytes from 128 to 133
        try:
            # read hardware
            data1 = DEV1_CTX.read_i2c_block_data(DEV1_ADDRESS, 0x00, 6)
            data2 = DEV2_CTX.read_i2c_block_data(DEV2_ADDRESS, 0x00, 6)


            frameindex1 = data1[0] << 8 | data1[1]
            timestamp1 = data1[2] << 8 | data1[3]
            value1 = (data1[4] << 8 | data1[5]) - 255
            frameindex2 = data2[0] << 8 | data2[1]
            timestamp2 = data2[2] << 8 | data2[3]
            value2 = (data2[4] << 8 | data2[5]) - 255
        except IOError as e: # frequent
            continue

#        if frameindex1 == 0xffff and timestamp1 == 0xffff: #i2c read error
#            continue

#        if value1 > 768: #out of bounds
#            continue

#        if frameindex2 == 0xffff and timestamp2 == 0xffff: #i2c read error
#            continue

#        if value2 > 768: #out of bounds
#            continue
        if value1 is -255:
            value1 = previous_value1

        if value2 is -255:
            value2 = previous_value2
        if ZEROED:
            value1 = value1 - BIAS1
            value2 = value2 - BIAS2
        else
            BIAS1 = value1
            BIAS2 = value2
            value1 = 0
            value2 = 0
            ZEROED = True

        if value1 < 0
            value1 = 0

        if value2 < 0
            value2 = 0

        previous_value1 = value1
        previous_value2 = value2

        if LOOKUP_TABLE is not None:
            if value1 > 768:
                print('Warning: sensor 1 out of bounds')
                value1 = -1
            else:
                value1 = LOOKUP_TABLE[0, value1]
            if value2 > 768:
                print('Warning: sensor 2 out of bounds')
                value2 = -1
            else:
                value2 = LOOKUP_TABLE[1, value2]
        out_file.write('%i, %i, %.2f\n' % (value1, value2, ELAPSED_TIME))
        redis_client.publish('sensor-data', f'{value1}')
        time.sleep(INTERVAL / float(1000))
        ELAPSED_TIME = ELAPSED_TIME + INTERVAL

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
    # open file to write data
    LOOKUP_TABLE = None
    if sys.argc > 2:
        LOOKUP_TABLE1 = np.load(sys.argv[1])
        LOOKUP_TABLE2 = np.load(sys.argv[2])
        LOOKUP_TABLE = np.concatenate([LOOKUP_TABLE1, LOOKUP_TABLE2], axis=1)
    OUT_FILE= open(int(time.time()) + '.txt', 'w')
    # try to connect to sensor
    try:
        DEV1_CTX = smbus.SMBus(DEV1_BUS)
        DEV2_CTX = smbus.SMBus(DEV2_BUS)
    except IOError as e:
        print e.message
        sys.exit(1)
    app.run(host='0.0.0.0', port=80)
