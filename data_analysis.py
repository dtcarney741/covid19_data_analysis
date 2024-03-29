#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 13 09:58:32 2020

@author: aiden
"""
from scipy import signal
import scipy.interpolate
import numpy as np
    
    
def detect_outliers(dataset, threshold=2):
    """
    Calculates outliers based on the z score algorithm where a low z score means 
    that it is highly correlated

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
        

def smooth_dataset(x_data, y_data, **kwargs):
    """
    smooths an evenly spaced dataset based on the savitzky-golay filtering algorithm
    as well as outlier interpolation

    Parameters
    ----------
    x_data : list of type int
        x data, this must be evenly spaced.
    y_data : list of type int
        the data on the y axis.
    **kwargs :
        start_threshold    : the starting threshold for the z score outlier method
        threshold_stepdown : the amount the threshold will decrease after each iteration (lower z score acceptance)
        iters              : the amount of iteration to perform
        window_length      : The length of the filter window (i.e. the number of coefficients). window_length must be a positive odd integer.
        polyorder          : The order of the polynomial used to fit the samples. polyorder must be less than window_length.
        
    Raises
    ------
    ValueError
        Raised if x dataset is not evenly spaced because this will impact smoothing
        algorithm.

    Returns
    -------
    x_data : list of type int
        smoothed x data.
    y_data : list of type int
        smoothed y data.

    """
    # make sure that dataset is evenly spaced by taking set of derivative, if dx
    # is different at all then the length of the set will be greater than 1
    if len(set(np.diff(x_data))) != 1:
        raise ValueError("Not an evenly spaced dataset")
    if len(x_data) != len(y_data):
        raise IndexError("lists are not equal lengths " + str(len(x_data)) + " vs. " + str(len(y_data)))

    for i in range(kwargs.get("iters", 5)):  # conform outliers and smooth
        threshold = kwargs.get("start_threshold", 3) - (i * kwargs.get("threshold_stepdown", 0.25))
        outliers = detect_outliers(y_data, threshold)

        new_x = []
        new_y = []
        for index, point in enumerate(y_data):  # replace outliers with interpolated values
            if point not in outliers:
                new_x.append(x_data[index])
                new_y.append(point)
            else:
                new_x.append(x_data[index])
                if index + 1 < len(y_data) and index - 1 >= 0:
                    val1 = y_data[index - 1]
                    val2 = y_data[index + 1]
                    new_y.append(int((val1 + val2) / 2))
                elif index + 2 > len(y_data):  # outlier is on the right end
                    slope = y_data[index - 1] - y_data[index - 2]
                    new_y.append(y_data[index - 1] + slope)
                elif index - 1 < 0: # outlier is on the left end
                    slope = y_data[index + 2] - y_data[index + 1]
                    new_y.append(y_data[index + 1] - slope)
                else:
                    new_y.append(9999999999999999999)
                
        x_data = new_x
        invalid_points = []
        for i, data_point in enumerate(new_y):              # convert invalid numbers to 0 so that filter works
            if np.isnan(data_point) or data_point == None:  # but keep track of indexes so they can be
                new_y[i] = 0                                # set back to invalid and not plotted once
                invalid_points.append(i)                    # filter has been run

        y_data = signal.savgol_filter(
            new_y,
            kwargs.get("window_length", 9),
            kwargs.get("polyorder", 1)
        )
        
        for i in invalid_points:  # convert invalid datapoints back to nan because there was nothing there originally
            y_data[i] = np.nan    # this is to gaurentee the dataset being at the same x values as those that were passed
        
    return x_data, y_data


