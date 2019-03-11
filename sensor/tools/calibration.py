#!/usr/bin/env python3
import threading
import argparse
import smbus2
import sys
import time
import numpy as np
from scipy.interpolate import UnivariateSpline
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

def get_args():
    parser = argparse.ArgumentParser()
    # filename of table, required as can mix between buses
    # sensor bus
    parser.add_argument('--address', required=True)
    parser.add_argument('--size', required=True)
    return parser.parse_args()

INTERVAL = 25 # in ms
READ_THREAD = None
THREAD_IS_RUN = False
DEV_BUS = 1
DEV_CTX = None
ZEROED = False
BIAS = 0
train_data = None
data_collected = 0

def calibration_function(train_data, method='cubic'):
    """ compute calibration mapping using polynomial regression
    args: N-by-2 array of training data
    keywords: calibration function (cubic polynomial regression or
    smoothing spline """
    
    x = train_data[:,0]
    y = train_data[:,1]
    valid = np.where(x != -255)
    x = x[valid].reshape(-1, 1)
    y = y[valid].reshape(-1, 1)
    test_input = np.arange(769).reshape(-1, 1)

    if method == 'cubic': # use cubic polynomial regression
        # transform to polynomial features
        poly = PolynomialFeatures(degree=3, include_bias=False)
        x = poly.fit_transform(x)
    
        lm = LinearRegression(fit_intercept=False).fit(x, y)
    
        # look-up table
        poly_input = poly.fit_transform(test_input)
        # look-up table is just an array which can be used just by the index as
        # input is integer-valued
        lookup_table = lm.predict(poly_input)
    elif method == 'spline': # use a cubic smoothing spline
        spl = UnivariateSpline(x, y)
        spl.set_smoothing_factor(0.5)
        lookup_table = spl(test_input)
    else:
        print('Incorrect calibration method specified, use "cubic" or "spline"')
        return np.empty([1]) # return this so rest doesn't crash
    return lookup_table

def read_device(weight, datapoints=100):
    global THREAD_IS_RUN
    global DEV_ADDRESS
    global DEV_CTX
    global ZEROED
    global BIAS
    global OPT_VERBOSE
    global train_data
    global data_collected
    timestamp = 1
    # clear up previously unused preallocated space from training data

    # preallocated space for training data
    data_space = np.concatenate([np.zeros([datapoints,1]),
        weight * np.ones([datapoints, 1])], axis=1)
    if train_data is None:
        train_data = data_space
    else:
        train_data = train_data[:data_collected, :]
        train_data = np.concatenate([train_data, data_space], axis=0)

    while THREAD_IS_RUN:
        value1, frameindex1 = 0, 0

            # SingleTac manual section 2.4.3 I2C Read Operation:
            # Where a Read operation is not preceded by a Read Request
            # operation the read location defaults to 128
            # (the sensor output location) and consecutive reads will
            # therefore simply read the default 32 bytes
            # of the sensor data region.
            # Here we read only 6 bytes from 128 to 133

        try:
            data1 = DEV_CTX.read_i2c_block_data(DEV_ADDRESS, 0x00, 6)

            frameindex1 = data1[0] << 8 | data1[1]
            timestamp1 = data1[2] << 8 | data1[3]
            value1 = (data1[4] << 8 | data1[5]) - 255
        except IOError as e: # frequent
            continue

        if frameindex1 == 0xffff and timestamp1 == 0xffff: #i2c read error
            continue

        if value1 > 768: #out of bounds
            continue

        if ZEROED:
            value1 = value1 - BIAS
        else:
            BIAS = value1
            value1 = 0
            ZEROED = True

        train_data[data_collected, 0] = value1
        data_collected = data_collected + 1
        time.sleep(INTERVAL / float(1000))
        print(value1)

def start_thread(weight):
    global READ_THREAD
    global THREAD_IS_RUN
    global ELAPSED_TIME

    # read some values, since the first read after connecting will be faulty
    for i in range(5):
        try:
            data1 = DEV_CTX.read_i2c_block_data(DEV_ADDRESS, 0x00, 6)

            frameindex1 = data1[0] << 8 | data1[1]
            timestamp1 = data1[2] << 8 | data1[3]
            value1 = (data1[4] << 8 | data1[5]) - 255
        except IOError as e: # frequent
            continue


    if READ_THREAD is None:
        ELAPSED_TIME = 0
        THREAD_IS_RUN = True
        READ_THREAD = threading.Thread(target=read_device,
                                       args=(weight,))
        READ_THREAD.start()

def stop_thread():
    global THREAD_IS_RUN
    global READ_THREAD

    THREAD_IS_RUN = False
    READ_THREAD.join()
    READ_THREAD = None

if __name__ == '__main__':
    args = get_args()
    DEV_ADDRESS = int(args.address, 0)
    try:
        DEV_CTX = smbus2.SMBus(DEV_BUS)
    except IOError as e:
        print (e.message)
        sys.exit(1)

    input_string = 'Start calibration? [Y/n] '
    while input(input_string).lower() !=  'n':
        input_string = 'Continue calibration? [Y/n] '
        # first calibrate zero weight
        if ZEROED is False:
            input('Place the sensor on its side and remove any weight' +
                ' from the sensor. Press enter to continue')
            weight = 0
        else:
            weight = float(input('Enter weight (g) '))
            weight = 0.00981 * weight

        start_thread(weight)
        time.sleep(2)
        stop_thread()
        train_data = train_data[:data_collected, :]

    print('Computing look-up table')
    table = calibration_function(train_data)
    np.save(args.address + args.size, table)
    np.save('train_data_' + args.address + '_' + args.size, train_data)
