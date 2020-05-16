#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 13 09:58:32 2020

@author: aiden
"""
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit
import numpy as np
import statsmodels.api as sm
import warnings


def exponential_func(x, a, b, c):
    """
    Calculates functional value of an exponential equation

    Parameters
    ----------
    x : int
        variable.
    a : int
        a constant.
    b : int
        a constant.
    c : int
        a constant.

    Returns
    -------
    float
        The functional value of the exponential equation.

    """
    return a * (b**x) + c
    
    
def detect_outliers(dataset, threshold=2):
    """
    Calculates outliers based on the z score algorithm

    Parameters
    ----------
    dataset : list
        dataset to find outliers in.
    threshold : int, optional
        The constant for with the z score must be lower than. The default is 2.

    Returns
    -------
    outliers : list
        A list of the outliers.

    """
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
    """
    Smooths a dataset through various methods. Currently supported modes are
    exponential, polynomial, and lowess. Accuracy score is calculated for each
    method by taking the distance between the new value and the original value.
    As such a lower accuracy number means that the data is closer to the original
    values.
    TODO: accuracy calculation is crude, update with something more robust

    Parameters
    ----------
    x : list of type float
        The x dataset.
    y : list of type float
        the y dataset.
    return_all : bool, optional
        Return as much data as possible. Intedned for debugging purposes. 
        The default is False.

    Raises
    ------
    IndexError
        Raised when datasets are not equal length.

    Returns
    -------
    various
        if return_all == True then there are 6 returns of type int.
        otherwise the y_dataset (which has been smoothed) and the accuracy
        of that dataset to the original is returned. The dataset returned accuracy
        number is lowest.

    """
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
    """
    Calculates and smooths a derivative based on given parameters. Algorithm
    works by doing an initial smoothing then iterating through removing outliers
    and smoothing.

    Parameters
    ----------
    x_dataset : list of type float
        the x axis data.
    y_dataset : list of type float
        the y axis data.
    initial_smoothing : int, optional
        If the data is to be smoothed before algorithm is applied. The default is 0.
    iters : int, optional
        The amount of iterations of the algorithm to perform. The default is 5.
    start_threshold : float, optional
        The constant for which the z score must be less than with the outlier
        calculation algorithm. The default is 3.
    threshold_stepdown : float, optional
        The amount to decrease the threshold constant after each iteration.
        The default is .2.
    debug : bool, optional
        If true, then all data calculated by algorithm is returned.
        The default is False.

    Returns
    -------
    list of type float
        x dataset of derivative.
    list of type float
        y dataset of derivative.

    """
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
