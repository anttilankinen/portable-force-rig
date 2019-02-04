import threading
import argparse
import smbus2
import sys
import time
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

def get_args():
    parser = argparse.ArgumentParser()
    # filename of table, required as can mix between buses
    parser.add_argument('-f', '--file', required=True)
    parser.add_argument('-v', '--verbose', default=False)
    # sensor bus
    parser.add_argument('-s', '--sensor', required=True)
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

def calibration_function(train_data):
    # compute calibration mapping using polynomial regression

    x = train_data[:,0]
    y = train_data[:,1]
    valid = np.where(x != -255)
    x = x[valid].reshape(-1, 1)
    # transform to polynomial features
    poly = PolynomialFeatures(degree=3, include_bias=False)
    x = poly.fit_transform(x)

    y = y[valid].reshape(-1, 1)

    lm = LinearRegression(fit_intercept=False).fit(x, y)

    # look-up table
    input = np.arange(769).reshape(-1, 1)
    poly_input = poly.fit_transform(input)
    # look-up table is just an array which can be used just by the index as
    # input is integer-valued
    lookup_table = lm.predict(poly_input)

    return lookup_table



def read_device(weight, datapoints=100):
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
        value1, frameindex1 = 0, 0

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
        time.sleep(2)
        stop_thread()
        train_data = train_data[:data_collected, :]
    print('Computing look-up table')
    table = calibration_function(train_data)
    np.save(args.file, table)
    print('Look-up table saved as "%s"' % (args.file))
