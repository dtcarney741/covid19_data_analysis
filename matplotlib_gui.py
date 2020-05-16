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
    """
    class with widgets for getting configuration for smoothing a derivative curve
    """
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


        tk.Label(self.root, text="Configuration", font=("TimesNewRoman", 12)).grid(row=0, column=0, sticky="w")
        self.config_btns.append(tk.Radiobutton(self.root, text="Auto", variable=self.config_var, value=0))
        self.config_btns.append(tk.Radiobutton(self.root, text="Manual", variable=self.config_var, value=1))

        for i, btn in enumerate(self.config_btns):
            btn.grid(row=i, column=1, sticky="w")
        self.config_btns[0].select()


        tk.Label(self.root, text="").grid(row=2, column=0, sticky="w")


        tk.Label(self.root, text="Initial Smoothing", font=("TimesNewRoman", 12)).grid(row=3, column=0, sticky="w")
        self.smoothing_btns.append(tk.Radiobutton(self.root, text="Auto", variable=self.smoothing_var, value=0))
        self.smoothing_btns.append(tk.Radiobutton(self.root, text="None", variable=self.smoothing_var, value=1))
        self.smoothing_btns.append(tk.Radiobutton(self.root, text="Exponential", variable=self.smoothing_var, value=2))
        self.smoothing_btns.append(tk.Radiobutton(self.root, text="Polynomial", variable=self.smoothing_var, value=3))
        self.smoothing_btns.append(tk.Radiobutton(self.root, text="LOWESS", variable=self.smoothing_var, value=4))

        for i, btn in enumerate(self.smoothing_btns):
            btn.grid(row=i + 3, column=1, sticky="w")
        self.smoothing_btns[smoothing].select()

        tk.Label(self.root, text="").grid(row=9, column=0 , sticky="w")

        tk.Label(self.root, text="Iterations", font=("TimesNewRoman", 12)).grid(row=10, column=0, sticky="w")
        self.iter_slider = tk.Scale(self.root, from_=0, to=10, orient="horizontal")
        self.iter_slider.grid(row=10, column=1, sticky="w")
        self.iter_slider.set(iterations)

        tk.Label(self.root, text="").grid(row=11, column=0, sticky="w")

        tk.Label(self.root, text="Outlier Threshold", font=("TimesNewRoman", 12)).grid(row=12, column=0, sticky="w")
        self.threshold_slider = tk.Scale(self.root, from_=0, to=5, resolution=0.1, orient="horizontal")
        self.threshold_slider.grid(row=12, column=1, sticky="w")
        self.threshold_slider.set(threshold)

        tk.Label(self.root, text="").grid(row=13, column=0, sticky="w")

        tk.Label(self.root, text="Outlier Threshold\nStep Down", justify="left", font=("TimesNewRoman", 12)).grid(row=14, column=0, sticky="w")
        self.stepdown_slider = tk.Scale(self.root, from_=-1, to=1, resolution=0.05, orient="horizontal")
        self.stepdown_slider.grid(row=14, column=1, sticky="w")
        self.stepdown_slider.set(stepdown)

        tk.Label(self.root, text="").grid(row=15, column=0, sticky="w")

        tk.Button(self.root, text="Close", command=self.__break_loop).grid(row=16, column=1, sticky="e")


    def __break_loop(self):
        """
        callback function for when close button is pressed

        Returns
        -------
        Nothing
        """
        self.break_loop = True


    def mainloop(self):
        """
        Mainloop of the tkinter window. Reads values set by widgets on the window.
        When close button is pressed or window ceases to exist and an exception is
        thrown, this loop will exit and the data will be returned

        Blocks until complete

        Returns
        -------
        auto : bool
            If derivative parameters should automatically be determined.
        smoothing : int
            The type of smoothing to use on the original graph before derivative is taken.
        iters : int
            Number of iterations of smoothing.
        threshold : Float
            The threshold constant that the outliers algorithm will use.
        stepdown : Float
            The amount to decrase the threshold after each iteration.

        """
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
    """
    integeration between datasets and an interactive matplotlib plot
    has options for adding derivative graphs
    """
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
        self.allow_exit = True


    def __make_labmda(self, entry):
        """
        makes a lambda function that can be used in iteration for setting callback
        funtion with a parameter

        Parameters
        ----------
        entry : int
            Index to pass to config callback which will be used to look at
            which dataset to use for the derivative.

        Returns
        -------
        Lambda function
            callback lambda function with parameter.

        """
        return lambda x: self.config_callback(x, entry)


    def __get_matrix_index(self, row, column):
        """
        Calculates the index in the plot matrix
        Used to see where the dataset for that plot is

        Parameters
        ----------
        row : int
            the row in the plot matrix.
        column : int
            the column in the plot matrix.

        Returns
        -------
        index : int
            The index where those matrix coordinates are found.

        """
        matrix = []
        for i in range(self.fig_rows):
            for j in range(self.fig_columns):
                matrix.append([i, j])

        index = matrix.index([row, column])
        return index


    def __get_matrix_coordinates(self, index):
        """
        Gets matrix coordinates from an index
        Used to see what dataset corresponds to a subplot

        Parameters
        ----------
        index : int
            The index that corresponds to coordinates in the matrix.

        Returns
        -------
        coords : list
            the row and column in the matrix.

        """
        matrix = []
        for i in range(self.fig_rows):
            for j in range(self.fig_columns):
                matrix.append([i, j])

        coords = matrix[index]
        return coords


    def add_dataset(self, x_datasets, y_datasets, labels):
        """
        Adds a dataset to be picked up and graphed by the mainloop

        Parameters
        ----------
        x_datasets : list of type int
            The data for the x axis.
        y_datasets : list of type int
            the data for the y axis.
        labels : list of type str
            The label that will be used for the legend of each dataset.

        Returns
        -------
        None.

        """
        self.x_datasets.append(x_datasets)
        self.y_datasets.append(y_datasets)
        self.labels_dataset.append(labels)
        self.plot_updates.append(self.__get_matrix_coordinates(len(self.x_datasets) - 1))


    def add_derivative_dataset(self, x_datasets, y_datasets, labels):
        """
        Wrapper for adding a derivative dataset to be graphed. This is necessary
        because each derivative dataset will get a corresponding button to change
        the configuration of how it is graphed. Without this, users cannot
        interact with derivative plots as well resulting in noisy data

        Parameters
        ----------
        x_datasets : list of type int
            The data for the x axis.
        y_datasets : list of type int
            The data for the y axis.
        labels : list of type str
            The label that will be used for the legend of each dataset.

        Returns
        -------
        None.

        """
        self.add_dataset(x_datasets, y_datasets, labels)
        self.config_btns.update({len(self.x_datasets) - 1:[None, None]})


    def remove_all_datasets(self):
        """
        Clears all of the data for each subplot and adds it to be updated by the
        mainloop

        Returns
        -------
        None.

        """
        self.x_datasets = []
        self.y_datasets = []
        self.labels_dataset = []
        self.config_btns = {}

        # add all plots to be updated because all data changed
        for i in range(self.fig_rows):
            for j in range(self.fig_columns):
                self.plot_updates.append([i, j])


    def new_figure(self, rows, columns):
        """
        Creates a new matplotlib subplots window most likely because there is
        a change in dimenstions of the subplots. Adds everything to be updated
        by the mainloop and invalidate all of the buttons because they need to
        be remade because they were attached to a previous window. This function
        does not remove any datasets.

        Parameters
        ----------
        rows : int
            The number of rows the subplot matrix will have.
        columns : int
            The number of columsn the subplot matrix will have.

        Returns
        -------
        None.

        """
        self.figure, self.subplots = plt.subplots(rows, columns, squeeze=False)
        self.fig_rows = rows
        self.fig_columns = columns

        self.btn_add_deriv = matplotlib.widgets.Button(plt.axes([0, 0, 0.3, 0.05]), "Add Derivative Graph")
        self.btn_add_deriv.on_clicked(self.new_derivative)

        # invalidate all buttons to None so it will be remade by mainloop
        for entry in self.config_btns:
            self.config_btns[entry][0] = None

        # add all plots to be updated because there is a new figure
        for i in range(self.fig_rows):
            for j in range(self.fig_columns):
                self.plot_updates.append([i, j])


    def graph_subplot(self, row, column):
        """
        Graphs the data for a given subplot. Each subplot will have an index
        in the datasets list that corrosponds to coordinates on the subplot.
        This makes it easy to update plots as the data does not need to be passed
        and it then can be stored and not have a need to be passed to many different
        functions. This function also adds all of the formatting including title,
        axis names, and axis formatting.

        The x data is stored as integers so it also has to perform a conversion to
        dates based on the lookup table passed in the ctor of the class

        Parameters
        ----------
        row : int
            The row in the subplot matrix.
        column : int
            The column in the subplot matrix.

        Raises
        ------
        IndexError
            If dataset for the given subplot does not exist.

        Returns
        -------
        None.

        """
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
            self.figure.suptitle('Covid-19 Confirmed Cases Plot')  # TODO: Change this

        except IndexError:
            raise IndexError("Dataset at index i=" + str(index) + " does not exist")


    def new_derivative(self, _):
        """
        Button callback for adding a new derivative. This looks at the last dataset
        present and differentiates it. It then makes a new figure with new
        dimensions so that the derivative graph will be displayed.

        Parameters
        ----------
        _ : any (not used)
            Necessary so that it is the proper architechture for a callback function.

        Returns
        -------
        None.

        """
        x_dataset = []
        y_dataset = []
        for x, y in zip(self.x_datasets[-1], self.y_datasets[-1]):
            x_data, y_data = data_analysis.get_derivative(
                x,
                y
            )
            x_dataset.append(x_data)
            y_dataset.append(y_data)

        self.allow_exit = False
        with self.mainloop_lock:
            plt.close(self.figure)
            self.new_figure(self.fig_rows, self.fig_columns + 1)
            self.add_derivative_dataset(
                x_dataset,
                y_dataset,
                self.labels_dataset[-1]
            )
        self.allow_exit = True


    def update_derivative(self, index):
        """
        Recalculates the derivative at index and overwrites the data at that index.
        Recursively does this for all following derivatives because they all changed
        because they are all dependent on the previous dataset.
        Recursion will stop once the index of the derivative data does not exist

        Parameters
        ----------
        index : int
            The index of the derivative data.

        Returns
        -------
        None.

        """
        if index in self.config_btns.keys():
            x_dataset = []
            y_dataset = []
            for x, y in zip(self.x_datasets[index - 1], self.y_datasets[index - 1]):
                x_data, y_data = data_analysis.get_derivative(
                    x,
                    y,
                    initial_smoothing=self.config_btns[index][1]["initial_smoothing"],
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


    def config_callback(self, _, entry):
        """
        Starts tkinter window that gets configuration options for
        calculating and smoothing derivative. Updates derivative once
        new parameters have been chosen

        Parameters
        ----------
        _ : any (not used)
            DESCRIPTION.
        entry : int
            the entry in the derivative data index where the new configuration
            parameters will be written.

        Returns
        -------
        None.

        """
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
        """
        The mainloop for the matplotlib window. Handles all plot updates that
        were set as a result of user interaction.

        Returns
        -------
        still_running : Bool
            If the window is open and still active. If false, then there
            will be no future user interaction with the matplotlib window
            and user iteraction can continue on

        """
        # make sure all config buttons exist and data is updated
        for entry in self.config_btns:
            if self.config_btns[entry][0] is None:  # if button dne
                btn_size = .7 / (len(self.config_btns))
                btn = matplotlib.widgets.Button(plt.axes([(((entry - 1)*btn_size) + 0.3), 0, btn_size, 0.05]), ("Config dy/dx graph - " + str(entry)))
                btn.on_clicked(self.__make_labmda(entry))
                self.config_btns[entry][0] = btn
            if self.config_btns[entry][1] is None:  # if config dne
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

            if not plt.fignum_exists(self.figure.number) and self.allow_exit:
                still_running = False
            else:
                still_running = True

        plt.pause(.1)

        return still_running



if __name__ == "__main__":
    # test functionality of configuration screen
    c = ConfigGUI(0, 5, 3, .25)
    auto, smoothing, iters, threshold, stepdown = c.mainloop()
    print(auto)
    print(smoothing)
    print(iters)
    print(threshold)
    print(stepdown)
