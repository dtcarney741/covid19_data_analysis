#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 13 09:58:32 2020

@author: aiden
"""
import numpy as np
from scipy.optimize import curve_fit
from scipy.interpolate import interp1d
import statsmodels.api as sm
import warnings


def exponential_func(x, a, b, c):
        return a * (b**x) + c
    
    
def detect_outliers(dataset, threshold=2):
    outliers=[]
    mean = np.mean(dataset)
    stdev = np.std(dataset)
    if stdev == 0:
        stdev = 0.0000000000000001
    for point in dataset:
        z_score = (point - mean) / stdev
        if abs(z_score) > threshold:
            outliers.append(point)
            
    return outliers
        
        
def fit_curve(x, y, return_all=False):
    if len(x) != len(y):
        raise IndexError("Length of x and y data sets are not equal: ", len(x), "vs.", len(y))
    
    # curve fit method 1 - Exponential
    exp_accuracy = 0
    exp_data = None
    try:
        exp_fit, pcov = curve_fit(exponential_func, x, y)
        exp_accuracy = 0
        # calc accuracy
        for i in range(len(x)):
            exp_val = exponential_func(i, *exp_fit)
            try:
                data_val = y[i]
            except IndexError:
                raise IndexError("Exp curve fit error: Data is not equal size")
            exp_accuracy += abs(exp_val - data_val)
            
        exp_data = exponential_func(x, *exp_fit)
    
    except RuntimeError:  # thrown when max tries to fit curve has been reached (there is no optimal parameters)
        exp_accuracy = 99999999999999999999
        exp_data = x

    
    # curve fit method 2 - Polynomial
    poly_fits = []
    poly_fits_accuracy = []
    for i in range(25):
        with warnings.catch_warnings():  # supress large polynomial warning
            warnings.filterwarnings('error')
            try:
                fit = np.poly1d(np.polyfit(x, y, i))
                poly_fits.append(fit)
            except np.RankWarning:
                pass
        
        # calc accuracy
        fit_accuracy = 0
        for j in range(len(x)):
            poly_val = fit(j)
            data_val = y[j]
            fit_accuracy += abs(poly_val - data_val)
        poly_fits_accuracy.append(fit_accuracy)
    index = poly_fits_accuracy.index(min(poly_fits_accuracy))
    poly_fit = poly_fits[index]
    poly_accuracy = poly_fits_accuracy[index]                     
    
    # curve fit method 3 - LOWESS + interpolation
    lowess = sm.nonparametric.lowess(y, x, frac=.1)
    lowess_x = list(zip(*lowess))[0]
    lowess_y = list(zip(*lowess))[1]
    f = interp1d(lowess_x, lowess_y, bounds_error=False)  # interpolate
    lowess_y = f(x)
    #calc accuracy
    lowess_accuracy = 0
    for i in range(len(x)):
        lowess_val = lowess_y[i]
        data_val = y[i]
        lowess_accuracy += abs(lowess_val - data_val)  
        
    #print(exp_accuracy, poly_accuracy, lowess_accuracy)
    # compare accuracy of each method and return method y data with lowest
    # accuracy number
    # all paramter can be set for debugging purposes
    
    poly_data = poly_fit(x)
    lowess_data = lowess_y
    if return_all:
        return exp_data, poly_data, lowess_data, exp_accuracy, poly_accuracy, lowess_accuracy
    elif exp_accuracy == min([exp_accuracy, poly_accuracy, lowess_accuracy]):
        return exp_data, exp_accuracy
    elif poly_accuracy == min([exp_accuracy, poly_accuracy, lowess_accuracy]):
        return poly_data, poly_accuracy
    else:
        return lowess_data, lowess_accuracy
    
    
def get_derivative(x_dataset, y_dataset, initial_smoothing=0, iters=5, start_threshold=3, threshold_stepdown=.2, debug=False):

    y1, y2, y3, a1, a2, a3 = fit_curve(x_dataset, y_dataset, return_all=True)
    curves = {
        "normal_data":[y_dataset, x_dataset],
        "exp":[y1, x_dataset, a1],
        "poly":[y2, x_dataset, a2],
        "lowess":[y3, x_dataset, a3]
        }
    
    smoothing_enum = ["auto", "normal_data", "exp", "poly", "lowess"]
    if initial_smoothing == 0:  # auto choose initial smoothing based on accuracy
        if a1 == min([a1, a2, a3]):
            ret = "exp"
        elif a1 == min([a1, a2, a3]):
            ret = "poly"
        else:
            ret = "lowess"
    else:
        ret = smoothing_enum[initial_smoothing]
    
        
    
    dx = np.diff(x_dataset)
    dy1 = np.diff(curves["normal_data"][0]) / dx
    dy2 = np.diff(curves["exp"][0]) / dx
    dy3 = np.diff(curves["poly"][0]) / dx
    dy4 = np.diff(curves["lowess"][0]) / dx
    derivatives = {
        "normal_data":{
            "iter0":[dy1, x_dataset[:-1], detect_outliers(dy1)]
            },
        "exp":{
            "iter0":[dy2, x_dataset[:-1], detect_outliers(dy2)]
            },
        "poly":{
            "iter0":[dy3, x_dataset[:-1], detect_outliers(dy3)]
            },
        "lowess":{
            "iter0":[dy4, x_dataset[:-1], detect_outliers(dy4)]
            },
        }
    
    for i in range(iters):
        # pop outliers from each of the smoothed curves
        iter_entry = "iter" + str(i)
        x = derivatives["normal_data"][iter_entry][1]
        y = derivatives["normal_data"][iter_entry][0]
        outliers = detect_outliers(y, threshold=start_threshold - (i * threshold_stepdown))
        new_x = []
        new_y = []
        for index, point in enumerate(y):
            if point not in outliers:
                new_x.append(x[index])
                new_y.append(point)
        dy, _ = fit_curve(new_x, new_y)
        entry = "iter" + str(i + 1)
        derivatives["normal_data"].update({entry:[dy, new_x, outliers]})


        iter_entry = "iter" + str(i)
        x = derivatives["exp"][iter_entry][1]
        y = derivatives["exp"][iter_entry][0]
        outliers = detect_outliers(y, threshold=start_threshold - (i * threshold_stepdown))
        new_x = []
        new_y = []
        for index, point in enumerate(y):
            if point not in outliers:
                new_x.append(x[index])
                new_y.append(point)
        dy, _ = fit_curve(new_x, new_y)
        entry = "iter" + str(i + 1)
        derivatives["exp"].update({entry:[dy, new_x, outliers]})

                
        iter_entry = "iter" + str(i)
        x = derivatives["poly"][iter_entry][1]
        y = derivatives["poly"][iter_entry][0]
        outliers = detect_outliers(y, threshold=start_threshold - (i * threshold_stepdown))
        new_x = []
        new_y = []
        for index, point in enumerate(y):
            if point not in outliers:
                new_x.append(x[index])
                new_y.append(point)
        dy, _ = fit_curve(new_x, new_y)
        entry = "iter" + str(i + 1)
        derivatives["poly"].update({entry:[dy, new_x, outliers]})
                        
                
        iter_entry = "iter" + str(i)
        x = derivatives["lowess"][iter_entry][1]
        y = derivatives["lowess"][iter_entry][0]
        outliers = detect_outliers(y, threshold=start_threshold - (i * threshold_stepdown))
        new_x = []
        new_y = []
        for index, point in enumerate(y):
            if point not in outliers:
                new_x.append(x[index])
                new_y.append(point)
        dy, _ = fit_curve(new_x, new_y)
        entry = "iter" + str(i + 1)
        derivatives["lowess"].update({entry:[dy, new_x, outliers]})
    
    iteration = "iter" + str(iters)
    derivative_x = derivatives[ret][iteration][1]
    derivative_y = derivatives[ret][iteration][0]
    
    if not debug:
        return derivative_x, derivative_y
    else:
        return curves, derivatives
