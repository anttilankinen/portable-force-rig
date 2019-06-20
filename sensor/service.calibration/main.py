import threading
import smbus2
import sys
import time
import json
import numpy as np
from flask import Flask, request
from flask_cors import CORS
from scipy.optimize import curve_fit

app = Flask(__name__)
CORS(app)

INTERVAL = 25 # in ms
READ_THREAD = None
THREAD_IS_RUN = False
DEV_BUS = 1
DEV_CTX = None
ZEROED = False
BIAS = 0
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

def f(x, a, b, c):
    return a * x + b * x ** 2 + c * x ** 3

def calibration_function(train_data):
    # compute calibration mapping using polynomial regression
    x = train_data[:,0]
    y = train_data[:,1]

    valid = np.where(x != -255)
    x = x[valid]
    y = y[valid]

    popt, pcov = curve_fit(f, x, y, bounds=(0, np.inf))
    sensor_range = np.arange(769).reshape(-1, 1)

    return f(sensor_range, popt[0], popt[1], popt[2])

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
        value, frameindex1 = 0, 0
        try:
            data1 = DEV_CTX.read_i2c_block_data(DEV_ADDRESS, 0x00, 6)
            frameindex1 = data1[0] << 8 | data1[1]
            timestamp1 = data1[2] << 8 | data1[3]
            value = (data1[4] << 8 | data1[5]) - 255
            print(value)

        except IOError as e: # frequent
            continue

        if frameindex1 == 0xffff and timestamp1 == 0xffff: #i2c read error
            continue

        if value > 768: #out of bounds
            continue

        if ZEROED:
            value = value - BIAS

        else:
            BIAS = value
            value = 0
            ZEROED = True

        train_data[data_collected, 0] = value
        data_collected = data_collected + 1
        time.sleep(INTERVAL / float(1000))

@app.route('/calibration/begin', methods=['POST'])
def calibrate():
    global READ_THREAD
    global THREAD_IS_RUN
    global train_data

    data = request.get_json()
    weight = 0.00981 * data['weight']

    # read some values, since the first read after connecting will be faulty
    for i in range(5):
        try:
            data1 = DEV_CTX.read_i2c_block_data(DEV_ADDRESS, 0x00, 6)
            frameindex1 = data1[0] << 8 | data1[1]
            timestamp1 = data1[2] << 8 | data1[3]
            value = (data1[4] << 8 | data1[5]) - 255

        except IOError as e: # frequent
            continue

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
        READ_THREAD = None
        train_data = train_data[:data_collected, :]
        return 'Ready for next weight..'
    return 'Calibration already started..'

@app.route('/calibration/end')
def create_lookup():
    global ZEROED
    global BIAS
    global train_data
    global data_collected

    if train_data is None:
        return 'Nothing to be calibrated'

    print('Computing look-up table..')
    np.save('./lookup/main', calibration_function(train_data))
    np.save('./train_data/main', train_data)
    print('Look-up table created!')

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
    app.config.from_object('config.default')
    DEV_ADDRESS = app.config['DEV_ADDRESS']

    try:
        DEV_CTX = smbus2.SMBus(DEV_BUS)

    except IOError as e:
        print(e.message)
        sys.exit(1)

    app.run(host='0.0.0.0', port=7006)
