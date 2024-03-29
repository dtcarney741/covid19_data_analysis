#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 22:06:37 2020

@author: aiden
"""
import copy
import datetime
import json
import math
import numpy as np
import streamlit as st
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import pycountry_convert as pc
from urllib.request import urlopen
import us
import pickle

import covid19_data
import data_grabber
import plot_handler


class SavGolParameters:
    def __init__(self, window_length=5, poly_order=1, iterations=2, start_threshold=3.0, threshold_stepdown=0.25):
        self.window_length = window_length
        self.poly_order = poly_order
        self.iterations = iterations
        self.start_threshold = start_threshold
        self.threshold_stepdown = threshold_stepdown
        
        
    def toDict(self):
        return {
            "window_length":self.window_length,
            "polyorder":self.poly_order,
            "iters":self.iterations,
            "start_threshold":self.start_threshold,
            "threshold_stepdown":self.threshold_stepdown
        }
        
    
class MovingAverageParameters:
    def __init__(self, window_length=7):
        self.window_length = window_length
        
        

class SmoothingOptionsInfo:
    __instance = None 
    
    @staticmethod 
    def get_instance():
       """ Static access method. """
       if SmoothingOptionsInfo.__instance == None:
          SmoothingOptionsInfo()
       return SmoothingOptionsInfo.__instance
   
    def __init__(self):
        if SmoothingOptionsInfo.__instance != None:
            raise RuntimeError("Constructor has already been called and exists at " + SmoothingOptionsInfo.__instance)
        else:
            SmoothingOptionsInfo.__instance = self
            
            self.data = [{
                "smooth":"none",
                "savgol":SavGolParameters(),
                "moving_average":MovingAverageParameters()
            }]
            
    def get_settings(self, i):
        if 0 <= i < len(self.data):
            return self.data[i]
        else:
            # st.warning("IndexError Avoided: Smoothing options at i=" + str(i) + " does not exist")
            return {
                "smooth":"none",
                "savgol":SavGolParameters(),
                "moving_average":MovingAverageParameters()
            }
        
    def set_settings(self, i, data):
        if 0 <= i < len(self.data):
            self.data[i] = data
        else:
            self.data.append(data)
            
        

class GraphSessionInfo:
    __instance = None 
    
    @staticmethod 
    def get_instance():
       """ Static access method. """
       if GraphSessionInfo.__instance == None:
          GraphSessionInfo()
       return GraphSessionInfo.__instance
   
    def __init__(self):
        if GraphSessionInfo.__instance != None:
            raise RuntimeError("Constructor has already been called and exists at " + GraphSessionInfo.__instance)
        else:
            GraphSessionInfo.__instance = self
            
            self.dates = None
            self.lookup_table = None
            self.plotted_regions = None
            
            self.data_handlers = []
            self.num_derivatives = 0
            self.cached_data_handlers = {}

    def increment_derivative_count(self):
        self.num_derivatives += 1
        
    def set_derivative_count(self, new_amount):
        self.num_derivatives = new_amount
        if self.num_derivatives < 0:
            self.num_derivatives = 0
            
    def set_plotted_regions(self, plotted_regions):
        self.plotted_regions = plotted_regions
        
    def set_dates_data(self, dates_data):
        self.dates = dates_data
    
    def set_lookup_table(self, lookup_table):
        self.lookup_table = lookup_table
        
    def get_data_handler(self, graph_name, data_attribute):
        cache_name = graph_name + "_" + str(self.num_derivatives) + "_" + "".join([i.node_name for i in self.plotted_regions])
        # if self.cached_data_handlers.get(cache_name):  # check if entry is cached and return that
        #     return self.cached_data_handlers.get(cache_name)
        
        # else:
        if True:
            datasets = []
            labels = []
            for node in self.plotted_regions:
                data = getattr(node, data_attribute)
                if callable(data):
                    data = data()
                    
                if data:
                    datasets.append(data)
                    labels.append(get_label(node))
                else:
                    st.warning("No " + graph_name + " data was found for " + node.node_name)
                    
            for i, dataset in enumerate(datasets):
                for j, data_point in enumerate(dataset):
                    if data_point is None:
                        datasets[i][j] = np.nan    
            
            handler = plot_handler.DataHandler(self.lookup_table, self.dates, datasets, labels)
            for i in range(self.num_derivatives):
                handler.new_derivative()
            
            self.cached_data_handlers.update({cache_name:handler})            
            return copy.deepcopy(handler)           


@st.cache(hash_funcs={covid19_data.Covid19_Tree_Node: lambda _: None}, allow_output_mutation=True)
def parse_data(file_urls, us_daily_reports_folder, world_daily_reports_folder):
    """
    gets data from nodes from select nodes. This is cached so that it doesn't
    need to be parsed after each rerun

    Parameters
    ----------
    file_urls : list
        list of urls of time series data from John Hopkins repo.
    us_daily_reports_folder : str
        folder name of us daily reports data from John Hopkins repo.
    world_daily_reports_folder : str
        folder name of world daily reports data from John Hopkins repo..

    Returns
    -------
    data : Covid19_Data
        data that was parsed from files.

    """
    if(os.path.isfile("data")):
        with open("data", "rb") as data_file:
            data = pickle.load(data_file)
            return data
        
    data = covid19_data.Covid19_Data()
    for file_url in file_urls:
        spinner_text = "Reading time series file: " + file_url
        with st.spinner(spinner_text):
            data.read_time_series_data(file_url)

    with st.spinner("Reading US daily reports"):
        data.read_daily_reports_data(us_daily_reports_folder, "us")
    with st.spinner("Reading world daily reports"):
        data.read_daily_reports_data(world_daily_reports_folder, "world")
    # covid19_data.dump_tree_to_file(data.time_series_data_tree, "test.txt")
    with st.spinner("Reading population data"):
        data.read_population_data("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv")
    
    with open("data", "wb") as data_file:
        pickle.dump(data, data_file)
    
    return data

             
@st.cache(allow_output_mutation=True)
def get_graph_session_info():
    """
    Gets object instance for the graph info class so that data will be saved 
    between runs

    Returns
    -------
    GraphSessionInfo
        Instance of singleton class.

    """
    return GraphSessionInfo.get_instance()

@st.cache(allow_output_mutation=True)           
def get_smoothing_options_session_info():
    """
    Gets the object instance of the smoothing class so that data will be saved
    between reruns

    Returns
    -------
    SmoothingOptionsInfo
        Instance of singleton class.

    """
    return SmoothingOptionsInfo.get_instance()

            
def get_smoothing_configuration(uid, areas, previous={}):
    """
    Uses streamlit api to get configuration for smoothing algorithm

    Parameters
    ----------
    uid : any
        a unique id because error will be the same if multiple streamlit boxes have
        the same text.
    areas : streamlit object
        an empty area that a new widget will be placed into.
    previous : dict, optional
        dict that contains previous configuration so that things will be updated
        through streamlit reruns. If not given default values are given.
        The default is {}.

    Returns
    -------
    data : TYPE
        DESCRIPTION.

    """
    # TODO: use st.form because that means things will not update until user clicks a button
    # leading to a more responsive gui
    
    if (previous.get("smooth") == "Moving Average"):
        default = 2
    elif (previous.get("smooth") == "Savitzky Golay"):
        default = 1
    else:
        default = 0
        
    data = previous
    
    radio = areas[0].radio("Smooth Graph", ['None', 'Savitzky Golay', 'Moving Average'], default, key=str(uid) + "1")
    if radio.upper() == "SAVITZKY GOLAY":
        form = areas[1].form(key=str(uid) + "form")
        window_len = form.slider("Filter Window Length", min_value=1, max_value=15, step=2, value=previous.get("window_length", 5), key=str(uid) + "2")
        poly_order = form.slider("Filter Polynomial Degree", min_value=0, max_value=15, step=1, value=previous.get("polyorder", 3), key=str(uid) + "3")
        iters = form.slider("Itrerations", min_value=0, max_value=30, step=1, value=previous.get("iters", 2), key=str(uid) + "4")
        outlier_threshold = form.slider("Outlier Threshold", min_value=0.0, max_value=5.0, step=0.1, value=previous.get("start_threshold", 3.0), key=str(uid) + "5")
        threshold_stepdown = form.slider("Outlier Threshold Stepdown", min_value=-1.0, max_value=1.0, step=.05, value=previous.get("threshold_stepdown", 0.25), key=str(uid) + "6")
        if(form.form_submit_button(label="Ok")):
            data = {
                "smooth":"Savitzky Golay",
                "savgol":SavGolParameters(window_len, poly_order, iters, outlier_threshold, threshold_stepdown),
                "moving_average":previous.get("moving_average")
            }

    elif radio.upper() == "MOVING AVERAGE":
        moving_average_len = areas[1].slider("Moving Average Length", min_value=1, max_value=15, step=1, value=previous.get("window_length", 5), key=str(uid) + "7")
        data = {
            "smooth":"Moving Average",
            "savgol":previous.get("savgol"),
            "moving_average":MovingAverageParameters(moving_average_len)
        }
    else:
        data = {
            "smooth":"none",
            "savgol":previous.get("savgol"),
            "moving_average":previous.get("moving_average")
        }
    return data


def get_label(node):
    """
    Creates a label from a node

    Parameters
    ----------
    node : Covid19_Tree_Node
        the node that will be used to get the name of.

    Returns
    -------
    string
        a string of the label for a given node.

    """
    name = node.node_name
    parent = node.parent
    grand_parent = parent.parent
    if parent:
        if parent.node_name == "World":
            parent = ""
        else:
            parent = ", " + parent.node_name
    else:
        parent = ""
   
    if grand_parent: 
        if grand_parent.node_name == "World":
            grand_parent = ""
        else:
            grand_parent = " (" + grand_parent.node_name + ")"
    else:
        grand_parent = ""
        
    new_name = name + parent + grand_parent
    return new_name.strip()


def get_regions(root_node):
    """
    Gets regions from a tree node using the streamlit api with multiselects
    Has functionality for adding all data to multiselect

    Parameters
    ----------
    root_node : Covid19_Tree_Node
        the root node of regions.

    Returns
    -------
    plotted_areas : list of Covid19_Tree_Node
        list of the regions that will be plotted.

    """
    # find what areas to graph
    region_default = ["US"]
    if st.sidebar.radio("Add all Regions", ['Yes', 'No'], 1) == "Yes":
        region_default = [i.node_name for i in root_node.get_children()]
    regions = st.sidebar.multiselect("Select Regions", sorted([i.node_name for i in root_node.get_children()]), default=region_default)

    regions_nodes = [root_node.get_child_node(name) for name in regions]
    plotted_areas = []
    for region in regions_nodes:
        if region.get_children():
            state_province_default = []
            if st.sidebar.checkbox("Add Data for " + get_label(region), value=True):
                plotted_areas.append(region)
            st.sidebar.markdown("---")
            
            if st.sidebar.radio("Add all States/Provinces in " + get_label(region), ['Yes', 'No'], 1) == "Yes":
                state_province_default = [i.node_name for i in region.get_children()]
            sub_regions = st.sidebar.multiselect(
                    ("State/Province in " + get_label(region)), 
                    sorted([i.node_name for i in region.get_children()]),
                    default=state_province_default
                )
            st.sidebar.markdown("---")
        
        
            sub_regions_nodes = [region.get_child_node(name) for name in sorted(sub_regions)]
            for sub_region in sub_regions_nodes:
                if sub_region.get_children():
                    county_default = []
                    if st.sidebar.radio("Add all Counties in " + get_label(sub_region), ['Yes', 'No'], 1) == "Yes":
                        county_default = [i.node_name for i in sub_region.get_children()]
                    counties = st.sidebar.multiselect(
                        ("Counties in " + get_label(sub_region)), 
                        sorted([i.node_name for i in sub_region.get_children()]),
                        default=county_default
                    )
                    plotted_areas.extend([sub_region.get_child_node(i) for i in counties])
                    
                    if st.sidebar.checkbox("Add Data for " + get_label(sub_region), value=True):
                        plotted_areas.append(sub_region)
                    st.sidebar.markdown("---")
                else:
                    plotted_areas.append(sub_region)
        else:
            plotted_areas.append(region)    

    return plotted_areas


# # get the data to parse
# file = "./data/2020-05-11/CSSEGISandData-COVID-19-5184bec/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv"
# folder = "./data/2020-05-11/CSSEGISandData-COVID-19-5184bec/csse_covid_19_data/csse_covid_19_daily_reports_us"


# # make directories for data to be held if they do not already exist
# if not os.path.isdir(os.path.join(os.path.dirname("."), "data")):
#     os.mkdir(os.path.join(os.path.dirname("."), "data"))

# # check if most recent data is downloaded
# all_subdirs = []
# for d in os.listdir('./data'):
#     bd = os.path.join('./data', d)
#     if os.path.isdir(bd):
#         all_subdirs.append(bd)
        
# if all_subdirs:
#     latest_subdir = max(all_subdirs, key=os.path.getmtime)
# else:
#     latest_subdir = "."
        
# if str(date.today()) not in latest_subdir:                        # download data if it is not present
#     with st.spinner("Retreiving Latest Data, Please Wait..."):
#         data_grabber.retrieve_data()
        
# data_folder = "./data/" + str(date.today()) + "/"
# data_folder = data_folder + os.listdir(data_folder)[0]
# time_series_folder = data_folder + "/csse_covid_19_data/csse_covid_19_time_series"
# us_daily_reports_folder = data_folder + "/csse_covid_19_data/csse_covid_19_daily_reports_us"
# daily_reports_folder = data_folder + "/csse_covid_19_data/csse_covid_19_daily_reports"


time_series_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/"
files = [
    time_series_url + "time_series_covid19_confirmed_US.csv",
    time_series_url + "/time_series_covid19_confirmed_global.csv",
    time_series_url + "/time_series_covid19_deaths_US.csv",
    time_series_url + "/time_series_covid19_deaths_global.csv"
    ]
us_daily_reports_folder = "csse_covid_19_data/csse_covid_19_daily_reports_us"
world_daily_reports_folder = "csse_covid_19_data/csse_covid_19_daily_reports"
covid_data = copy.deepcopy(parse_data(files, us_daily_reports_folder, world_daily_reports_folder))
world_node = covid_data.time_series_data_tree

# world_node = covid19_data.read_tree_from_file("test.txt")

# covid19_data.dump_tree_to_file(world_node, "before.txt")
# covid19_data.dump_tree_to_file(tree2, "after.txt")

# covid19_data.print_tree(world_node, "tree1.txt")
# covid19_data.print_tree(tree2, "tree2.txt")

mode = st.sidebar.selectbox(
    "Mode",
    [
        "Line Chart",
        "Area Chart",
        "Percentage Area Chart",
        "Pie Chart",
        "Bar Chart",
        "Map",
        "Parsed Data - Time Series",
        "Parsed Data - Daily Reports",
        "File Data"
    ]
)
# select the type of graph
data_options = {
    "Confirmed Cases":"confirmed_cases_time_series_data",
    "Deaths":"deaths_time_series_data",
    "Daily New Confirmed Cases":"get_daily_new_cases",
    "Daily New Deaths":"get_daily_new_deaths",
    "Testing":"people_tested_time_series_data",
    "Confirmed Cases Incident":"incident_rate_time_series_data",
    "Confirmed Cases Incident - Calculated":"get_calculated_cases_incident_rate",
    "Deaths Incident":"get_calculated_deaths_incident_rate",
    "Daily New Confirmed Cases Incident" : "get_daily_new_cases_incident_rate",
    "Daily New Deaths Incident" : "get_daily_new_deaths_incident_rate",
    "Log10(mvg_avg(Daily New Confirmed Cases Incident))": "get_log10_7day_moving_average_daily_new_cases_incident_rate",
    "Log2(mvg_avg(Daily New Confirmed Cases Incident))": "get_log2_7day_moving_average_daily_new_cases_incident_rate",
    "Log2(mvg_avg(100*Daily New Deaths Incident))": "get_log2_7day_moving_average_daily_new_deaths_incident_rate",
    "Active Cases":"active_cases_time_series_data",
    "Recovered Cases":"recovered_cases_time_series_data",
    "Recovery Rate":"get_recovery_rate",
    "Confirmed Cases to People Tested Ratio":"get_ratio_confirmed_cases_to_people_tested",
    "New Confirmed Cases to People Tested Ratio":"get_daily_ratio_confirmed_cases_to_people_tested",
    "Case Fatality Rate":"get_case_fatality_rate",
    "30 Day Moving Window Case Fatality Rate":"get_moving_window_case_fatality_rate",
    "Testing Incident":"get_calculated_people_tested_incident_rate"
}

if st.button("Clear Cache"):
    st.caching.clear_cache()

# get x axis data
dates = covid_data.time_series_dates 
int_to_dates_lookup, dates_to_int_lookup = covid_data.create_lookup_tables(min(dates), max(dates))
    
    
if mode == "Line Chart":
    graph_types1 = st.sidebar.multiselect("Axis 1", sorted(data_options.keys()), default=["Confirmed Cases"])
    graph_types2 = st.sidebar.multiselect("Axis 2", sorted(data_options.keys()))
    
    st.sidebar.markdown("---")
    
    plotted_areas = get_regions(world_node)

    # add original datasets to the plot handler     
    x = []
    
    # create look up tables
    for _ in range(len(plotted_areas)):
        x.append([dates_to_int_lookup.get(date.strftime("%m-%d-%Y")) for date in dates])
    
    get_graph_session_info().set_dates_data(x)
    get_graph_session_info().set_lookup_table(int_to_dates_lookup)
    get_graph_session_info().set_plotted_regions(plotted_areas)
       
    add_axis_title_to_legend = False
    
    plot_handlers_axis1 = []
    plot_handlers_axis2 = []
    
    y_axis1_titles = []
    y_axis2_titles = []
    x_axis_title = "Date"
    
    for i, graph in enumerate(graph_types1):
        handler = get_graph_session_info().get_data_handler(graph, data_options.get(graph))
        plot_handlers_axis1.append(handler)
        y_axis1_titles.append(graph)
        if i > 0:
            add_axis_title_to_legend = True
            
    for i, graph in enumerate(graph_types2):
        handler = get_graph_session_info().get_data_handler(graph, data_options.get(graph))
        plot_handlers_axis2.append(handler)
        y_axis2_titles.append(graph)
        if i > 0:
            add_axis_title_to_legend = True
    
    plots_data = [plot_handlers_axis1, plot_handlers_axis2]
    y_axis_titles = [y_axis1_titles, y_axis2_titles]
    
    if len(plots_data) > 1:
        add_axis_title_to_legend = True
            
    # get configuration for each graph
    areas = []
    areas.append(st.empty())
    
    smooth_areas = []  # area for smoothing options
    for j in range(7):
        smooth_areas.append(st.empty())
    data = get_smoothing_configuration(0, smooth_areas, get_smoothing_options_session_info().get_settings(0)) 
    get_smoothing_options_session_info().set_settings(0, data)
    
    for dataset in plots_data:
        for data_entry in dataset:
            # configuration for first plot
            data_entry.update_configuration(0, data)
            data_entry.update_plot_data(0)
    
    
    user_interaction_areas = []
    for i in range(get_graph_session_info().num_derivatives):
        partition = []
        
        partition.append(st.empty())  # area for derivative graph
        
        partition.append(st.empty())  # area for removing derivative
        
        smooth_areas = []  # area for smoothing options
        for j in range(6):
            smooth_areas.append(st.empty())
        partition.append(smooth_areas) 
        
        user_interaction_areas.append(partition)
    
    
    partition = []
    
    partition.append(st.empty())  # area for derivative graph
    
    partition.append(st.empty())  # area for removing derivative
    
    smooth_areas = []  # area for smoothing options
    for j in range(6):
        smooth_areas.append(st.empty())
    partition.append(smooth_areas) 
    new_der_btn = st.empty()
    if new_der_btn.button("New Derivative"):
        for dataset in plots_data:
            for data_entry in dataset:
                data_entry.new_derivative()
                data_entry.update_plot_data(data_entry.num_plots)
        get_graph_session_info().increment_derivative_count()
        user_interaction_areas.append(partition)
        
    
    # configuration for derivative plots -- this also includes option to remove plot
    remove_next_derivative = False
    for i, partition in enumerate(user_interaction_areas):
        if partition[1].button("Remove Derivative", key="7" + str(i + 1)) or remove_next_derivative:
            for dataset in plots_data:
                for data_entry in dataset:
                    data_entry.remove_derivative_dataset(i + 1)
            get_graph_session_info().set_derivative_count(data_entry.num_plots - 1)
    
            remove_next_derivative = True
            partition[1].empty()
            continue  # move to next derivative number if derivative is removed
        
        
        data = get_smoothing_configuration(i + 1, partition[2], get_smoothing_options_session_info().get_settings(i + 1))
        get_smoothing_options_session_info().set_settings(i + 1, data)
        
        for dataset in plots_data:
            for data_entry in dataset:
                data_entry.update_configuration(i + 1, data)
                data_entry.update_plot_data(i + 1)
    
    # fill in graphs with configured areas
    formatted_data = {}
    
    # format data so it can be used by multi axis plots function
    for axis, axis_data in enumerate(plots_data):
        for i, dataset in enumerate(axis_data):
            for derivative_number, data in enumerate(dataset.format_data(y_axis_titles[axis][i], x_axis_title)):
                if not formatted_data.get(derivative_number):
                    formatted_data.update({derivative_number:{axis+1:[data]}})
                else:
                    try:
                        formatted_data.get(derivative_number).get(axis + 1).append(data)
                    except AttributeError:
                        formatted_data.get(derivative_number).update({axis + 1:[data]})

    plot_objects = plot_handler.create_multi_axis_plots(formatted_data, add_axis_title_to_legend)            
    for a in user_interaction_areas:
        areas.append(a[0])
       
    for area, plt in zip(areas, plot_objects):
        area.plotly_chart(plt, use_container_width=True)
        



elif mode == "Area Chart":
    if st.sidebar.checkbox("Select Country"):
        region = st.sidebar.selectbox("Region", sorted([i.node_name for i in world_node.get_children() if i.get_children()]))    
        
        selected_node = None
        if st.sidebar.checkbox("Select State/Province"):
            sub_region = st.sidebar.selectbox("State/Province", sorted([i.node_name for i in world_node.get_child_node(region).get_children() if i.get_children()]))
            selected_node = world_node.get_child_node(region).get_child_node(sub_region)
        else:
            selected_node = world_node.get_child_node(region)

    else:
        selected_node = world_node
    
    
    data_type = st.sidebar.selectbox("Data Table Entry", sorted(data_options.keys()))
    
    columns = {"region":[], "date":[], data_type:[]}
    for node in selected_node.get_children():
        data = getattr(node, data_options.get(data_type))
        if callable(data):
            data = data()
            
        if data:
            for i, date in zip(data, dates):
                columns["region"].append(node.node_name)
                columns["date"].append(date)
                columns[data_type].append(i)
        else:
            st.warning("No " + data_type + " data was found for " + node.node_name)        
    
    df = pd.DataFrame(columns)
    
    fig = px.area(df, x="date", y=data_type, color="region", line_group="region")
    st.plotly_chart(fig, use_container_width=True)  
    
    
    
    
elif mode == "Percentage Area Chart":
    if st.sidebar.checkbox("Select Country"):
        region = st.sidebar.selectbox("Region", sorted([i.node_name for i in world_node.get_children() if i.get_children()]))    
        
        selected_node = None
        if st.sidebar.checkbox("Select State/Province"):
            sub_region = st.sidebar.selectbox("State/Province", sorted([i.node_name for i in world_node.get_child_node(region).get_children() if i.get_children()]))
            selected_node = world_node.get_child_node(region).get_child_node(sub_region)
        else:
            selected_node = world_node.get_child_node(region)

    else:
        selected_node = world_node
    data_type = st.sidebar.selectbox("Data Table Entry", sorted(data_options.keys()))
    
    aggregate = [0 for i in range(len(selected_node.get_children()))]
    for node in selected_node.get_children():
        data = getattr(node, data_options.get(data_type))
        if callable(data):
            data = data()
        if data:
            for i in range(len(aggregate)):
                try:
                    aggregate[i] += data[i]
                except TypeError:  # catch if datapoint is None
                    pass
                except IndexError:
                    pass
        
    columns = {"region":[], "date":[], data_type:[]}
    fig = go.Figure()
    for node in selected_node.get_children():
        data = getattr(node, data_options.get(data_type))
        if callable(data):
            data = data()
        
        if data:
            data_percentage = []
            for sum_data, node_data in zip(aggregate, data):
                try:
                    value = (node_data / sum_data) * 100
                except:
                    value = 0
                data_percentage.append(value)
            fig.add_trace(go.Scatter(
                x=dates, 
                y=data_percentage,
                mode='lines+markers',
                stackgroup='one',
                name=node.node_name,
                groupnorm='percent' # sets the normalization for the sum of the stackgroup
            ))
        else:
            st.warning("No " + data_type + " data was found for " + node.node_name)        

    st.plotly_chart(fig, use_container_width=True)  

    
    
elif mode == "Pie Chart":
    if st.sidebar.checkbox("Select Country"):
        region = st.sidebar.selectbox("Region", sorted([i.node_name for i in world_node.get_children() if i.get_children()]))    
        
        selected_node = None
        if st.sidebar.checkbox("Select State/Province"):
            sub_region = st.sidebar.selectbox("State/Province", sorted([i.node_name for i in world_node.get_child_node(region).get_children() if i.get_children()]))
            selected_node = world_node.get_child_node(region).get_child_node(sub_region)
        else:
            selected_node = world_node.get_child_node(region)

    else:
        selected_node = world_node
    data_type = st.sidebar.selectbox("Data Type", sorted(data_options.keys()))
    

    columns = {"region":[], "date":[], data_type:[]}
    for node in selected_node.get_children():
        data = getattr(node, data_options.get(data_type))
        if callable(data):
            data = data()
        
        if data:
            columns["region"].append(node.node_name)
            columns["date"].append(dates[-1])
            columns[data_type].append(data[-1])
        else:
            date = dates[-1].strftime("%m/%d/%Y")
            st.warning("No " + data_type + " data was found for " + node.node_name + " on " + date)        
    
    df = pd.DataFrame(columns)
    date = dates[-1].strftime("%m/%d/%Y")
    fig = px.pie(df, values=data_type, names="region", title=data_type + " data on " + date)
    # fig = px.histogram(df, x="date", y=data_type, color="region")

    st.plotly_chart(fig, use_container_width=True)  
    
    aggregate = sum([0 if i == None else i for i in columns[data_type]])
    st.write("Aggregate: ", aggregate)



        
elif mode == "Bar Chart":
    if st.sidebar.checkbox("Select Country"):
        region = st.sidebar.selectbox("Region", sorted([i.node_name for i in world_node.get_children() if i.get_children()]))    
        
        selected_node = None
        if st.sidebar.checkbox("Select State/Province"):
            sub_region = st.sidebar.selectbox("State/Province", sorted([i.node_name for i in world_node.get_child_node(region).get_children() if i.get_children()]))
            selected_node = world_node.get_child_node(region).get_child_node(sub_region)
        else:
            selected_node = world_node.get_child_node(region)

    else:
        selected_node = world_node
    data_types = st.sidebar.multiselect("Data Type", sorted(data_options.keys()))

    fig = go.Figure()
    aggregates = []
    for data_type in data_types:
        regions = []
        node_data = []
        for node in selected_node.get_children():
            data = getattr(node, data_options.get(data_type))
            if callable(data):
                data = data()
            
            if data:
                node_data.append(data[-1])
                regions.append(node.node_name)
            else:
                date = dates[-1].strftime("%m/%d/%Y")
                st.warning("No " + data_type + " data was found for " + node.node_name + " on " + date)        
        fig.add_trace(go.Bar(
            x=regions,
            y=node_data,
            name=data_type,
        ))
        aggregates.append(sum([0 if i == None else i for i in node_data]))

    if st.checkbox("Stack Bar Graph"):
        fig.update_layout(barmode='stack')

    st.plotly_chart(fig, use_container_width=True)  

    for data_type, aggregate in zip(data_types, aggregates):
        st.write(data_type, " Aggregate: ", aggregate)

    
elif mode == "Map":
    map_type = st.sidebar.selectbox("Map Mode", ["US Counties", "US States", "US State", "European Countries", "World"])
    data_type = st.sidebar.selectbox("Color Mode", sorted(data_options.keys()))
    map_color_scale = "turbid"
    if st.sidebar.checkbox("Allow Animations", False):
        animations = True
    else:
        animations = False
    st.sidebar.markdown("###### (Turning off animations will speed up loading times significantly)")
    st.sidebar.markdown("---")
    
    if map_type == "US Counties":
        with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
            counties_fips = json.load(response)
        states = [i for i in  world_node.get_child_node("US").get_children()]
        counties = []
        for state in states:
            counties.extend(state.get_children())
        
        # filter out some dates otherwise animation will be way to big to handle
        days_in_between = math.ceil((dates[-1] - dates[0]).days / 13)  # 13 the max number of data points for counties
                                                                       # otherwise the dataset becomes too big for the animation
                                                                       # to handle
        valid_dates = [dates[-1]]
        i = 1
        while valid_dates[-1] - (datetime.timedelta(days=days_in_between * i)) > dates[0]:
            valid_dates.append(valid_dates[-1] - (datetime.timedelta(days=days_in_between * i)))
        
        anim_data = {}
        no_anim_data = {}
        zero_data = []
        j = 0
        
        for i, county in enumerate(counties):
            if county.fips and county.fips in [i.get("id") for i in list(counties_fips.values())[1]]:
                node_data = getattr(county, data_options.get(data_type))
                if callable(node_data):
                    node_data = node_data()
                if node_data:
                    d = {
                        "fips":county.fips,
                        "data":node_data[-1] if node_data[-1] is not None else 0,
                        "county":county.node_name + ", " + county.parent.node_name
                        
                    }
                    no_anim_data.update({j:d})
                    for k, datapoint in enumerate(node_data):
                        d = {
                            "fips":county.fips,
                            "county":county.node_name + ", " + county.parent.node_name,
                            "data":datapoint if datapoint is not None else 0,
                            "date":str(dates[k]),                            
                        }
                        if dates[k] in valid_dates:
                            anim_data.update({j:d})
                            j += 1
                        
                    if node_data[-1] == 0 or (node_data and node_data[-1] is None):
                        zero_data.append(county.node_name + ", " + county.parent.node_name)
        df_anim = pd.DataFrame.from_dict(anim_data, orient='index')
        df_no_anim = pd.DataFrame.from_dict(no_anim_data, orient='index')
        
        if not df_anim.empty and not df_no_anim.empty and animations:
            fig = px.choropleth(
                df_anim, 
                geojson=counties_fips, 
                locations='fips', 
                color='data',
                animation_frame="date",
                color_continuous_scale=map_color_scale,
                scope="usa",
                labels={'data':data_type},
                hover_name="county"
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("## Areas with 0 " + data_type + "as of Today")
            for i in zero_data:
                st.markdown("* " + i)
        elif not df_anim.empty and not df_no_anim.empty:
            fig = px.choropleth(
                df_no_anim, 
                geojson=counties_fips, 
                locations='fips', 
                color='data',
                color_continuous_scale=map_color_scale,
                scope="usa",
                labels={'data':data_type},
                hover_name="county"
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("## Areas with 0 " + data_type + "as of Today")
            for i in zero_data:
                st.markdown("* " + i)            
        else:
            st.warning("No data for counties available with selected data type")

    elif map_type == "US States":
        states = [i for i in  world_node.get_child_node("US").get_children()]

        anim_data = {}
        no_anim_data = {}
        zero_data = []
        j = 0
        for i, state in enumerate(states):
            node_data = getattr(state, data_options.get(data_type))
            if callable(node_data):
                node_data = node_data()
            if node_data and us.states.lookup(state.fips):
                d = {
                    "state_code":us.states.lookup(state.fips).abbr,
                    "data":node_data[-1] if node_data[-1] is not None else 0,
                    "state":state.node_name
                    
                }
                no_anim_data.update({j:d})
                for k, datapoint in enumerate(node_data):
                    d = {
                        "state_code":us.states.lookup(state.fips).abbr,
                        "data":datapoint if datapoint is not None else 0,
                        "date":str(dates[k]),
                        "state":state.node_name
                        
                    }

                    anim_data.update({j:d})
                    j += 1
                
                if node_data[-1] == 0 or (node_data and node_data[-1] is None):
                    zero_data.append(state.node_name + ", " + state.parent.node_name)
            
        df_anim = pd.DataFrame.from_dict(anim_data, orient='index')
        df_no_anim = pd.DataFrame.from_dict(no_anim_data, orient='index')

        if not df_anim.empty and not df_no_anim.empty and animations:
            fig = px.choropleth(
                df_anim, 
                locations='state_code', 
                color="data",
                animation_frame="date",
                locationmode="USA-states",
                color_continuous_scale=map_color_scale,
                scope="usa",
                labels={'data':data_type},
                hover_name="state",
            )
            delay = st.sidebar.number_input("Animation Delay", min_value=5, max_value=1000, value=5)
            fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = delay

            st.plotly_chart(fig, use_container_width=True)
            st.markdown("## Areas with 0 " + data_type + " as of Today")
            for i in zero_data:
                st.markdown("* " + i)
        elif not df_anim.empty and not df_no_anim.empty:
            fig = px.choropleth(
                df_no_anim, 
                locations='state_code', 
                color="data",
                locationmode="USA-states",
                color_continuous_scale=map_color_scale,
                scope="usa",
                labels={'data':data_type},
                hover_name="state",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("## Areas with 0 " + data_type + " as of Today")
            for i in zero_data:
                st.markdown("* " + i)            
                
        else:
            st.warning("No data for states available with selected data type")

    elif map_type == "US State":
        state = st.sidebar.selectbox("Select State", [i.node_name for i in  world_node.get_child_node("US").get_children()])
        
        with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
            counties_fips = json.load(response)
        
        counties = [i for i in world_node.get_child_node("US").get_child_node(state).get_children()]
        
        # filter out some dates otherwise animation will be way to big to handle
        days_in_between = math.ceil((dates[-1] - dates[0]).days / 13)  # 13 the max number of data points for counties
                                                                       # otherwise the dataset becomes too big for the animation
                                                                       # to handle
        valid_dates = [dates[-1]]
        i = 1
        while valid_dates[-1] - (datetime.timedelta(days=days_in_between * i)) > dates[0]:
            valid_dates.append(valid_dates[-1] - (datetime.timedelta(days=days_in_between * i)))
        
        anim_data = {}
        no_anim_data = {}
        zero_data = []
        j = 0
        for i, county in enumerate(counties):
            if county.fips and county.fips in [i.get("id") for i in list(counties_fips.values())[1]]:
                node_data = getattr(county, data_options.get(data_type))
                if callable(node_data):
                    node_data = node_data()
                if node_data:
                    d = {
                        "fips":county.fips,
                        "data":node_data[-1] if node_data[-1] is not None else 0,
                        "county":county.node_name + ", " + county.parent.node_name
                        
                    }
                    no_anim_data.update({j:d})
                    for k, datapoint in enumerate(node_data):
                        d = {
                            "fips":county.fips,
                            "data":datapoint if datapoint is not None else 0,
                            "county":county.node_name + ", " + county.parent.node_name,
                            "date":str(dates[k])
                        }
                        if dates[k] in valid_dates:
                            anim_data.update({j:d})
                            j += 1

                    if node_data[-1] == 0:
                        zero_data.append(county.node_name + ", " + county.parent.node_name)

        df_anim = pd.DataFrame.from_dict(anim_data, orient='index')
        df_no_anim = pd.DataFrame.from_dict(no_anim_data, orient='index')
        
        if not df_anim.empty and not df_no_anim.empty and animations:
            fig = px.choropleth(
                df_anim, 
                geojson=counties_fips, 
                animation_frame="date",
                locations='fips', 
                color='data',
                color_continuous_scale=map_color_scale,
                scope="usa",
                center={"lon":float(world_node.get_child_node("US").get_child_node(state).longitude), "lat":float(world_node.get_child_node("US").get_child_node(state).latitude)},
                labels={'data':data_type},
                hover_name="county",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("## Areas with 0 " + data_type + " as of Today")
            for i in zero_data:
                st.markdown("* " + i)
                
        elif not df_anim.empty and not df_no_anim.empty:
            fig = px.choropleth(
                df_no_anim, 
                geojson=counties_fips, 
                locations='fips', 
                color="data",
                color_continuous_scale=map_color_scale,
                scope="usa",
                center={"lon":float(world_node.get_child_node("US").get_child_node(state).longitude), "lat":float(world_node.get_child_node("US").get_child_node(state).latitude)},
                labels={'data':data_type},
                hover_name="county",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("## Areas with 0 " + data_type + " as of Today")
            for i in zero_data:
                st.markdown("* " + i)            
                
        else:
            st.warning("No data for state available with selected data type")
                          
    elif map_type == "European Countries":
        countries = []
        for country in world_node.get_children():
            try:
                iso2 = pc.country_alpha3_to_country_alpha2(country.iso3)
            except KeyError:
                continue
            try:
                continent = pc.country_alpha2_to_continent_code(iso2)
                if continent == "EU":
                    countries.append(country)
            except KeyError:
                continue
            
        anim_data = {}
        no_anim_data = {}
        zero_data = []
        j = 0
        for i, country in enumerate(countries):
            node_data = getattr(country, data_options.get(data_type))
            if callable(node_data):
                node_data = node_data()
            if node_data and country.iso3:
                d = {
                    "iso_code":country.iso3,
                    "data":node_data[-1] if node_data[-1] is not None else 0,
                    "country":country.node_name
                }
                no_anim_data.update({j:d})
                for k, datapoint in enumerate(node_data):
                    d = {
                        "iso_code":country.iso3,
                        "data":datapoint if datapoint is not None else 0,
                        "country":country.node_name,
                        "date":str(dates[k])
                    }

                    anim_data.update({j:d})
                    j += 1

                j += 1
                if node_data[-1] == 0 or (node_data and node_data[-1] is None):
                    zero_data.append(country.node_name)
                
        df_anim = pd.DataFrame.from_dict(anim_data, orient='index')
        df_no_anim = pd.DataFrame.from_dict(no_anim_data, orient='index')
        
        if not df_anim.empty and not df_no_anim.empty and animations:
            fig = px.choropleth(
                df_anim, 
                locations='iso_code', 
                animation_frame="date",
                color='data',
                scope="europe",
                color_continuous_scale=map_color_scale,
                labels={'data':data_type},
                hover_name="country"
            )
            delay = st.sidebar.number_input("Animation Delay", min_value=5, max_value=1000, value=5)
            fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = delay
            
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("## Areas with 0 " + data_type + " as of Today")
            for i in zero_data:
                st.markdown("* " + i)
        elif not df_anim.empty and not df_no_anim.empty:
            fig = px.choropleth(
                df_no_anim, 
                locations='iso_code', 
                color="data",
                color_continuous_scale=map_color_scale,
                scope="europe",
                labels={'data':data_type},
                hover_name="country",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("## Areas with 0 " + data_type + " as of Today")
            for i in zero_data:
                st.markdown("* " + i)        
        else:
            st.warning("No data for countries available with selected data type")
                  
    elif map_type == "World":
        countries = [i for i in  world_node.get_children()]

        anim_data = {}
        no_anim_data = {}
        zero_data = []
        j = 0
        for i, country in enumerate(countries):
            node_data = getattr(country, data_options.get(data_type))
            if callable(node_data):
                node_data = node_data()
            if node_data and country.iso3:
                d = {
                    "iso_code":country.iso3,
                    "data":node_data[-1] if node_data[-1] is not None else 0,
                    "country":country.node_name
                }
                no_anim_data.update({j:d})
                for k, datapoint in enumerate(node_data):
                    d = {
                        "iso_code":country.iso3,
                        "data":datapoint if datapoint is not None else 0,
                        "country":country.node_name,
                        "date":str(dates[k])
                    }

                    anim_data.update({j:d})
                    j += 1

                if node_data[-1] == 0 or (node_data and node_data[-1] is None):
                    zero_data.append(country.node_name)
                
        df_anim = pd.DataFrame.from_dict(anim_data, orient='index')
        df_no_anim = pd.DataFrame.from_dict(no_anim_data, orient='index')
        
        if not df_anim.empty and not df_no_anim.empty and animations:
            fig = px.choropleth(
                df_anim, 
                locations='iso_code', 
                animation_frame="date",
                color='data',
                color_continuous_scale=map_color_scale,
                labels={'data':data_type},
                hover_name="country"
            )
            delay = st.sidebar.number_input("Animation Delay", min_value=5, max_value=1000, value=5)
            fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = delay
            
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("## Areas with 0 " + data_type + " as of Today")
            for i in zero_data:
                st.markdown("* " + i)
        elif not df_anim.empty and not df_no_anim.empty:
            fig = px.choropleth(
                df_no_anim, 
                locations='iso_code', 
                color="data",
                color_continuous_scale=map_color_scale,
                labels={'data':data_type},
                hover_name="country",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("## Areas with 0 " + data_type + " as of Today")
            for i in zero_data:
                st.markdown("* " + i)  
        else:
            st.warning("No data for counties available with selected data type")
                                                
 
elif mode == "Parsed Data - Time Series":
    data_type = st.sidebar.selectbox("Data Table Entry", sorted(data_options.keys()))
    plotted_areas = get_regions(world_node)
    
    columns = {}
    for node in plotted_areas:
        data = getattr(node, data_options.get(data_type))
        if callable(data):
            data = data()
            
        if data:
            columns.update({node.node_name:data})
        else:
            st.warning("No " + data_type + " data was found for " + node.node_name)

    df = pd.DataFrame(columns, index=dates)
    st.dataframe(df)

    
    
    
elif mode == "Parsed Data - Daily Reports":
    plotted_areas = get_regions(world_node)
    
    for node in plotted_areas:
        columns = {}
        for data_name, data_attribute in data_options.items():
            data = getattr(node, data_attribute)
            if callable(data):
                data = data()
            if data:
                columns.update({data_name:data})
            else:
                st.warning("No " + data_name + " data was found for " + node.node_name)
        
        df = pd.DataFrame(columns, index=dates)
        st.write("Dataframe for ", get_label(node))
        st.dataframe(df)




elif mode == "File Data":
    # make directories for data to be held if they do not already exist
    if not os.path.isdir(os.path.join(os.path.dirname("."), "data")):
        os.mkdir(os.path.join(os.path.dirname("."), "data"))
    
    # check if most recent data is downloaded
    all_subdirs = []
    for d in os.listdir('./data'):
        bd = os.path.join('./data', d)
        if os.path.isdir(bd):
            all_subdirs.append(bd)
            
    if all_subdirs:
        latest_subdir = max(all_subdirs, key=os.path.getmtime)
    else:
        latest_subdir = "."
            
    if str(datetime.date.today()) not in latest_subdir:
        if st.button("Download Data"):  # download data if it is not present
            with st.spinner("Retreiving Latest Data, Please Wait..."):
                data_grabber.retrieve_data()
                
    else:
        st.success("Current Data is already saved to disk")
        if st.button("Download Data Again"):  # download data if it is not present
            with st.spinner("Retreiving Latest Data, Please Wait..."):
                data_grabber.retrieve_data()
            