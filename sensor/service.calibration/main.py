import threading
import smbus2
import sys
import time
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
DEV1_BUS = 1
DEV1_ADDRESS = 0x06
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
    global train_data
    global data_collected
    timestamp = 1

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
            data1 = DEV1_CTX.read_i2c_block_data(DEV1_ADDRESS, 0x00, 6)
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
            value1 = value1 - BIAS1

        else:
            BIAS1 = value1
            value1 = 0
            ZEROED = True

        train_data[data_collected, 0] = value1
        data_collected = data_collected + 1
        time.sleep(INTERVAL / float(1000))

@app.route('/calibration/begin', methods=['POST'])
def calibrate():
    global READ_THREAD
    global THREAD_IS_RUN
    global ELAPSED_TIME
    global train_data

    data = request.get_json()
    # if sensor not started
    if data is not None and READ_THREAD is None:
        print('Calibrating for weight: ' + str(data['weight']))
        # start reading from sensor
        ELAPSED_TIME = 0
        THREAD_IS_RUN = True
        READ_THREAD = threading.Thread(target=read_device, args=(data['weight'],))
        READ_THREAD.start()

        # stop reading from sensor
        time.sleep(2)
        print('Finishing..')
        THREAD_IS_RUN = False
        READ_THREAD.join()
        READ_THREAD = None

        # calibrate
        train_data = train_data[:data_collected, :]
        return 'Ready for next weight..'
    return 'Calibration already started..'

@app.route('/calibration/end')
def create_lookup():
    global ZEROED
    global BIAS1
    global train_data
    global data_collected

    if train_data is None:
        return 'Nothing to be calibrated'

    print('Computing look-up table..')
    table = calibration_function(train_data)
    np.save('./lookup', table)
    print('Look-up table created!')

    ZEROED = False
    BIAS1 = 0
    train_data = None
    data_collected = 0
    print('Calibration done!')

    return 'Calibration done!'

if __name__ == '__main__':
    try:
        DEV1_CTX = smbus2.SMBus(DEV1_BUS)

    except IOError as e:
        print(e.message)
        sys.exit(1)

    app.run(host='0.0.0.0', port=7006)
