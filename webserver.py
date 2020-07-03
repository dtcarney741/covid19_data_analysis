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
def create_plot_handler(lookup, x, y, labels):
    return plot_handler.DataHandler(lookup, x, y, labels)


def get_configuration(uid):
    smooth = st.radio("Smooth Graph", ['Yes', 'No'], 1, key="1" + str(uid))
    if smooth.upper() == "YES":
        # test functionality of configuration screen
        window_len = st.slider("Filter Window Length", min_value=1, max_value=15, step=2, value=5, key="2" + str(uid))
        poly_order = st.slider("Filter Polynomial Degree", min_value=0, max_value=15, step=1, value=3, key="3" + str(uid))
        iters = st.slider("Itrerations", min_value=0, max_value=30, step=1, value=2, key="1" + str(uid))
        outlier_threshold = st.slider("Outlier Threshold", min_value=0.0, max_value=5.0, step=0.1, value=3.0, key="4" + str(uid))
        threshold_stepdown = st.slider("Outlier Threshold Stepdown", min_value=-1.0, max_value=1.0, step=.05, value=0.25, key="5" + str(uid))
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
            "window_length":5,
            "polyorder":5,
            "iters":2,
            "start_threshold":3,
            "threshold_stepdown":0.25
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


# select the type of graph
graph_type = st.sidebar.selectbox(
    "Graph Type", 
    sorted([
        "Confirmed Cases", 
        "Deaths", 
        "Daily New Confirmed Cases",
        "Daily New Deaths",
        "Testing", 
        "Incident Plot",
        "Active Cases",
        "Recovered Cases",
        "Death Rate",
        "Recovery Rate",
        "Confirmed Cases to People Tested Ratio",
        "Confirmed Cases and Deaths 1 axis",
        "Confirmed Cases and Deaths 2 axes",
    ]), 
    1
)


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

plots_data = None
y_axis_titles = []
x_axis_title = ""
for _ in range(len(plotted_areas)):
    x.append([dates_to_int_lookup.get(date.strftime("%m-%d-%Y")) for date in dates])

datasets = []
labels = []

add_axis_title_to_legend = False
if graph_type == "Confirmed Cases":
    for node in plotted_areas:
        if node.confirmed_cases_time_series_data:
            datasets.append(node.confirmed_cases_time_series_data)
            labels.append(get_label(node))
        else:
            st.warning("No Confirmed Cases data was found for " + node.node_name)
    for i, dataset in enumerate(datasets):
        for j, data_point in enumerate(dataset):
            if data_point is None:
                datasets[i][j] = np.nan
    x_axis_title = "Date"
    y_axis_titles.append(["Confirmed Cases"])
    plots_data = [[create_plot_handler(int_to_dates_lookup, x, datasets, labels)]]

elif graph_type == "Deaths":
    for node in plotted_areas:
        if node.deaths_time_series_data:
            datasets.append(node.deaths_time_series_data)
            labels.append(get_label(node))
        else:
            st.warning("No Deaths data was found for " + node.node_name)
    for i, dataset in enumerate(datasets):
        for j, data_point in enumerate(dataset):
            if data_point is None:
                datasets[i][j] = np.nan
    x_axis_title = "Date"
    y_axis_titles.append(["Deaths"])
    plots_data = [[create_plot_handler(int_to_dates_lookup, x, datasets, labels)]]

elif graph_type == "Daily New Confirmed Cases":
    for node in plotted_areas:
        if node.get_daily_new_cases():
            datasets.append(node.get_daily_new_cases())
            labels.append(get_label(node))
        else:
            st.warning("No Daily New Confirmed Cases data was found for " + node.node_name)
    for i, dataset in enumerate(datasets):
        for j, data_point in enumerate(dataset):
            if data_point is None:
                datasets[i][j] = np.nan
    x_axis_title = "Date"
    y_axis_titles.append(["Daily New Confirmed Cases"])
    plots_data = [[create_plot_handler(int_to_dates_lookup, x, datasets, labels)]]

