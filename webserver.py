#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 22:06:37 2020

@author: aiden
"""
import copy
import numpy as np
import streamlit as st

import covid19_data
import plot_handler


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
                "smooth":False,
                "window_length":5,
                "polyorder":3,
                "iters":2,
                "start_threshold":3.0,
                "threshold_stepdown":0.25
            }]
            
    def get_settings(self, i):
        if 0 <= i < len(self.data):
            return self.data[i]
        else:
            # st.warning("IndexError Avoided: Smoothing options at i=" + str(i) + " does not exist")
            return {
                "smooth":False,
                "window_length":5,
                "polyorder":3,
                "iters":2,
                "start_threshold":3.0,
                "threshold_stepdown":0.25
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
def parse_data(file_urls, folders):
    with st.spinner("Parsing Data, Please Wait..."):
        data = covid19_data.Covid19_Data()
        for file in file_urls:
            data.read_time_series_cases_data(file)
        for folder in folders:
            data.read_us_daily_reports_data(folder)
        
    return data

             
@st.cache(allow_output_mutation=True)
def get_graph_session_info():
    return GraphSessionInfo.get_instance()

@st.cache(allow_output_mutation=True)           
def get_smoothing_options_session_info():
    return SmoothingOptionsInfo.get_instance()

            
def get_configuration(uid, areas, previous={}):
    default = int(not(previous.get("smooth", False)))
    # smooth = areas[0].radio("Smooth Graph", ['Yes', 'No'], 1, key=str(uid) + "1")
    radio = areas[0].radio("Smooth Graph", ['Yes', 'No'], default, key=str(uid) + "1")
    if radio.upper() == "YES":
        # test functionality of configuration screen
        window_len = areas[1].slider("Filter Window Length", min_value=1, max_value=15, step=2, value=previous.get("window_length", 5), key=str(uid) + "1")
        poly_order = areas[2].slider("Filter Polynomial Degree", min_value=0, max_value=15, step=1, value=previous.get("polyorder", 3), key=str(uid) + "2")
        iters = areas[3].slider("Itrerations", min_value=0, max_value=30, step=1, value=previous.get("iters", 2), key=str(uid) + "3")
        outlier_threshold = areas[4].slider("Outlier Threshold", min_value=0.0, max_value=5.0, step=0.1, value=previous.get("start_threshold", 3.0), key=str(uid) + "4")
        threshold_stepdown = areas[5].slider("Outlier Threshold Stepdown", min_value=-1.0, max_value=1.0, step=.05, value=previous.get("threshold_stepdown", 0.25), key=str(uid) + "5")
        data = {
            "smooth":True,
            "window_length":window_len,
            "polyorder":poly_order,
            "iters":iters,
            "start_threshold":outlier_threshold,
            "threshold_stepdown":threshold_stepdown
        }
    else:
        data = {
            "smooth":False,
            "window_length":previous.get("window_length", 5),
            "polyorder":previous.get("polyorder", 3),
            "iters":previous.get("iters", 2),
            "start_threshold":previous.get("start_threshold", 3.0),
            "threshold_stepdown":previous.get("threshold_stepdown", 0.25)
        }
        
    return data


def get_label(node):
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
    time_series_url + "/time_series_covid19_deaths_global.csv",
    time_series_url + "/time_series_covid19_deaths_US.csv",
    ]
folders = [
    "csse_covid_19_data/csse_covid_19_daily_reports_us"
    ]
covid_data = copy.deepcopy(parse_data(files, folders))
world_node = covid_data.time_series_data_tree



mode = st.sidebar.selectbox(
    "Mode",
    [
        "Line Chart",
        "Data"
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
    "Active Cases":"active_cases_time_series_data",
    "Recovered Cases":"recovered_cases_time_series_data",
    "Recovery Rate":"get_recovery_rate",
    "Confirmed Cases to People Tested Ratio":"get_ratio_confirmed_cases_to_people_tested"
    }

graph_types1 = st.sidebar.multiselect("Axis 1", sorted(data_options.keys()), default=["Confirmed Cases"])
graph_types2 = st.sidebar.multiselect("Axis 2", sorted(data_options.keys()), default=["Confirmed Cases"])



# find what areas to graph
regions = st.sidebar.multiselect("Select Regions", sorted([i.node_name for i in world_node.get_children()]), default=["US"])
regions_nodes = [world_node.get_child_node(name) for name in regions]
plotted_areas = []
for region in regions_nodes:
    if region.get_children():
        sub_regions = st.sidebar.multiselect(
                ("State/Province in " + region.node_name), 
                sorted([i.node_name for i in region.get_children()])
            )
        if st.sidebar.checkbox("Plot Data for " + region.node_name, value=True):
            plotted_areas.append(region)
    
    
        sub_regions_nodes = [region.get_child_node(name) for name in sorted(sub_regions)]
        for sub_region in sub_regions_nodes:
            if sub_region.get_children():
                counties = st.sidebar.multiselect(
                    ("Counties in " + sub_region.node_name), 
                    sorted([i.node_name for i in sub_region.get_children()])
                )
                plotted_areas.extend([sub_region.get_child_node(i) for i in counties])
                
                if st.sidebar.checkbox("Plot Data for " + sub_region.node_name, value=True):
                    plotted_areas.append(sub_region)
            else:
                plotted_areas.append(sub_region)
    else:
        plotted_areas.append(region)
        
        
# add original datasets to the plot handler     
dates = covid_data.time_series_dates 
int_to_dates_lookup, dates_to_int_lookup = covid_data.create_lookup_tables(min(dates), max(dates))
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
    # handler = create_data_handler(int_to_dates_lookup, plotted_areas, x, graph, data_options.get(graph))
    handler = get_graph_session_info().get_data_handler(graph, data_options.get(graph))
    plot_handlers_axis1.append(handler)
    y_axis1_titles.append(graph)
    if i > 0:
        add_axis_title_to_legend = True
        
for i, graph in enumerate(graph_types2):
    # handler = create_data_handler(int_to_dates_lookup, plotted_areas, x, graph, data_options.get(graph))
    handler = get_graph_session_info().get_data_handler(graph, data_options.get(graph))
    plot_handlers_axis2.append(handler)
    y_axis2_titles.append(graph)
    if i > 0:
        add_axis_title_to_legend = True

plots_data = [plot_handlers_axis1, plot_handlers_axis2]
y_axis_titles = [y_axis1_titles, y_axis2_titles]

if len(plots_data) > 1:
    add_axis_title_to_legend = True
    

    
    
if st.button("Refresh"):
    st.caching.clear_cache()


# get configuration for each graph
areas = []
areas.append(st.empty())


smooth_areas = []  # area for smoothing options
for j in range(6):
    smooth_areas.append(st.empty())
data = get_configuration(0, smooth_areas, get_smoothing_options_session_info().get_settings(0)) 
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
    new_der_btn.empty()
    

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
    
    
    data = get_configuration(i + 1, partition[2], get_smoothing_options_session_info().get_settings(i + 1))
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
# print(len(areas), len(plot_objects), plots_data[0][0].num_plots, get_graph_session_info().num_derivatives)
   
for area, plt in zip(areas, plot_objects):
    area.plotly_chart(plt, use_container_width=True)
    