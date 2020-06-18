#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 22:06:37 2020

@author: aiden
"""

import streamlit as st
import copy

import covid19_data
import plot_handler

@st.cache(hash_funcs={covid19_data.Covid19_Tree_Node: lambda _: None}, allow_output_mutation=True)
def parse_data(file_name, folder_name):
    st.write("Cache miss: expensive_computation")
    data = covid19_data.Covid19_Data()
    data.read_time_series_cases_data("./data/2020-05-11/CSSEGISandData-COVID-19-5184bec/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv")
    data.read_us_daily_reports_data("./data/2020-05-11/CSSEGISandData-COVID-19-5184bec/csse_covid_19_data/csse_covid_19_daily_reports_us")
    
    return data

@st.cache(allow_output_mutation=True)   
def create_plot_handler(lookup, x_label, y_label, x, y, labels):
    return plot_handler.PlotHandler(lookup, x_label, y_label, x, y, labels)


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


# get the data to parse
file = "./data/2020-05-11/CSSEGISandData-COVID-19-5184bec/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_US.csv"
folder = "./data/2020-05-11/CSSEGISandData-COVID-19-5184bec/csse_covid_19_data/csse_covid_19_daily_reports_us"
covid_data = copy.deepcopy(parse_data(file, folder))
world_node = covid_data.time_series_data_tree


# select the type of graph
graph_type = st.sidebar.selectbox(
    "Graph Type", 
    ["Confirmed Cases", "Deaths", "Testing", "Incident Plot"]
    )


# find what areas to graph
regions = st.sidebar.multiselect("Select Regions", sorted([i.node_name for i in world_node.get_children()]))
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
for _ in range(len(plotted_areas)):
    x.append([dates_to_int_lookup.get(date.strftime("%m-%d-%Y")) for date in dates])

datasets = []
labels = []
if graph_type == "Confirmed Cases":
    for node in plotted_areas:
        if node.confirmed_cases_time_series_data:
            datasets.append(node.confirmed_cases_time_series_data)
            labels.append(get_label(node))
        else:
            st.warning("No Confirmed Cases data was found for " + node.node_name)
    plots = create_plot_handler(int_to_dates_lookup, "Date", "Confirmed Cases", x, datasets, labels)
elif graph_type == "Deaths":
    for node in plotted_areas:
        if node.deaths_time_series_data:
            datasets.append(node.deaths_time_series_data)
            labels.append(get_label(node))
        else:
            st.warning("No Deaths data was found for " + node.node_name)
    plots = create_plot_handler(int_to_dates_lookup, "Date", "Deaths", x, datasets, labels)
elif graph_type == "Testing":
    for node in plotted_areas:
        if node.people_tested_time_series_data:
            datasets.append(node.people_tested_time_series_data)
            labels.append(get_label(node))
        else:
            st.warning("No Testing data was found for " + node.node_name)
    plots = create_plot_handler(int_to_dates_lookup, "Date", "Tests", x, datasets, labels)
elif graph_type == "Incident Plot":
    for node in plotted_areas:
        if node.incident_rate_time_series_data:
            datasets.append(node.incident_rate_time_series_data)
            labels.append(get_label(node))
        else:
            st.warning("No Incident Rate data was found for " + node.node_name)
    plots = create_plot_handler(int_to_dates_lookup, "Date", "Incident Rate", x, datasets, labels)

st.button("Refresh")


# get configuration for each graph
areas = []
areas.append(st.empty())

# configuration for first plot
data = get_configuration(0) 
# print(data)
plots.update_configuration(0, data)
plots.update_plot_data(0)
if st.button("New Derivative"):
    plots.new_derivative()


# configuration for derivative plots -- this also includes option to remove plot
for i in range(1, plots.num_plots):
    areas.append(st.empty())

    a = st.empty()
    if a.button("Remove Derivative", key="5" + str(i)):
        plots.remove_derivative_dataset(i)
        a.empty()
    
    else:
        data = get_configuration(i)
            
        # print(data)
        plots.update_configuration(i, data)
        plots.update_plot_data(i)
        
        if st.button("New Derivative", key="6" + str(i)):
            plots.new_derivative()


# fill in graphs with configured areas
for area, i in zip(areas, range(plots.num_plots)):
    plt = plots.update_plot(i)
    area.plotly_chart(plt, use_container_width=True)
    