elif graph_type == "Daily New Deaths":
    for node in plotted_areas:
        if node.get_daily_new_deaths():
            datasets.append(node.get_daily_new_deaths())
            labels.append(get_label(node))
        else:
            st.warning("No Daily New Deaths data was found for " + node.node_name)
    for i, dataset in enumerate(datasets):
        for j, data_point in enumerate(dataset):
            if data_point is None:
                datasets[i][j] = np.nan
    x_axis_title = "Date"
    y_axis_titles.append(["Daily New Deaths"])
    plots_data = [[create_plot_handler(int_to_dates_lookup, x, datasets, labels)]]

elif graph_type == "Testing":
    for node in plotted_areas:
        if node.people_tested_time_series_data:
            datasets.append(node.people_tested_time_series_data)
            labels.append(get_label(node))
        else:
            st.warning("No Testing data was found for " + node.node_name)
    for i, dataset in enumerate(datasets):
        for j, data_point in enumerate(dataset):
            if data_point is None:
                datasets[i][j] = np.nan
    x_axis_title = "Date"
    y_axis_titles.append(["Tests"])
    plots_data = [[create_plot_handler(int_to_dates_lookup, x, datasets, labels)]]

elif graph_type == "Incident Plot":
    for node in plotted_areas:
        if node.incident_rate_time_series_data:
            datasets.append(node.incident_rate_time_series_data)
            labels.append(get_label(node))
        else:
            st.warning("No Incident Rate data was found for " + node.node_name)
    for i, dataset in enumerate(datasets):
        for j, data_point in enumerate(dataset):
            if data_point is None:
                datasets[i][j] = np.nan
    x_axis_title = "Date"
    y_axis_titles.append(["Confirmed Cases per 100k Population"])
    plots_data = [[create_plot_handler(int_to_dates_lookup, x, datasets, labels)]]

elif graph_type == "Active Cases":
    for node in plotted_areas:
        if node.incident_rate_time_series_data:
            datasets.append(node.active_cases_time_series_data)
            labels.append(get_label(node))
        else:
            st.warning("No Active Cases data was found for " + node.node_name)
    for i, dataset in enumerate(datasets):
        for j, data_point in enumerate(dataset):
            if data_point is None:
                datasets[i][j] = np.nan
    x_axis_title = "Date"
    y_axis_titles.append(["Active Cases"])
    plots_data = [[create_plot_handler(int_to_dates_lookup, x, datasets, labels)]]

elif graph_type == "Recovered Cases":
    for node in plotted_areas:
        if node.incident_rate_time_series_data:
            datasets.append(node.recovered_cases_time_series_data)
            labels.append(get_label(node))
        else:
            st.warning("No Recovered Cases data was found for " + node.node_name)
    for i, dataset in enumerate(datasets):
        for j, data_point in enumerate(dataset):
            if data_point is None:
                datasets[i][j] = np.nan
    x_axis_title = "Date"
    y_axis_titles.append(["Recovered Cases"])
    plots_data = [[create_plot_handler(int_to_dates_lookup, x, datasets, labels)]]

elif graph_type == "Death Rate":
    for node in plotted_areas:
        if node.deaths_time_series_data and node.confirmed_cases_time_series_data:
            ratio = []
            for deaths, confirmed in zip(node.deaths_time_series_data, node.confirmed_cases_time_series_data):
                try:
                    ratio.append(deaths / confirmed)
                except TypeError:
                    ratio.append(np.nan)
                except ZeroDivisionError:
                    ratio.append(np.nan)
                
            datasets.append(ratio)
            labels.append(get_label(node))
        else:
            st.warning("Death rate could not be calculated for " + node.node_name)
    for i, dataset in enumerate(datasets):
        for j, data_point in enumerate(dataset):
            if data_point is None:
                datasets[i][j] = np.nan
    x_axis_title = "Date"
    y_axis_titles.append(["Death Rate"])
    plots_data = [[create_plot_handler(int_to_dates_lookup, x, datasets, labels)]]
    
elif graph_type == "Recovery Rate":
    for node in plotted_areas:
        if node.get_recovery_rate():
            datasets.append(node.get_recovery_rate())
            labels.append(get_label(node))
        else:
            st.warning("No Recovery Rate data was found for " + node.node_name)
    for i, dataset in enumerate(datasets):
        for j, data_point in enumerate(dataset):
            if data_point is None:
                datasets[i][j] = np.nan
    x_axis_title = "Date"
    y_axis_titles.append(["Recovery Rate"])
    plots_data = [[create_plot_handler(int_to_dates_lookup, x, datasets, labels)]]

