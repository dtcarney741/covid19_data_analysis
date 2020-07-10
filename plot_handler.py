#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 14 17:06:00 2020

@author: aiden
"""

from datetime import datetime
import plotly.graph_objects as go

import data_analysis


class DataHandler:
    """
    class that contains methods for modifying and storing data that is to 
    be graphed. Contains methods for smoothing data and adding derivative plots
    up to the nth derivative
    """
    def __init__(self, integer_to_date_table, x_datasets, y_datasets, labels):        
        self.num_plots = 0

        self.integer_to_date_table = integer_to_date_table

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


    def new_derivative(self):
        """
        Creates a new derivative of the dataset

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

        self.add_dataset(x_dataset, y_dataset, self.labels_dataset[-1])


    def update_configuration(self, index, new_configuration):
        """
        Updates the configuration parameters

        Parameters
        ----------
        index : int
            The index for which to change the parameters for.
        new_configuration : dict
            Dictionary containing the configuration parameters.

        Returns
        -------
        None.

        """
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


    def format_data(self, y_axis_title, x_axis_title):
        """
        Returns formatted data about a dataset that is condensed and easy to parse

        Parameters
        ----------
        y_axis_title : string
            Label to put on the y axis.
        x_axis_title : string
            Label to put on the x axis.

        Returns
        -------
        plot_entry : list
            List of datasets where each iteration is the nth derivative of the original
            data and i=0 is the original data. Dataset contains the data, label, and 
            the axis titles

        """
        plot_entry = []
        for index in range(self.num_plots):
            x_data = []
            y_data = []
            labels = []
            for x, y, label in zip(self.x_datasets[index], self.y_datasets[index], self.labels_dataset[index]):
                x_dates = [ datetime.strptime(self.integer_to_date_table.get(integer), '%m-%d-%Y') for integer in x ]
                x_data.append(x_dates)
                y_data.append(y)
                labels.append(label)
            
            plot_entry.append({
                "x_data":x_data,
                "y_data":y_data,
                "labels":labels,
                "y_axis_title":("Change in " * index) + y_axis_title,
                "x_axis_title":x_axis_title
            })
            
        return plot_entry



def create_multi_axis_plots(plot_entries, add_axis_title_to_legend=False):  
    """
    Creates plotly plot objects with multiple y axes from a dictionary
    of datasets

    Parameters
    ----------
    plot_entries : dict
        data in format 
        data = {
            plot0:{
                y0:[data_entry1, data_entry2],
                y1:[data_entry1, data_entry2]
                }
            plot1:{
                y0:[data_entry1, data_entry2],
                y1:[data_entry1, data_entry2]
                }
        }

    Returns
    -------
    plot_objects : list
        List of plotly objects.

    """
    plot_objects = []

    for plot_number, plots in plot_entries.items():     
        # create plot object
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
        
        y_axis_titles = []
        x_axis_title = ""

        # add data to the plot on the correct y axis
        for y_axis_id, dataset in plots.items(): 
            for entry in dataset:
                for x, y, label in zip(entry.get("x_data"), entry.get("y_data"), entry.get("labels")):
                    if add_axis_title_to_legend:
                        name = label + " - " + entry.get("y_axis_title")
                    else:
                        name = label
                        
                    if y_axis_id > 1:
                        plot.add_trace(
                            go.Scatter(
                                x=x, 
                                y=y, 
                                mode="lines+markers", 
                                name=name,
                                yaxis=("y" + str(y_axis_id))
                            )
                        )
                    else:
                        plot.add_trace(
                            go.Scatter(
                                x=x, 
                                y=y, 
                                mode="lines+markers", 
                                name=name,
                            )
                        )
                    
                y_axis_titles.append(entry.get("y_axis_title"))   # axis titles will be overwritten with each iteration but they should
                x_axis_title = entry.get("x_axis_title")          # all be the same so it will not matter

                if y_axis_id > 1:
                    plot.update_layout(
                        **{
                            "yaxis" + str(y_axis_id):dict(
                                title=entry.get("y_axis_title"),
                                side=("right" if y_axis_id % 2 == 0 else "left"),
                                overlaying="y"
                            )
                        }
                    )
                else:
                    plot.update_layout(
                        yaxis=dict(title=entry.get("y_axis_title"))
                    )

        title = " and ".join(set(y_axis_titles)) + " vs. " + x_axis_title
        if len(dataset) > 1:
            plot.update_layout(yaxis=dict(title=" and ".join(set(y_axis_titles))))
            
        plot.update_layout(
            title=title,
            xaxis=dict(
                title=x_axis_title
            ),
            font=dict(
                family="Courier New, monospace",
                size=14,
                color="#7f7f7f"
            ),
            showlegend=True,
            legend=dict(x=1.2, y=1.1),
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
        
        plot_objects.append(plot)
    
    return plot_objects

