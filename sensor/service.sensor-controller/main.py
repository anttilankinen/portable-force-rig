import os
import time
import redis
import threading
from flask import Flask, request
import smbus2
import numpy as np
import sys

REDIS_PORT = int(os.getenv('REDIS_PORT'))
DEV1_ADDRESS = os.getenv('DEV1_ADDRESS')
DEV2_ADDRESS = os.getenv('DEV2_ADDRESS')

app = Flask(__name__)
redis_client = redis.StrictRedis(host='redis', port=REDIS_PORT, db=0)
reddis_channel = redis_client.pubsub()

INTERVAL = 25 # in ms
ELAPSED_TIME = 0
READ_THREAD = None
THREAD_IS_RUN = False
DEV_BUS = 1
DEV_CTX = None
ZEROED = False
BIAS1 = 0
BIAS2 = 0
lookup_table1 = None
lookup_table2 = None

def read_devices():
    global ELAPSED_TIME
    global ZEROED
    global BIAS1
    global BIAS2

    while THREAD_IS_RUN:
        value, frameindex = 0, 0
        try:
            # read hardware
            data1 = DEV_CTX.read_i2c_block_data(DEV1_ADDRESS, 0x00, 6)
            data2 = DEV_CTX.read_i2c_block_data(DEV2_ADDRESS, 0x00, 6)

            frameindex1 = data1[0] << 8 | data1[1]
            timestamp1 = data1[2] << 8 | data1[3]
            value1 = (data1[4] << 8 | data1[5]) - 255
            frameindex2 = data2[0] << 8 | data2[1]
            timestamp2 = data2[2] << 8 | data2[3]
            value2 = (data2[4] << 8 | data2[5]) - 255

        except IOError as e: # frequent
            continue

        if ZEROED:
            value1 = value1 - BIAS1
            value2 = value2 - BIAS2

        else:
            BIAS1 = value1
            BIAS2 = value2
            value1 = 0
            value2 = 0
            ZEROED = True

        if lookup_table1 is not None:
            if value1 >= len(lookup_table1): # out of bounds
                value1 = lookup_table1[-1, 0]
                print('Sensor 1 out of bounds')
            else:
                value1 = lookup_table1[value1, 0]

        if lookup_table2 is not None:
            if value2 >= len(lookup_table2): # out of bounds 
                value2 = lookup_table2[-1, 0]
                print('Sensor 2 out of bounds')
            else:
                value2 = lookup_table2[value2, 0]

        average = (value1[0] + value2[0]) / 2
        redis_client.publish('sensor-data', "{:.3f}".format(average))
        time.sleep(INTERVAL / float(1000))
        ELAPSED_TIME = ELAPSED_TIME + INTERVAL

# start process to read from GPIO
@app.route('/start', methods=['POST'])
def start():
    # read from GPIO
    global THREAD_IS_RUN
    global READ_THREAD
    global ELAPSED_TIME
    global lookup_table1
    global lookup_table2

    data = request.get_json()
    size = data['size']

    if data is not None and lookup_table1 is None:
        lookup_table1 = np.load(f'./lookup/{DEV1_ADDRESS}_{size}')

    if data is not None and lookup_table2 is None:
        lookup_table2 = np.load(f'./lookup/{DEV2_ADDRESS}_{size}')

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
    global lookup_table1
    global lookup_table2

    if READ_THREAD is not None:
        THREAD_IS_RUN = False
        READ_THREAD.join()
        READ_THREAD = None
        lookup_table1 = None
        lookup_table2 = None
        return 'Stopped reading from sensor..'
    return 'Sensor not running..'

if __name__ == '__main__':
    # try to connect to sensor
    try:
        DEV_CTX = smbus2.SMBus(DEV_BUS)

    except IOError as e:
        print(e.message)
        sys.exit(1)

    app.run(host='0.0.0.0', port=80)
