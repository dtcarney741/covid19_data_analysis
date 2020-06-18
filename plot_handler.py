#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 14 17:06:00 2020

@author: aiden
"""

from datetime import datetime
import plotly.graph_objects as go

import data_analysis


class PlotHandler:
    """
    integeration between datasets and a plotly plot
    has options for adding derivative graphs
    """
    def __init__(self, integer_to_date_table, x_axis_label, y_axis_label, x_datasets, y_datasets, labels):        
        self.num_plots = 0

        self.integer_to_date_table = integer_to_date_table
        self.x_axis_label = x_axis_label
        self.y_axis_label = y_axis_label


        self.original_x = []  # keep copy of unmodified data to do math with
        self.original_y = []
        self.x_datasets = []
        self.y_datasets = []
        self.labels_dataset = []
        self.plot_configurations = []
        
        self.plots_changed = []
        
        self.add_dataset(x_datasets, y_datasets, labels)


    def add_dataset(self, x_datasets, y_datasets, labels):
        """
        Adds the first original dataset to be picked up and plotted by the mainloop

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
        self.original_x.append(x_datasets)
        self.original_y.append(y_datasets)
        
        self.x_datasets.append(x_datasets)
        self.y_datasets.append(y_datasets)
        self.labels_dataset.append(labels)
        self.plot_configurations.append({
            "smooth":False,
            "window_length":9,
            "polyorder":1,
            "iters":2,
            "start_threshold":3,
            "threshold_stepdown":0
        })
        
        self.num_plots += 1

        
        self.plots_changed.append(len(self.x_datasets) - 1)

        

    def remove_derivative_dataset(self, index):
        """
        Clears data for a derivative plot and all subsequent derivative plots
        because they won't have data to be based on

        Returns
        -------
        None.

        """
        i = index  # add plots to be updated
        while i < self.num_plots:
            self.plots_changed.append(i)
            i += 1
        
        self.x_datasets = self.x_datasets[:index]
        self.y_datasets = self.y_datasets[:index]
        self.labels_dataset = self.labels_dataset[:index]
        self.plot_configurations = self.plot_configurations[:index]
        
        self.num_plots = len(self.x_datasets)
        print(self.num_plots)


    def update_plot(self, index):
        if index > self.num_plots or index < 0:
            raise IndexError("No dataset exists for i=" + str(index))
        
        if index > 0:
            suf = lambda n: "%d%s"%(n,{1:"st",2:"nd",3:"rd"}.get(n if n<20 else n%10,"th"))
            title = suf(index) + " derivative of " + self.y_axis_label + " vs. " + self.x_axis_label
        else:
            title = self.y_axis_label + " vs. " + self.x_axis_label
        
        plot = None
        plot = go.Figure()
        plot.update_xaxes(
            rangeslider_visible=False,
            rangeselector=dict(
                buttons=list([
                    dict(count=7, label="1w", step="day", stepmode="backward"),
                    dict(count=14, label="2w", step="day", stepmode="backward"),
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
        
        for x, y, label in zip(self.x_datasets[index], self.y_datasets[index], self.labels_dataset[index]):
            x_dates = [ datetime.strptime(self.integer_to_date_table.get(integer), '%m-%d-%Y') for integer in x ]
            plot.add_trace(
                go.Scatter(
                    x=x_dates, 
                    y=y, 
                    mode="lines+markers", 
                    name=label
                )
            )
            
        plot.update_layout(
            title=title,
            xaxis_title=self.x_axis_label,
            yaxis_title=self.y_axis_label,
            font=dict(
                family="Courier New, monospace",
                size=18,
                color="#7f7f7f"
            ),
            showlegend=True,
            plot_bgcolor="rgb(255, 255, 255)"
        )
        
        plot.update_xaxes(
            tickangle=-45, 
            showgrid=True, 
            gridwidth=1, 
            gridcolor="gray"
        )
        plot.update_yaxes(
            tickangle=0, 
            showgrid=True, 
            gridwidth=1, 
            gridcolor="gray", 
            zeroline=True, 
            zerolinewidth=2, 
            zerolinecolor="black"
        )
        
        return plot
        

    def new_derivative(self):
        x_dataset = []
        y_dataset = []
        for x, y in zip(self.x_datasets[-1], self.y_datasets[-1]):
            x_data, y_data = data_analysis.derivative(
                x,
                y
            )
            x_dataset.append(x_data)
            y_dataset.append(y_data)

        self.add_dataset(x_dataset, y_dataset, self.labels_dataset[-1])


    def update_configuration(self, index, new_configuration):
        if index < self.num_plots and index >= 0:
            self.plot_configurations[index] = new_configuration


    def update_plot_data(self, index):
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
        if index < len(self.x_datasets) and index > 0:
            x_dataset = []
            y_dataset = []
            for x, y in zip(self.x_datasets[index - 1], self.y_datasets[index - 1]):
                x_data, y_data = data_analysis.derivative(x,y)
                if self.plot_configurations[index]["smooth"]:
                    x_data, y_data = data_analysis.smooth_dataset(x_data, y_data, **self.plot_configurations[index])
                x_dataset.append(x_data)
                y_dataset.append(y_data)

            self.x_datasets[index] = x_dataset
            self.y_datasets[index] = y_dataset
            self.plots_changed.append(index)
            
            self.update_plot_data(index + 1)  # update all following derivative graphs


        elif index == 0:
            x_dataset = []
            y_dataset = []
            for i, dataset in enumerate(zip(self.x_datasets[0], self.y_datasets[0])):
                x_data = self.original_x[0][i]
                y_data = self.original_y[0][i]
                if self.plot_configurations[index]["smooth"]:
                    x_data, y_data = data_analysis.smooth_dataset(x_data, y_data, **self.plot_configurations[0])

                x_dataset.append(x_data)
                y_dataset.append(y_data)

            self.x_datasets[0] = x_dataset
            self.y_datasets[0] = y_dataset
            self.plots_changed.append(0)
                        
            self.update_plot_data(index + 1)  # update all following derivative graphs




    # def mainloop(self):
    #     """
    #     The mainloop for the matplotlib window. Handles all plot updates that
    #     were set as a result of user interaction.

    #     Returns
    #     -------
    #     still_running : Bool
    #         If the window is open and still active. If false, then there
    #         will be no future user interaction with the matplotlib window
    #         and user iteraction can continue on

    #     """
    #     # make sure all config buttons exist and data is updated
    #     for entry in self.config_btns:
    #         if self.config_btns[entry][0] is None:  # if button dne
    #             btn_size = .7 / (len(self.config_btns))
    #             btn = matplotlib.widgets.Button(plt.axes([(((entry - 1)*btn_size) + 0.3), 0, btn_size, 0.05]), ("Config dy/dx graph - " + str(entry)))
    #             btn.on_clicked(self.__make_labmda(entry))
    #             self.config_btns[entry][0] = btn
    #         if self.config_btns[entry][1] is None:  # if config dne
    #             config = {
    #                 "smooth":False,
    #                 "window_length":9,
    #                 "polyorder":1,
    #                 "iters":2,
    #                 "start_threshold":3,
    #                 "threshold_stepdown":0
    #             }
    #             self.config_btns[entry][1] = config

    #     # update plots that changed
    #     with self.mainloop_lock:
    #         for plot in self.plot_updates:
    #             self.graph_subplot(plot[0], plot[1])
                
    #         self.plot_updates = []

    #         if not plt.fignum_exists(self.figure.number) and self.allow_exit:
    #             still_running = False
    #         else:
    #             still_running = True

    #     plt.pause(.1)

    #     return still_running

