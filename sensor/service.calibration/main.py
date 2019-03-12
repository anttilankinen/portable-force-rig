import threading
import smbus2
import sys
import time
import json
import numpy as np
from flask import Flask, request
from flask_cors import CORS
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

app = Flask(__name__)
CORS(app)

INTERVAL = 25 # in ms
READ_THREAD = None
THREAD_IS_RUN = False
DEV_BUS = 1
DEV_CTX = None
ZEROED = False
BIAS = 0
CURRENT_ADDRESS = None
CURRENT_SIZE = None
train_data = None
data_collected = 0

def filter_data(dataset):
   # separate different values
    unique_values = np.unique(dataset[:, 1])
    out = np.ndarray([len(unique_values), 2])
    for i, value in enumerate(unique_values):
        input_subset = dataset[dataset[:, 1] == value, 0]
        out[i, 0] = np.median(input_subset)
        out[i, 1] = value
    return out

def calibration_function(train_data, method='cubic'):
    # compute calibration mapping using polynomial regression
    train_data = filter_data(train_data)
    x = train_data[:,0].reshape(-1, 1)
    y = train_data[:,1].reshape(-1, 1)
    test_input = np.arange(np.max(x)).reshape(-1, 1)

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
        spl = InterpolatedUnivariateSpline(x, y, k=min(3, len(x) - 1))
        lookup_table = spl(test_input)
    else:
        print('Incorrect calibration method specified, use "cubic" or "spline"')
        return np.empty([1]) # return this so rest doesn't crash
    return lookup_table

def read_device(weight, datapoints=100):
    global ZEROED
    global BIAS
    global train_data
    global data_collected

    # preallocated space for training data
    data_space = np.concatenate([np.zeros([datapoints,1]),
        weight * np.ones([datapoints, 1])], axis=1)
    if train_data is None:
        train_data = data_space
    else:
        train_data = train_data[:data_collected, :]
        train_data = np.concatenate([train_data, data_space], axis=0)

    data_size = train_data.shape[0]

    while THREAD_IS_RUN:
        value1, frameindex1 = 0, 0
        try:
            data1 = DEV_CTX.read_i2c_block_data(CURRENT_ADDRESS, 0x00, 6)
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

@app.route('/calibration/begin', methods=['POST'])
def calibrate():
    global READ_THREAD
    global THREAD_IS_RUN
    global CURRENT_ADDRESS
    global CURRENT_SIZE
    global train_data

    data = request.get_json()

    if data is not None and CURRENT_ADDRESS is None:
        CURRENT_ADDRESS = data['address']

    if data is not None and CURRENT_SIZE is None:
        CURRENT_SIZE = data['size']

    # read some values, since the first read after connecting will be faulty
    for i in range(5):
        try:
            data1 = DEV_CTX.read_i2c_block_data(CURRENT_ADDRESS, 0x00, 6)
            frameindex1 = data1[0] << 8 | data1[1]
            timestamp1 = data1[2] << 8 | data1[3]
            value1 = (data1[4] << 8 | data1[5]) - 255

        except IOError as e: # frequent
            continue

    weight = 0.00981 * data['weight']
    # if sensor not started
    if data is not None and READ_THREAD is None:
        print('Calibrating for weight: ' + str(weight))
        # start reading from sensor
        THREAD_IS_RUN = True
        READ_THREAD = threading.Thread(target=read_device, args=(weight,))
        READ_THREAD.start()

        # stop reading from sensor
        time.sleep(2)
        print('Finishing..')
        THREAD_IS_RUN = False
        READ_THREAD.join()
        train_data = train_data[:data_collected, :]
        return 'Ready for next weight..'
    return 'Calibration already started..'

@app.route('/calibration/end')
def create_lookup():
    global ZEROED
    global BIAS
    global CURRENT_ADDRESS
    global CURRENT_SIZE
    global train_data
    global data_collected

    if train_data is None:
        return 'Nothing to be calibrated'

    print('Computing look-up table..')
    np.save(f'./lookup/{CURRENT_ADDRESS}_{CURRENT_SIZE}', calibration_function(train_data))
    np.save(f'./train_data/{CURRENT_ADDRESS}_{CURRENT_SIZE}', train_data)
    print('Look-up table created!')

    CURRENT_ADDRESS = None
    CURRENT_SIZE = None
    ZEROED = False
    BIAS = 0
    train_data = None
    data_collected = 0
    print('Calibration done!')
    return 'Calibration done!'

@app.route('/calibration/show')
def show_calibration():
    return { 'calibration': json.dumps(train_data.tolist()) }

if __name__ == '__main__':
    try:
        DEV_CTX = smbus2.SMBus(DEV_BUS)

    except IOError as e:
        print(e.message)
        sys.exit(1)

    app.run(host='0.0.0.0', port=7006)
