import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

def f(x, a, b, c):
    return a * x + b * x + c * x

def calibration_function2(train_data):
    # compute calibration mapping using polynomial regression
    x = np.array(train_data.iloc[:,0])
    y = np.array(train_data.iloc[:,1])

    valid = np.where(x != -255)
    x = x[valid]#.reshape(-1, 1)
    y = y[valid]#.reshape(-1, 1)

    popt, pcov = curve_fit(f, x, y, bounds=(0, np.inf))
    sensor_range = np.arange(max(x) + 1).reshape(-1, 1)
    
    return f(sensor_range, popt[0], popt[1], popt[2])

data_dir = '~/Projects/portable-force-rig/misc/train_data/'
large_5 = pd.read_csv(data_dir + 'large_5.csv', sep=',', header=None)
large_6 = pd.read_csv(data_dir + 'large_6.csv', sep=',', header=None)
medium_5 = pd.read_csv(data_dir + 'medium_5.csv', sep=',', header=None)
medium_6 = pd.read_csv(data_dir + 'medium_6.csv', sep=',', header=None)

l5 = calibration_function2(large_5)
l6 = calibration_function2(large_6)
m5 = calibration_function2(medium_5)
m6 = calibration_function2(medium_6)

np.savetxt('mediumopt_5.csv', m5, delimiter=',')
np.savetxt('mediumopt_6.csv', m6, delimiter=',')
np.savetxt('largeopt_5.csv', l5, delimiter=',')
np.savetxt('largeopt_6.csv', l6, delimiter=',')