elif graph_type == "Confirmed Cases to People Tested Ratio":
    for node in plotted_areas:
        if node.get_ratio_confirmed_cases_to_people_tested():
            datasets.append(node.get_ratio_confirmed_cases_to_people_tested())
            labels.append(get_label(node))
        else:
            st.warning("No Confirmed Cases to People Tested Ratio data was found for " + node.node_name)
    for i, dataset in enumerate(datasets):
        for j, data_point in enumerate(dataset):
            if data_point is None:
                datasets[i][j] = np.nan
    x_axis_title = "Date"
    y_axis_titles.append(["Cases to Tests Ratio"])
    plots_data = [[create_plot_handler(int_to_dates_lookup, x, datasets, labels)]]

elif graph_type == "Confirmed Cases and Deaths 1 axis":
    dataset1 = []
    dataset2 = []
    for node in plotted_areas:
        if node.deaths_time_series_data and node.confirmed_cases_time_series_data:
            dataset1.append(node.confirmed_cases_time_series_data)
            dataset2.append(node.deaths_time_series_data)
            labels.append(get_label(node))
        else:
            st.warning("Data could not be found for " + node.node_name)

    for i, dataset in enumerate(datasets):
        for j, data_point in enumerate(dataset):
            if data_point is None:
                datasets[i][j] = np.nan
    
    x_axis_title = "Date"
    y_axis_titles.append(["Confirmed Cases", "Deaths"])
    
    add_axis_title_to_legend = True
    
    plots_data = [
        [
            create_plot_handler(int_to_dates_lookup, x, dataset1, labels),
            create_plot_handler(int_to_dates_lookup, x, dataset2, labels)
        ]
    ]
    
elif graph_type == "Confirmed Cases and Deaths 2 axes":
    dataset1 = []
    dataset2 = []
    for node in plotted_areas:
        if node.deaths_time_series_data and node.confirmed_cases_time_series_data:
            dataset1.append(node.confirmed_cases_time_series_data)
            dataset2.append(node.deaths_time_series_data)
            labels.append(get_label(node))
        else:
            st.warning("Data could not be found for " + node.node_name)

    for i, dataset in enumerate(datasets):
        for j, data_point in enumerate(dataset):
            if data_point is None:
                datasets[i][j] = np.nan
    
    x_axis_title = "Date"
    y_axis_titles.append(["Confirmed Cases"])
    y_axis_titles.append(["Deaths"])
    
    add_axis_title_to_legend = True
    
    plots_data = [
        [create_plot_handler(int_to_dates_lookup, x, dataset1, labels)],
        [create_plot_handler(int_to_dates_lookup, x, dataset2, labels)]
    ]
        
    
    
if st.button("Refresh"):
    st.caching.clear_cache()


# get configuration for each graph
areas = []
areas.append(st.empty())

new_derivative = False
data = get_configuration(0) 
if st.button("New Derivative"):
    new_derivative = True
for dataset in plots_data:
    for data_entry in dataset:
        # configuration for first plot
        data_entry.update_configuration(0, data)
        data_entry.update_plot_data(0)
        if new_derivative == True:
            data_entry.new_derivative()


# configuration for derivative plots -- this also includes option to remove plot
for i in range(1, plots_data[0][0].num_plots):
    areas.append(st.empty())

    a = st.empty()
    if a.button("Remove Derivative", key="5" + str(i)):
        for dataset in plots_data:
            for data_entry in dataset:
                data_entry.remove_derivative_dataset(i)
        a.empty()
    
    else:
        data = get_configuration(i)
            
        for dataset in plots_data:
            for data_entry in dataset:
                data_entry.update_configuration(i, data)
                data_entry.update_plot_data(i)
        
        if st.button("New Derivative", key="6" + str(i)):
            for dataset in plots_data:
                dataset.new_derivative()


# fill in graphs with configured areas
formatted_data = {}
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

for area, plt, i in zip(areas, plot_objects, range(plots_data[0][0].num_plots)):
    area.plotly_chart(plt, use_container_width=True)
    
