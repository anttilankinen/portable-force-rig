import os
import random
import time
import redis
import threading
from flask import Flask
import smbus2

REDIS_PORT = int(os.getenv('REDIS_PORT'))

app = Flask(__name__)
redis_client = redis.StrictRedis(host='redis', port=REDIS_PORT, db=0)
reddis_channel = redis_client.pubsub()

INTERVAL = 25 # in ms
ELAPSED_TIME = 0
READ_THREAD = None
THREAD_IS_RUN = False
DEV_BUS = 1
DEV_ADDRESS = 0x04
DEV_CTX = None

def read_device(out_file):
    global ELAPSED_TIME
    global THREAD_IS_RUN
    global DEV_ADDRESS
    timestamp = 1

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
            data = DEV_CTX.read_i2c_block_data(DEV_ADDRESS, 0x00, 6)
            frameindex = data[0] << 8 | data[1]
            timestamp = data[2] << 8 | data[3]
            value = (data[4] << 8 | data[5]) - 255

        except IOError as e: # frequent
            continue

        if frameindex == 0xffff and timestamp == 0xffff: #i2c read error
            continue

        if value > 768: #out of bounds
            continue

        out_file.write('%i, %i, %i, %.2f\n' % (frameindex, timestamp, value,
            ELAPSED_TIME))

        redis_client.publish('sensor-data', f'{value}')
        time.sleep(INTERVAL / float(1000))
        ELAPSED_TIME = ELAPSED_TIME + INTERVAL

# start process to read from GPIO
@app.route('/start')
def start():
    # read from GPIO
    global out_file
    global THREAD_IS_RUN
    global READ_THREAD
    global ELAPSED_TIME
    global DEV_ADDRESS
    if READ_THREAD is None:
        ELAPSED_TIME = 0
        THREAD_IS_RUN = True
        READ_THREAD = threading.Thread(target=read_device, args=(out_file,))
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
    out_file = open('saved-readings/' + str(int(time.time())) + '.txt', 'w')
    # try to connect to sensor
    try:
        DEV_CTX = smbus2.SMBus(DEV_BUS)
    except IOError as e:
        print(e.message)
        sys.exit(1)
    app.run(host='0.0.0.0', port=80)
