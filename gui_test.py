#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 12 18:51:08 2020

@author: aiden
"""
# import tkinter as tk
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# from matplotlib.figure import Figure

# import numpy as np
# import matplotlib.pyplot as plt

# master = tk.Tk()

# fig = Figure(figsize=(6,6))
# canvas = FigureCanvasTkAgg(fig, master=master)
# canvas.get_tk_widget().pack()

# ax1 = fig.add_subplot(1, 1, 1)
# for i in range(10):
#     y = np.random.random()
#     ax1.scatter(i, y)
#     master.update()
    
# fig.delaxes(ax1)
# fig = Figure()
# ax1 = fig.add_subplot(2, 1, 1)
# canvas = FigureCanvasTkAgg(fig, master=master)
# canvas.get_tk_widget().pack()
# for i in range(10):
#     y = np.random.random()
#     ax1.scatter(i, y)
#     master.update()

# ax2 = fig.add_subplot(2, 1, 2)
# for i in range(10):
#     y = np.random.random()
#     ax2.scatter(i, y)


# #plt.show()
# #master.mainloop()
# import matplotlib.pyplot as plt
# from matplotlib.widgets import Button
# import itertools

# button = Button(plt.axes([0.45, 0.45, 0.2, 0.08]), 'Blink!')


# def button_click(event):
#     button.ax.set_axis_bgcolor('teal')
#     button.ax.figure.canvas.draw()

#     # Also you can add timeout to restore previous background:
#     plt.pause(0.2)
#     button.ax.set_axis_bgcolor(button.color)
#     button.ax.figure.canvas.draw()


# button.on_clicked(button_click)

# plt.show()
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

fig = plt.figure()
def next(event, text):
    print(text)
    pass


axnext = plt.axes([0.81, 0.05, 0.1, 0.075])
bnext = Button(axnext, 'Next')
bnext.on_clicked(lambda x: next(x, bnext.label.get_text()))
bback = Button(plt.axes([0.5, 0.05, 0.1, 0.075]), 'Back')
bback.on_clicked(lambda x: next(x, bback.label.get_text()))
plt.show()