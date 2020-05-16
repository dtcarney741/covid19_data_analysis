#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 13 09:11:27 2020

@author: aiden
"""
from datetime import datetime
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib
import threading
import tkinter as tk
import time

import data_analysis


class ConfigGUI:
    def __init__(self, smoothing, iterations, threshold, stepdown, window_name="dy/dx Configuration"):
        self.root = tk.Tk()
        self.root.geometry("330x335")
        self.root.columnconfigure(0, weight=1)
        self.root.title(window_name)
        
        self.break_loop = False
        
        self.config_btns = []
        self.smoothing_btns = []
        self.iter_slider = None
        self.threshold_slider = None
        self.stepdown_slider = None
        
        self.config_var = tk.IntVar(self.root)
        self.smoothing_var = tk.IntVar(self.root)

        
        tk.Label(self.root, text="Configuration", font=("TimesNewRoman", 12)).grid(row=0, column=0 , sticky="w")
        self.config_btns.append(tk.Radiobutton(self.root, text="Auto", variable=self.config_var, value=0))
        self.config_btns.append(tk.Radiobutton(self.root, text="Manual", variable=self.config_var, value=1))
        
        for i, btn in enumerate(self.config_btns):
            btn.grid(row=i, column=1, sticky="w") 
        self.config_btns[0].select()


        tk.Label(self.root, text="").grid(row=2, column=0 , sticky="w")


        tk.Label(self.root, text="Initial Smoothing", font=("TimesNewRoman", 12)).grid(row=3, column=0 , sticky="w")
        self.smoothing_btns.append(tk.Radiobutton(self.root, text="Auto", variable=self.smoothing_var, value=0))
        self.smoothing_btns.append(tk.Radiobutton(self.root, text="None", variable=self.smoothing_var, value=1))        
        self.smoothing_btns.append(tk.Radiobutton(self.root, text="Exponential", variable=self.smoothing_var, value=2))
        self.smoothing_btns.append(tk.Radiobutton(self.root, text="Polynomial", variable=self.smoothing_var, value=3))
        self.smoothing_btns.append(tk.Radiobutton(self.root, text="LOWESS", variable=self.smoothing_var, value=4))
        
        for i, btn in enumerate(self.smoothing_btns):
            btn.grid(row=i + 3, column=1, sticky="w")         
        self.smoothing_btns[smoothing].select()
        
        tk.Label(self.root, text="").grid(row=9, column=0 , sticky="w")
        
        tk.Label(self.root, text="Iterations", font=("TimesNewRoman", 12)).grid(row=10, column=0 , sticky="w")
        self.iter_slider = tk.Scale(self.root, from_=0, to=10, orient="horizontal")
        self.iter_slider.grid(row=10, column=1, sticky="w")   
        self.iter_slider.set(iterations)
        
        tk.Label(self.root, text="").grid(row=11, column=0 , sticky="w")
        
        tk.Label(self.root, text="Outlier Threshold", font=("TimesNewRoman", 12)).grid(row=12, column=0 , sticky="w")
        self.threshold_slider = tk.Scale(self.root, from_=0, to=5, resolution=0.1, orient="horizontal")
        self.threshold_slider.grid(row=12, column=1, sticky="w")   
        self.threshold_slider.set(threshold)
        
        tk.Label(self.root, text="").grid(row=13, column=0 , sticky="w")
        
        tk.Label(self.root, text="Outlier Threshold\nStep Down", justify="left", font=("TimesNewRoman", 12)).grid(row=14, column=0 , sticky="w")
        self.stepdown_slider = tk.Scale(self.root, from_=-1, to=1, resolution=0.05, orient="horizontal")
        self.stepdown_slider.grid(row=14, column=1, sticky="w")   
        self.stepdown_slider.set(stepdown)
        
        tk.Label(self.root, text="").grid(row=15, column=0 , sticky="w")
        
        tk.Button(self.root, text="Close", command=self.__break_loop).grid(row=16, column=1 , sticky="e")
        
        
    def __break_loop(self):
        self.break_loop = True
        
    def mainloop(self):
        destroy_window = True
        while 1:
            try:
                if self.config_var.get() == 0:  # auto is selected so disable other parameters
                    for btn in self.smoothing_btns:
                        btn.config(state="disabled")
                    self.iter_slider.config(state="disabled")
                    self.threshold_slider.config(state="disabled")
                    self.stepdown_slider.config(state="disabled")
                else:
                    for btn in self.smoothing_btns:
                        btn.config(state="normal")
                    self.iter_slider.config(state="normal")
                    self.threshold_slider.config(state="normal")
                    self.stepdown_slider.config(state="normal")
                self.root.update()
                
                if self.break_loop:
                    break 
                
                time.sleep(.1)
    
                auto = not bool(self.config_var.get())
                smoothing = self.smoothing_var.get()
                iters = self.iter_slider.get()
                threshold = self.threshold_slider.get()
                stepdown = self.stepdown_slider.get()
            
            except tk.TclError:
                destroy_window = False
                break
        
        if destroy_window:
            self.root.destroy()
        
        return auto, smoothing, iters, threshold, stepdown


class MatplotlibGUI:
    def __init__(self, integer_to_date_table, x_axis_label, y_axis_label):
        self.figure = None
        self.subplots = None
        self.fig_rows = 0
        self.fig_columns = 0
        
        self.integer_to_date_table = integer_to_date_table
        self.x_axis_label = x_axis_label 
        self.y_axis_label = y_axis_label
        
        self.btn_add_deriv = None
        self.btn_smooth_data = None
        self.config_btns = {}  # derivative_data_index:[button_obj, configuration]
        
        self.x_datasets = []
        self.y_datasets = []
        self.labels_dataset = []

        self.plot_updates = []
        
        self.mainloop_lock = threading.Lock()
    
    def __make_labmda(self, entry):
        return lambda x: self.config_callback(x, entry)
    
    def __get_matrix_index(self, row, column):
        matrix = []
        for i in range(self.fig_rows):
            for j in range(self.fig_columns):
                matrix.append([i, j])
                
        index = matrix.index([row, column])
        return index
    
    def __get_matrix_coordinates(self, index):
        matrix = []
        for i in range(self.fig_rows):
            for j in range(self.fig_columns):
                matrix.append([i, j])
                
        coords = matrix[index]
        return coords
        
    def add_dataset(self, x_datasets, y_datasets, labels):
        self.x_datasets.append(x_datasets)
        self.y_datasets.append(y_datasets)
        self.labels_dataset.append(labels)
        self.plot_updates.append(self.__get_matrix_coordinates(len(self.x_datasets) - 1))
        
    def add_derivative_dataset(self, x_datasets, y_datasets, labels):
        self.add_dataset(x_datasets, y_datasets, labels)
        self.config_btns.update({len(self.x_datasets) - 1:[None, None]})
    
    def remove_all_datasets(self):
        self.x_datasets = []
        self.y_datasets = []
        self.labels_dataset = []
        self.derivative_indexes = []
        
        # add all plots to be updated because all data changed
        for i in range(self.fig_rows):
            for j in range(self.fig_columns):
                self.plot_updates.append([i, j])
        
    def new_figure(self, rows, columns):
        self.figure, self.subplots = plt.subplots(rows, columns, squeeze=False)
        self.fig_rows = rows
        self.fig_columns = columns
        
        self.button = matplotlib.widgets.Button(plt.axes([0, 0, 0.3, 0.05]), "Add Derivative Graph")
        self.button.on_clicked(self.new_derivative)
        
        # invalidate all buttons to None so it will be remade by mainloop
        for entry in self.config_btns:
            self.config_btns[entry][0] = None
            
        # add all plots to be updated because there is a new figure
        for i in range(self.fig_rows):
            for j in range(self.fig_columns):
                self.plot_updates.append([i, j])
        
    def graph_subplot(self, row, column):
        index = self.__get_matrix_index(row, column)
        try:
            self.subplots[row, column].cla()
            for x, y, label in zip(self.x_datasets[index], self.y_datasets[index], self.labels_dataset[index]):
                x_dates = [ datetime.strptime(self.integer_to_date_table.get(integer), '%m-%d-%Y') for integer in x ]
                self.subplots[row, column].plot(x_dates, y, marker='o', label=label)
            
            for label in self.subplots[row, column].get_xticklabels():
                label.set_ha("right")
                label.set_rotation(30)
            self.subplots[row, column].xaxis.set_major_locator(mdates.MonthLocator())
            self.subplots[row, column].xaxis.set_major_formatter(mdates.DateFormatter('%m-%d-%Y'))
            self.subplots[row, column].format_xdata = mdates.DateFormatter('%m-%d-%Y')
            self.subplots[row, column].grid(True)
            self.subplots[row, column].legend()
            self.subplots[row, column].set_xlabel(self.x_axis_label)
            self.subplots[row, column].set_ylabel(self.y_axis_label)
            self.figure.subplots_adjust(bottom=0.25, wspace=.35)
            self.figure.suptitle('Covid-19 Confirmed Cases Plot')
        except IndexError:
            raise IndexError("Dataset at index i=" + str(index) + " does not exist")
        
    def new_derivative(self, event):
        x_dataset = []
        y_dataset = []
        for x, y in zip(self.x_datasets[-1], self.y_datasets[-1]):
            x_data, y_data = data_analysis.get_derivative(
                x,
                y
            )
            x_dataset.append(x_data)
            y_dataset.append(y_data)
        with self.mainloop_lock:
            plt.close(self.figure)
            self.new_figure(self.fig_rows, self.fig_columns + 1)
            self.add_derivative_dataset(
                x_dataset, 
                y_dataset,
                self.labels_dataset[-1]
            )

    def update_derivative(self, index):
        if index in self.config_btns.keys():
            x_dataset = []
            y_dataset = []
            for x, y in zip(self.x_datasets[index - 1], self.y_datasets[index - 1]):
                x_data, y_data = data_analysis.get_derivative(
                    x,
                    y,
                    initial_smoothing = self.config_btns[index][1]["initial_smoothing"],
                    iters=self.config_btns[index][1]["iterations"], 
                    start_threshold=self.config_btns[index][1]["outlier_threshold"], 
                    threshold_stepdown=self.config_btns[index][1]["outlier_stepdown"]
                )
                #TODO: add actual smoothing options
                x_dataset.append(x_data)
                y_dataset.append(y_data)
            self.x_datasets[index] = x_dataset
            self.y_datasets[index] = y_dataset
            
            self.plot_updates.append(self.__get_matrix_coordinates(index))
            
            self.update_derivative(index + 1)  # update all following derivative graphs
       
        
    # def smooth_data_callback(self):
        
        
        
    def config_callback(self, event, entry):   
        c = ConfigGUI(
            self.config_btns[entry][1]["initial_smoothing"],
            self.config_btns[entry][1]["iterations"],
            self.config_btns[entry][1]["outlier_threshold"],
            self.config_btns[entry][1]["outlier_stepdown"],
            "dy/dx " + str(entry) + " Configuration"
            )
        auto, smoothing, iters, threshold, stepdown = c.mainloop()
        
        if not auto:
            self.config_btns[entry][1]["initial_smoothing"] = smoothing
            self.config_btns[entry][1]["iterations"] = iters
            self.config_btns[entry][1]["outlier_threshold"] = threshold
            self.config_btns[entry][1]["outlier_stepdown"] = stepdown
        else:
            self.config_btns[entry][1]["initial_smoothing"] = 0
            self.config_btns[entry][1]["iterations"] = 5
            self.config_btns[entry][1]["outlier_threshold"] = 3
            self.config_btns[entry][1]["outlier_stepdown"] = 0.25
        
        self.update_derivative(entry)




        
    def mainloop(self):
        # make sure all config buttons exist and data is updated
        for entry in self.config_btns:
            if self.config_btns[entry][0] == None:  # if button dne
                btn_size = .7 / (len(self.config_btns))
                btn = matplotlib.widgets.Button(plt.axes([(((entry - 1)*btn_size) + 0.3), 0, btn_size, 0.05]), ("Config dy/dx graph - " + str(entry)))
                btn.on_clicked(self.__make_labmda(entry))
                self.config_btns[entry][0] = btn
            if self.config_btns[entry][1] == None:  # if config dne
                config = {
                    "initial_smoothing":0,
                    "iterations":5,
                    "outlier_threshold":3,
                    "outlier_stepdown":0.25
                }
                self.config_btns[entry][1] = config
        
        # update plots that changed
        with self.mainloop_lock:
            for plot in self.plot_updates:
                self.graph_subplot(plot[0], plot[1])
            self.plot_updates = []
            
        plt.pause(.1)
        
        
        
if __name__ == "__main__":
    # test functionality of configuration screen
    c = ConfigGUI(0, 5, 3, .25)
    auto, smoothing, iters, threshold, stepdown = c.mainloop()
    print(auto)
    print(smoothing)
    print(iters)
    print(threshold)
    print(stepdown)