#!/usr/bin/env python3
import threading
import argparse
import smbus
import sys
import time
import numpy as np
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import DotProduct

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", default="lookup.txt")
    parser.add_argument("--verbose", default=False)
    return parser.parse_args()

INTERVAL = 25 # in ms
READ_THREAD = None
THREAD_IS_RUN = False
DEV1_BUS = 1
DEV1_ADDRESS = 0x04
DEV1_CTX = None
ZEROED = False
BIAS1 = 0
train_data = None
data_collected = 0

def calibration_function(train_data, interval=(0, 1)):
    # compute calibration mapping using gaussian process regression
    # yeah its beefy for the problem but it gives confidence intervals
    # and can give suggestions about which sections to calibrate
    x = train_data[:,0]
    y = train_data[:,1]
    valid = np.where(x != -255)
    x = x[valid].reshape(-1, 1)
    y = y[valid].reshape(-1, 1)

    gpr = GaussianProcessRegressor(kernel=DotProduct(),
        random_state=0).fit(x, y)
    # for lookup table, get predicted means for fast processing
    input = np.arange(769).reshape(-1, 1)
    y_pred, sigma = gpr.predict(input, return_std=True)
    if np.max(y_pred) > interval[1]:
        cutoff = int(np.where(y_pred.reshape(-1) > interval[1])[0][0])
        sigms = sigma[:cutoff]
    lookup_table = np.concatenate([input, y_pred], axis=1)

    return lookup_table, sigma



def read_device(weight, datapoints=200):
    global THREAD_IS_RUN
    global DEV1_ADDRESS
    global DEV1_CTX
    global ZEROED
    global BIAS1
    global OPT_VERBOSE
    global train_data
    global data_collected
    timestamp = 1
    # preallocated space for training data
    data_space = np.concatenate([np.zeros([datapoints,1]),
        weight * np.ones([datapoints, 1])], axis=1)
    if train_data is None:
        train_data = data_space
    else:
        train_data = np.concatenate([train_data, data_space], axis=0)

    data_size = train_data.shape[0]

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
            data1 = DEV1_CTX.read_i2c_block_data(DEV1_ADDRESS, 0x00, 6)
            #data2 = DEV2_CTX.read_i2c_block_data(DEV2_ADDRESS, 0x00, 6)


            frameindex1 = data1[0] << 8 | data1[1]
            timestamp1 = data1[2] << 8 | data1[3]
            value1 = (data1[4] << 8 | data1[5]) - 255
            #frameindex2 = data2[0] << 8 | data2[1]
            #timestamp2 = data2[2] << 8 | data2[3]
            #value2 = (data2[4] << 8 | data2[5]) - 255
        except IOError as e: # frequent
            continue

        if frameindex1 == 0xffff and timestamp1 == 0xffff: #i2c read error
            continue

        if value1 > 768: #out of bounds
            continue

        #if frameindex2 == 0xffff and timestamp2 == 0xffff: #i2c read error
        #    continue

#        if value2 > 768: #out of bounds
#            continue

        if ZEROED:
            value1 = value1 - BIAS1
#            value2 = value2 - BIAS2
        else:
            BIAS1 = value1
#            BIAS2 = value2
            value1 = 0
#            value2 = 0
            ZEROED = True
        time.sleep(INTERVAL / float(1000))
        data_collected = data_collected + 1
        if OPT_VERBOSE:
            print(value1)
        if data_collected == data_size:
            break

def start_thread(weight):
    global READ_THREAD
    global THREAD_IS_RUN
    global ELAPSED_TIME

    if READ_THREAD is None:
        ELAPSED_TIME = 0
        THREAD_IS_RUN = True
        READ_THREAD = threading.Thread(target=read_device,
            args=(weight,))
        READ_THREAD.start()
        print('started running')
        return 'Started reading from sensor..'
    print('already running')
    return 'Sensor already running..'

def stop_thread():
    global THREAD_IS_RUN
    global READ_THREAD

    THREAD_IS_RUN = False
    READ_THREAD.join()
    READ_THREAD = None

if __name__ == '__main__':
    args = get_args()
    OPT_VERBOSE = args.verbose
    try:
        DEV1_CTX = smbus.SMBus(DEV1_BUS)
        #DEV2_CTX = smbus.SMBus(DEV2_BUS)
    except IOError as e:
        print (e.message)
        sys.exit(1)

    input_string = 'Start calibration? [Y/n]'
    while input(input_string).lower() !=  'n':
        input_string = 'Continue calibration? [Y/n]'
        # first calibrate zero weight
        if ZEROED is False:
            input('Place the sensor on its side and remove any weight' +
                ' from the sensor. Press enter to continue')
            weight = 0
        else:
            weight = float(input('Enter weight (N)'))

        start_thread(weight)
        time.sleep(3)
        stop_thread()
        table, stds = calibration_function(train_data)
        max_std = np.max(stds) # least confidence in predicted value
        worst_force_pred = table[np.argmax(max_std), 1] # we are the least
        # confident about this particular force, so maybe we need to calibrate
        # around it
        print(table)
        print(stds)
        print('Largest 95%% confidence interval is %.2f at %i N' %
            (max_std, worst_force_pred))

