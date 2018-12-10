#!/usr/bin/env python
# PPS SingleTact Demo
# Written by Ardhan Madras <ardhan@rocksis.net>
#

import cairo
import sys
import math
import time
import random
import threading
from logo import *
import subprocess
import argparse

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="data.txt")
    parser.add_argument("--verbose", default=False)
    return parser.parse_args()

DEVICE_ENABLED = False
try:
    import smbus
    DEVICE_ENABLED = True
except ImportError:
    pass
res = (1280, 720)
WINDOW_WIDTH = int(res[0])
WINDOW_HEIGHT = int(res[1])
GRAPH_WIDTH = WINDOW_WIDTH - 75
GRAPH_HEIGHT = WINDOW_HEIGHT - 60
GRAPH_X_START = 65
GRAPH_Y_START = 10
INTERVAL = 25 # In ms
ELAPSED_TIME = 0


SECONDS = []
SECOND_MAX = 30
SECOND_SPACE = GRAPH_WIDTH / float(SECOND_MAX)
 
CURVES = []
CURVE_MAX = SECOND_MAX * (1000 / INTERVAL)
CURVE_SPACE = GRAPH_WIDTH / float(CURVE_MAX)

VALUE_MAX = 760
VALUE_MIN = -240
VALUE_STEP = 20
VALUE_SPACE = 50

READ_THREAD = None
THREAD_IS_RUN = False
KEY_IS_PRESSED = False
TOUCH_BEGIN = False
TOUCH_TIME = 0
timecount=0

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
            # Where a Read operation is not preceded by a Read Request operation the read location defaults to
            # 128 (the sensor output location) and consecutive reads will therefore simply read the default 32 bytes
            # of the sensor data region.
            # Here we read only 6 bytes from 128 to 133
        try:
            data = DEV_CTX.read_i2c_block_data(DEV_ADDRESS, 0x00, 6)
            

            frameindex = data[0] << 8 | data[1]
            timestamp = data[2] << 8 | data[3]
            value = (data[4] << 8 | data[5]) - 255
        except IOError as e:
            continue

        if frameindex == 0xffff and timestamp == 0xffff: #i2c read error
            continue
        if value > 768: #out of bounds
            continue
        if OPT_VERBOSE: #debug, launch in terminal with -v
            args = (frameindex, timestamp, value,ELAPSED_TIME / float(1000))
            sys.stderr.write('frameindex=%i timestamp=%i value=%i sec=%.2f\n' % args)
        out_file.write('%i, %i, %i, %.2f\n' % (frameindex, timestamp, value,
            ELAPSED_TIME))
        time.sleep(INTERVAL / float(1000))
        ELAPSED_TIME = ELAPSED_TIME + INTERVAL

def start_thread(out_file, restart=False):
    global READ_THREAD
    global THREAD_IS_RUN
    global ELAPSED_TIME
    global DEV_ADDRESS
    if restart is True:
        THREAD_IS_RUN = False
        READ_THREAD.join()

        if OPT_VERBOSE:
            sys.stderr.write('resetting baseline...\n')
        for i in range(0,2):
            try:
#                data = DEV_CTX.read_i2c_block_data(DEV_ADDRESS, 0, 6)
#                data = [ 0x02, 41, 2, data[4], data[5], 0xff ]
#                DEV_CTX.write_i2c_block_data(DEV_ADDRESS, 41, data)


#write zero to baseline registers
                data = [ 41, 2, 0, 0, 0xff ]
                DEV_CTX.write_i2c_block_data(DEV_ADDRESS, 0x02, data)
                time.sleep(.1)
#read sensor data
                data = DEV_CTX.read_i2c_block_data(DEV_ADDRESS, 0x00, 6)
                msb = data[4]
                lsb = data[5]
#write new baseline registers
                data = [ 41, 2, msb, lsb, 0xff ]
                DEV_CTX.write_i2c_block_data(DEV_ADDRESS, 0x02, data)
                time.sleep(.1)
            except IOError as e:
                if OPT_VERBOSE:
                    sys.stderr.write('write: ' + str(e) + '\n')
            finally:
                break

    ELAPSED_TIME = 0

    THREAD_IS_RUN = True
    READ_THREAD = threading.Thread(target=read_device, args=(out_file,))
    READ_THREAD.start()

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
        DEV_CTX = smbus.SMBus(DEV_BUS)
    except IOError as e:
        print e.message
        sys.exit(1)

    if OPT_VERBOSE:
        print 'I2C bus=%i address=0x%x' % (DEV_BUS, DEV_ADDRESS)
        print 'samplerate=%ims' % INTERVAL

    try:
        start_thread(out_file)
        while 1:
            time.sleep(0.1)
    except KeyboardInterrupt:
        out_file.close()

    stop_thread()

    sys.exit(0)
