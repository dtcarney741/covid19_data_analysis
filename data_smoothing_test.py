#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 19 19:03:55 2020

@author: aiden
"""

from scipy import signal
import scipy.interpolate
import matplotlib.pyplot as plt
import numpy as np

import data_analysis

y_data = [
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    5,
    7,
    11,
    29,
    39,
    51,
    78,
    106,
    131,
    157,
    196,
    242,
    381,
    517,
    587,
    694,
    825,
    899,
    987,
    1060,
    1233,
    1495,
    1614,
    1765,
    1952,
    2169,
    2328,
    2703,
    2947,
    3217,
    3563,
    3734,
    3953,
    4075,
    4345,
    4571,
    4712,
    4888,
    5079,
    5317,
    5593,
    5832,
    6026,
    6026,
    6421,
    6539,
    6750,
    6912,
    7088,
    7294,
    7611,
    7888,
    8112,
    8437,
    8691,
    9046,
    9385,
    9668,
    9889,
    10164,
    10464,
    10700,
    11101,
    11373,
    11674,
    11771,
    12086,
    ]
print(len(y_data))
x_data = range(20, len(y_data) + 20)
x, y = data_analysis.derivative(x_data, y_data, smooth=False, iters=1)
x1, y1 = data_analysis.derivative(x_data, y_data, smooth=True, iters=1)

# interp = scipy.interpolate.interp1d(x_data, y_data, kind="linear")
# x_interp = []
# y_interp = []
# for i in range(x_data[0], len(x_data) - 1):
#     x_interp.append(i)
#     y_interp.append(interp(i))

# dx = np.diff(x_interp)
# dy = np.diff(y_interp) / dx

figure, axes = plt.subplots(2, 1, squeeze=False)
axes[0, 0].plot(x, y, color="red")
axes[1, 0].plot(x1, y1, color="red")


# for i in range(10):
#     print(i, len(dx), len(dy))
        
    
#     outliers = data_analysis.detect_outliers(dy, 1)
#     print(len(outliers))
#     new_dx = []
#     new_dy = []
#     for index, point in enumerate(dy):  # replace outliers with interpolated values
#         if point not in outliers:
#             new_dx.append(index)
#             new_dy.append(point)
#         else:
#             new_dx.append(index)
#             val1 = dy[index - 1]
#             val2 = dy[index + 1]
#             new_dy.append(int((val1 + val2) / 2))
#     dy = new_dy
#     x = new_dx
    
#     dy = signal.savgol_filter(
#         dy,
#         9,
#         2
#     )

#     axes[i + 1, 0].plot(x, dy, color="blue")
    
