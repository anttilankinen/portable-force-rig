#!/usr/bin/python3

import sys
import time
import threading
import smbus2
import argparse

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="data.txt")
    parser.add_argument("--verbose", default=False)
    return parser.parse_args()


INTERVAL = 25 # in ms
ELAPSED_TIME = 0
READ_THREAD = None
THREAD_IS_RUN = False
DEV_BUS = 1
DEV1_ADDRESS = 0x05
DEV_CTX = None
DEV2_ADDRESS = 0x06
ZEROED = False
BIAS1 = 0
BIAS2 = 0

def read_device(out_file):
    global ELAPSED_TIME
    global THREAD_IS_RUN
    global DEV1_ADDRESS
    global DEV2_ADDRESS
    global DEV_CTX
    global ZEROED
    global BIAS1
    global BIAS2
    global OPT_VERBOSE
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

        if frameindex1 == 0xffff and timestamp1 == 0xffff: #i2c read error
            continue

        if value1 > 768: #out of bounds
            continue

        if frameindex2 == 0xffff and timestamp2 == 0xffff: #i2c read error
            continue

        if value2 > 768: #out of bounds
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

        out_file.write('%i, %i, %.2f\n' % (value1, value2, ELAPSED_TIME))
        if OPT_VERBOSE:
            print(value1, value2)
        time.sleep(INTERVAL / float(1000))
        ELAPSED_TIME = ELAPSED_TIME + INTERVAL

def start_thread(out_file):
    global READ_THREAD
    global THREAD_IS_RUN
    global ELAPSED_TIME

    if READ_THREAD is None:
        ELAPSED_TIME = 0
        THREAD_IS_RUN = True
        READ_THREAD = threading.Thread(target=read_device, args=(out_file,))
        READ_THREAD.start()
        return 'Started reading from sensor..'
    return 'Sensor already running..'

def stop_thread():
    global THREAD_IS_RUN
    global READ_THREAD

    THREAD_IS_RUN = False
    READ_THREAD.join()

if __name__ == '__main__':
    args = get_args()
    out_file = open(args.file, 'w')
    OPT_VERBOSE = args.verbose
    try:
        DEV_CTX = smbus2.SMBus(DEV_BUS)
    except IOError as e:
        print(e.message)
        sys.exit(1)

    try:
        start_thread(out_file)
        while 1:
            time.sleep(0.1)
    except KeyboardInterrupt:
        out_file.close()

    stop_thread()

    sys.exit(0)
