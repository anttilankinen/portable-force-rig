#/usr/bin/python3
import sys
import time
import threading
import smbus2
import argparse
import numpy as np

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="data.txt")
    parser.add_argument("--calibrated", default=False)
    parser.add_argument("--address1", default=0x04)
    parser.add_argument("--address2", default=0x04)
    
    return parser.parse_args()


INTERVAL = 25 # in ms
ELAPSED_TIME = 0
READ_THREAD = None
THREAD_IS_RUN = False
DEV_BUS = 1
DEV_CTX = None
ZEROED = False
BIAS1 = 0
BIAS2 = 0

def read_device(out_file):
    global ELAPSED_TIME
    global THREAD_IS_RUN
    global DEV1_ADDRESS
    global DEV_CTX
    global ZEROED
    global BIAS1
    global lookup_table
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

            frameindex1 = data1[0] << 8 | data1[1]
            timestamp1 = data1[2] << 8 | data1[3]
            value1 = (data1[4] << 8 | data1[5]) - 255
        except IOError as e: # frequent
            continue

        if ZEROED:
            value1 = value1 - BIAS1
        else:
            BIAS1 = value1
            value1 = 0
            ZEROED = True

        if lookup_table is not None:
            if value1 > 768: #out of bounds
                value1 = lookup_table[-1, 0]
                print('Warning: out of bounds')
            else:
                value1 = lookup_table[value1, 0]

        out_file.write('%i, %.2f\n' % (value1, ELAPSED_TIME))
        print(value1)
        time.sleep(INTERVAL / float(1000))
        ELAPSED_TIME = ELAPSED_TIME + INTERVAL

def read_devices(out_file):
    global ELAPSED_TIME
    global THREAD_IS_RUN
    global DEV1_ADDRESS
    global DEV2_ADDRESS
    global DEV_CTX
    global ZEROED
    global BIAS1
    global BIAS2
    global lookup_table
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

        if ZEROED:
            value1 = value1 - BIAS1
            value2 = value2 - BIAS2
        else:
            BIAS1 = value1
            BIAS2 = value2
            value1 = 0
            value2 = 0
            ZEROED = True

        if lookup_table is not None:
            if value1 > 768: # out of bounds
                value1 = lookup_table[-1, 0]
                print('Sensor 1 out of bounds')
            else:
                value1 = lookup_table[value1, 0]
            if value2 > 768: # out of bounds
                value2 = lookup_table[-1, 1]
                print('Sensor 2 out of bounds')
            else:
                value2 = lookup_table2[value2, 1]

        out_file.write('%i, %i, %.2f\n' % (value1, value2, ELAPSED_TIME))
        print(value1, value2)
        time.sleep(INTERVAL / float(1000))
        ELAPSED_TIME = ELAPSED_TIME + INTERVAL

def start_thread(out_file):
    global READ_THREAD
    global THREAD_IS_RUN
    global ELAPSED_TIME
    global DEV1_ADDRESS
    global DEV2_ADDRESS

    if READ_THREAD is None:
        ELAPSED_TIME = 0
        THREAD_IS_RUN = True
        if DEV1_ADDRESS == DEV2_ADDRESS:
            READ_THREAD = threading.Thread(target=read_device,
                args=(out_file,))
        else:
            READ_THREAD = threading.Thread(target=read_devices,
                args=(out_file,))

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
    DEV1_ADDRESS = int(args.address1, 0)
    DEV2_ADDRESS = int(args.address2, 0)

    if args.calibrated:
        lookup_table = np.load(args.address1)
        if DEV1_ADDRESS == DEV2_ADDRESS:
            lookup_table2 = np.load(args.address2)
            lookup_table = np.concatenate([lookup_table, lookup_table2],
                    axis=1)
    else:
        lookup_table = None

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
