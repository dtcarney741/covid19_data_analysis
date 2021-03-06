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
    def __init__(self, window_name="dy/dx Configuration", **kwargs):
        self.root = tk.Tk()
        self.root.geometry("330x335")
        self.root.columnconfigure(0, weight=1)
        self.root.title(window_name)

        self.break_loop = False

        self.config_btns = []
        self.window_slider = None
        self.polyorder_slider = None
        self.iter_slider = None
        self.threshold_slider = None
        self.stepdown_slider = None

        self.config_var = tk.IntVar(self.root)

        tk.Label(self.root, text="Smooth Data", font=("TimesNewRoman", 12)).grid(row=0, column=0, sticky="w")
        self.config_btns.append(tk.Radiobutton(self.root, text="No", variable=self.config_var, value=0))
        self.config_btns.append(tk.Radiobutton(self.root, text="Yes", variable=self.config_var, value=1))

        for i, btn in enumerate(self.config_btns):
            btn.grid(row=i, column=1, sticky="w")
        self.config_btns[0].select()


        tk.Label(self.root, text="").grid(row=2, column=0, sticky="w")

        tk.Label(self.root, text="Filter Window Length", font=("TimesNewRoman", 12)).grid(row=3, column=0, sticky="w")
        self.window_slider = tk.Scale(self.root, from_=0, to=15, orient="horizontal")
        self.window_slider.grid(row=3, column=1, sticky="w")
        self.window_slider.set(kwargs.get("window_length", 5))


        tk.Label(self.root, text="").grid(row=5, column=0, sticky="w")

        tk.Label(self.root, text="Filter Polynomial Degree", font=("TimesNewRoman", 12)).grid(row=6, column=0, sticky="w")
        self.polyorder_slider = tk.Scale(self.root, from_=0, to=15, orient="horizontal")
        self.polyorder_slider.grid(row=6, column=1, sticky="w")
        self.polyorder_slider.set(kwargs.get("polyorder", 5))

        tk.Label(self.root, text="").grid(row=9, column=0 , sticky="w")

        tk.Label(self.root, text="Iterations", font=("TimesNewRoman", 12)).grid(row=10, column=0, sticky="w")
        self.iter_slider = tk.Scale(self.root, from_=0, to=10, orient="horizontal")
        self.iter_slider.grid(row=10, column=1, sticky="w")
        self.iter_slider.set(kwargs.get("iters", 5))

        tk.Label(self.root, text="").grid(row=11, column=0, sticky="w")

        tk.Label(self.root, text="Outlier Threshold", font=("TimesNewRoman", 12)).grid(row=12, column=0, sticky="w")
        self.threshold_slider = tk.Scale(self.root, from_=0, to=5, resolution=0.1, orient="horizontal")
        self.threshold_slider.grid(row=12, column=1, sticky="w")
        self.threshold_slider.set(kwargs.get("start_threshold", 3))

        tk.Label(self.root, text="").grid(row=13, column=0, sticky="w")

        tk.Label(self.root, text="Outlier Threshold\nStep Down", justify="left", font=("TimesNewRoman", 12)).grid(row=14, column=0, sticky="w")
        self.stepdown_slider = tk.Scale(self.root, from_=-1, to=1, resolution=0.05, orient="horizontal")
        self.stepdown_slider.grid(row=14, column=1, sticky="w")
        self.stepdown_slider.set(kwargs.get("threshold_stepdown", 0.25))

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
                    self.window_slider.config(state="disabled")
                    self.polyorder_slider.config(state="disabled")
                    self.iter_slider.config(state="disabled")
                    self.threshold_slider.config(state="disabled")
                    self.stepdown_slider.config(state="disabled")
                else:
                    self.window_slider.config(state="normal")
                    self.polyorder_slider.config(state="normal")
                    self.iter_slider.config(state="normal")
                    self.threshold_slider.config(state="normal")
                    self.stepdown_slider.config(state="normal")
                self.root.update()

                if self.break_loop:
                    break

                time.sleep(.1)

                data = {
                    "smooth":bool(self.config_var.get()),
                    "window_length":self.window_slider.get(),
                    "polyorder":self.polyorder_slider.get(),
                    "iters":self.iter_slider.get(),
                    "start_threshold":self.threshold_slider.get(),
                    "threshold_stepdown":self.stepdown_slider.get()
                }

            except tk.TclError:
                destroy_window = False
                break

        if destroy_window:
            self.root.destroy()

        return data




class MatplotlibGUI:
    """
    integeration between datasets and an interactive matplotlib plot
    has options for adding derivative graphs
    """
    def __init__(self, integer_to_date_table, x_axis_label, y_axis_label, plot_title=None):
        self.figure = None
        self.subplots = None
        self.fig_rows = 0
        self.fig_columns = 0

        self.integer_to_date_table = integer_to_date_table
        self.x_axis_label = x_axis_label
        self.y_axis_label = y_axis_label
        if not plot_title:
            self.plot_title = y_axis_label
        else:
            self.plot_title = plot_title

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
            if self.config_btns.get(index):
                suf = lambda n: "%d%s"%(n,{1:"st",2:"nd",3:"rd"}.get(n if n<20 else n%10,"th"))
                deriv_number = list(self.config_btns.keys()).index(index) + 1
                title = suf(deriv_number) + " derivative of " + self.y_axis_label + " vs. " + self.x_axis_label
            else:
                title = self.y_axis_label + " vs. " + self.x_axis_label
                
            self.subplots[row, column].set_title(title, size=10)
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
            self.figure.suptitle("Covid-19 " + self.plot_title + " Plot", fontsize=18)

        except IndexError:
            raise IndexError("Dataset at index i=" + str(index) + " does not exist")


    def new_derivative(self, _):
        """
        Button callback for adding a new (derivative). This looks at the last dataset
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
            x_data, y_data = data_analysis.derivative(
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
                x_data, y_data = data_analysis.derivative(
                    x,
                    y,
                    **self.config_btns[index][1]
                )
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
        c = ConfigGUI("dy/dx " + str(entry) + " Configuration", **self.config_btns[entry][1])
        self.config_btns[entry][1] = c.mainloop()

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
                    "smooth":False,
                    "window_length":9,
                    "polyorder":1,
                    "iters":2,
                    "start_threshold":3,
                    "threshold_stepdown":0
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
    c = ConfigGUI()
    smoothing, window_len, polyorder, iters, threshold, stepdown = c.mainloop()
    print(smoothing)
    print(window_len)
    print(polyorder)
    print(iters)
    print(threshold)
    print(stepdown)
