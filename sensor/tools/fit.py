import numpy as np
from scipy.optimize import curve_fit
import pandas as pd

def f1(x, c1, e1):
    return c1 * x ** e1

def f2(x, c1, e1, c2, e2):
    return c1 * x ** e1 + c2 * x ** e2

def f3(x, c1, e1, c2, e2, c3, e3):
    return c1 * x ** e1 + c2 * x ** e2 + c3 * x ** e3

def f4(x, c1, e1, c2, e2, c3, e3, c4, e4):
    return c1 * x ** e1 + c2 * x ** e2 + c3 * x ** e3 + c4 * x ** e4

def f5(x, c1, e1, c2, e2, c3, e3, c4, e4, c5, e5):
    return c1 * x ** e1 + c2 * x ** e2 + c3 * x ** e3 + c4 * x ** e4 + c5 * x ** e5

def f(x, *p):
    p = np.reshape(p, (-1, 2))
    return sum(p[i, 0] * np.sign(x) * np.abs(x) ** p[i, 1] for i in range(np.shape(p)[0]))

def AIC(y, y_pred, k):
    rss = sum((y - y_pred) ** 2)
    n = len(y)
    return 2 * k + n * np.log(rss)

def calibration_function2(train_data):
    # compute calibration mapping using polynomial regression
    # two possibilites of the function shape are used:
    # 1. second derivative nonnegative
    # 2. second derivative nonpositive
    # this is to avoid "wiggling" of the curve
    x = np.array(train_data.iloc[:,0])
    y = np.array(train_data.iloc[:,1])

    valid = np.where(x != -255)
    x = x[valid]
    y = y[valid]
    aic_min = np.inf
    
    for i in range(5):
        # positive second derivative
        print(i)
        
        # bounds for coefficients (nonnegative) and exponents (larger than one)
        k = 2 * (i + 1)
        bounds = ([0, 1] * (i + 1), np.inf) # coefficients, exponents
        popt, pcov = curve_fit(f, x, y, p0 = np.ones(k), bounds=bounds, maxfev=5000)
        y_pred = f(x, popt)
        aic = AIC(y, y_pred, k)
        if aic < aic_min:
            aic_min = aic
            p = popt
        
        # negative second derivative
        bounds = (0, [np.inf, 1] * (i + 1)) # coefficients, exponents
        popt, pcov = curve_fit(f, x, y, p0 = np.ones(k), bounds=bounds, maxfev=5000)
        y_pred = f(x, popt)
        aic = AIC(y, y_pred, k)
        if aic < aic_min:
            aic_min = aic
            p = popt

    #popt, pcov = curve_fit(f, x, y, bounds=(0, np.inf))
    sensor_range = np.arange(max(x) + 1).reshape(-1, 1)
    print(p)
    return f(sensor_range, p)

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