def derivative(x_data, y_data):
    """
    calculates the derivative of a dataset and smooths it

    Parameters
    ----------
    x_data : list of type int
        data on the x axis.
    y_data : list of type int
        data on the y axis.
    **kwargs : 
        smooth : boolean value of whether or not to smooth the data
        see smooth_dataset.

    Raises
    ------
    IndexError
        Raised when length of lists is not equal.

    Returns
    -------
    dx : list of type int
        the new x dataset.
    dy : list of type int
        the derivative of the y dataset.

    """
    if len(x_data) != len(y_data):
        raise IndexError("lists are not equal lengths " + str(len(x_data)) + " vs. " + str(len(y_data)))

    # interpolate dataset so that it is for sure a an evenly spaced function
    # this makes the differentiation algorithm work
    interp = scipy.interpolate.interp1d(x_data, y_data, kind="linear")
    x_interp = []
    y_interp = []
    for i in range(x_data[0], x_data[-1]):
        x_interp.append(i)
        y_interp.append(interp(i))

    #dx = np.diff(x_interp)
    dx = x_interp[:-1]
    dy = np.diff(y_interp) / 1  # function is evenly spaced because of 
                                # interpolation method so dx will be 1
    
    # if kwargs.get("smooth", False):
    #     dx, dy = smooth_dataset(dx, dy, **kwargs)
    
    return dx, dy

def moving_average(y_data, window_len):
    """
    calculates the backward moving average over the specified number of data points for the specified data set

    Parameters
    ----------
    y_data : list of data values (int or float)
    window_len : integer with number of data points to include in moving average ()

    Raises
    ------

    Returns
    -------
    moving_average : list
        list of moving average values by day (the first window_len values in the list will be None)
        will return None if something goes wrong

    """
    if window_len < len(y_data) and window_len > 0:
        moving_average_sum = 0
        moving_avg_data = []
        
        for i in range(0,len(y_data)):
            if y_data[i] and not np.isnan(y_data[i]):
                add_value = y_data[i]
            else:
                add_value = 0
            if i == window_len-1:
                moving_average_sum = moving_average_sum + add_value
                moving_average = moving_average_sum/window_len
            elif i >= window_len:
                if y_data[i - window_len] and not np.isnan(y_data[i - window_len]):
                    sub_value = y_data[i - window_len]
                else:
                    sub_value = 0
                moving_average_sum = moving_average_sum + add_value - sub_value
                moving_average = moving_average_sum/window_len
            else:
                moving_average_sum = moving_average_sum + add_value
                moving_average = add_value

            moving_avg_data.append(moving_average)

        return moving_avg_data
                
    else:
        return None
    
def moving_window_ratio(num_data, den_data, window_len):
    """
    calculates the ratio between the sum of two sets of data in a moving window

    Parameters
    ----------
    num_data : list of data values for the numerator of the ratio (int or float)
    den_data : list of data values for the denominator of the ratio (int or float)
    window_len : integer with number of data points to include in each window calculation ()

    Raises
    ------

    Returns
    -------
    moving_average : list
        list of moving average values by day (the first window_len values in the list will be None)
        will return None if something goes wrong

    """
    if window_len < len(num_data) and window_len > 0 and len(num_data) == len(den_data):
        window_num_sum = 0
        window_den_sum = 0
        window_ratio_data = []
        
        for i in range(0,len(num_data)):
            if num_data[i] and not np.isnan(num_data[i]):
                add_num_value = num_data[i]
            else:
                add_num_value = 0
            if den_data[i] and not np.isnan(den_data[i]):
                add_den_value = den_data[i]
            else:
                add_den_value = 0
            if i == window_len-1:
                window_num_sum = window_num_sum + add_num_value
                window_den_sum = window_den_sum + add_den_value
                if window_den_sum != 0:
                    ratio = window_num_sum / window_den_sum
                else:
                    ratio = None
            elif i >= window_len:
                if num_data[i - window_len] and not np.isnan(num_data[i - window_len]):
                    sub_num_value = num_data[i - window_len]
                else:
                    sub_num_value = 0
                if den_data[i - window_len] and not np.isnan(den_data[i - window_len]):
                    sub_den_value = den_data[i - window_len]
                else:
                    sub_den_value = 0                
                window_num_sum = window_num_sum + add_num_value - sub_num_value
                window_den_sum = window_den_sum + add_den_value - sub_den_value
                if window_den_sum != 0:
                    ratio = window_num_sum / window_den_sum
                else:
                    ratio = None
            else:
                window_num_sum = window_num_sum + add_num_value
                window_den_sum = window_den_sum + add_den_value
                ratio = None

            window_ratio_data.append(ratio)

        return window_ratio_data
                
    else:
        return None
 