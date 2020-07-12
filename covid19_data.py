import csv
import datetime
import os
import requests

import github_directory_tree
import matplotlib_gui

class Covid19_Tree_Node(object):
    def __init__(self, name):
        """Description: Initialize a tree node
        Inputs: None
        Outputs: Initializes data structures
        """
        self.node_name = name
        self.child_nodes = {}
        self.confirmed_cases_time_series_data = []
        self.deaths_time_series_data = []
        self.people_tested_time_series_data = []
        self.incident_rate_time_series_data = []
        self.active_cases_time_series_data = []
        self.recovered_cases_time_series_data = []
        self.population = None
        self.hospitalizations_time_series_data = []
        self.latitude = None
        self.longitude = None
        self.parent = None
        
    
    def add_child(self, tree_node):
        """Description: Add a tree node as a child to this tree
        Inputs: tree_node - a reference to an object of type Covid19_Tree_Node
        Outputs: 
            If the tree_node is not already a child of this tree:
                Adds the node as a child
                Sets the node's parent value to point to this tree node
                Returns True
            Else:
                Returns False
        """
        if self.get_child_node(tree_node.node_name) == None:
            self.child_nodes[tree_node.node_name] = tree_node
            tree_node.parent = self
            return True
        else:
            return False

    def get_child_node(self, name):
        """Description: get a reference to a node object for a child node
        Inputs: name - The name of the child node to return a reference for
        Outputs: returns Covid19_Tree_Node if the child exists or None if not
        """
        if name in self.child_nodes:
            return self.child_nodes[name]
        else:
            return None
            
    def get_children(self):
        """Description: get a list of references to all the children nodes
        Inputs: None
        Outputs: returns list of references to child nodes
        """
        children_list = []
        for child in self.child_nodes:
            children_list.append(self.child_nodes[child])
        return children_list

    def initialize_confirmed_cases(self,length):
        """Description: Initialize the confirmed cases data array
        Inputs: length - number of data values to initailize
        Outputs: self.confirmed_cases_time_series_data[0:length-1] is initialized with None
        """
        self.confirmed_cases_time_series_data = []
        for i in range(0,length):
            self.confirmed_cases_time_series_data.append(None)

    def initialize_deaths(self,length):
        """Description: Initialize the deaths data array
        Inputs: length - number of data values to initailize
        Outputs: self.deaths_time_series_data[0:length-1] is initialized with None
        """
        self.deaths_time_series_data = []
        for i in range(0,length):
            self.deaths_time_series_data.append(None)

    def initialize_people_tested(self,length):
        """Description: Initialize the people tested data array
        Inputs: length - number of data values to initailize
        Outputs: self.people_tested_time_series_data[0:length-1] is initialized with None
        """
        self.people_tested_time_series_data = []
        for i in range(0,length):
            self.people_tested_time_series_data.append(None)

    def initialize_incident_rate(self,length):
        """Description: Initialize the incident rate data array
        Inputs: length - number of data values to initailize
        Outputs: self.incident_rate_time_series_data[0:length-1] is initialized with None
        """
        self.incident_rate_time_series_data = []
        for i in range(0,length):
            self.incident_rate_time_series_data.append(None)

    def initialize_active_cases(self,length):
        """Description: Initialize the active cases data array
        Inputs: length - number of data values to initailize
        Outputs: self.incident_rate_time_series_data[0:length-1] is initialized with None
        """
        self.active_cases_time_series_data = []
        for i in range(0,length):
            self.active_cases_time_series_data.append(None)

    def initialize_recovered_cases(self,length):
        """Description: Initialize the recovered cases data array
        Inputs: length - number of data values to initailize
        Outputs: self.incident_rate_time_series_data[0:length-1] is initialized with None
        """
        self.recovered_cases_time_series_data = []
        for i in range(0,length):
            self.recovered_cases_time_series_data.append(None)

    def initialize_hospitalizations(self,length):
        """Description: Initialize the recovered cases data array
        Inputs: length - number of data values to initailize
        Outputs: self.hospitalizations_time_series_data[0:length-1] is initialized with None
        """
        self.hospitalizations_time_series_data = []
        for i in range(0,length):
            self.hospitalizations_time_series_data.append(None)

    def get_daily_new_cases(self):
        """Description: Calculate and return list of derived data
        Inputs: None
        Outputs: daily_new_cases[] where each element is defined as: self.confirmed_cases_time_series_data[i] - self.confirmed_cases_time_series_data[i-1]
                    and daily_new_cases[0] = None
        """
        daily_new_cases = []
        daily_new_cases.append(None)
        for i in range(1,len(self.confirmed_cases_time_series_data)):
            if self.confirmed_cases_time_series_data[i] != None and self.confirmed_cases_time_series_data[i-1] != None:
                val = self.confirmed_cases_time_series_data[i] - self.confirmed_cases_time_series_data[i-1]
            else:
                val = None
            daily_new_cases.append(val)
        return daily_new_cases

    def get_daily_new_deaths(self):
        """Description: Calculate and return list of derived data
        Inputs: None
        Outputs: daily_new_deaths[] where each element is defined as: self.deaths_time_series_data[i] - self.deaths_time_series_data[i-1]
                    and daily_new_deaths[0] = None
        """
        daily_new_deaths = []
        daily_new_deaths.append(None)
        for i in range(1,len(self.deaths_time_series_data)):
            if self.deaths_time_series_data[i] != None and self.deaths_time_series_data[i-1] != None:
                val = self.deaths_time_series_data[i] - self.deaths_time_series_data[i-1]
            else:
                val = None
            daily_new_deaths.append(val)
        return daily_new_deaths

    def get_daily_new_people_tested(self):
        """Description: Calculate and return list of derived data
        Inputs: None
        Outputs: daily_new_people_tested[] where each element is defined as: self.people_tested_time_series_data[i] - self.people_tested_time_series_data[i-1]
                    and daily_new_people_tested[0] = None
        """
        daily_new_people_tested = []
        daily_new_people_tested.append(None)
        for i in range(1,len(self.people_tested_time_series_data)):
            if self.people_tested_time_series_data[i] != None and self.people_tested_time_series_data[i-1] != None:
                val = self.people_tested_time_series_data[i] - self.people_tested_time_series_data[i-1]
            else:
                val = None
            daily_new_people_tested.append(val)
        return daily_new_people_tested
    
    def get_recovery_rate(self):
        """Description: Calculate and return list of derived data
        Inputs: None
        Outputs: recovery_rate[] where each element is defined as: self.recovered_cases_time_series_data[i] / self.confirmed_cases_time_series_data[i]
        """
        recovery_rate = []
        for i in range(0, len(self.confirmed_cases_time_series_data)):
            if self.recovered_cases_time_series_data[i] != None and self.confirmed_cases_time_series_data[i] != None and self.confirmed_cases_time_series_data[i] != 0:
                val = self.recovered_cases_time_series_data[i] / self.confirmed_cases_time_series_data[i]
            else:
                val = None
            recovery_rate.append(val)
        return recovery_rate

    def get_ratio_confirmed_cases_to_people_tested(self):
        """Description: Calculate and return list of derived data
        Inputs: None
        Outputs: ratio[] where each element is defined as: self.confirmed_cases_time_series_data[i] / self.people_tested_time_series_data[i]
        """
        ratio = []
        for i in range(0, len(self.people_tested_time_series_data)):
            if self.confirmed_cases_time_series_data[i] != None and self.people_tested_time_series_data[i] != None and self.people_tested_time_series_data[i] != 0:
                val = self.confirmed_cases_time_series_data[i] / self.people_tested_time_series_data[i]
            else:
                val = None
            ratio.append(val)
        return ratio

    def get_daily_ratio_confirmed_cases_to_people_tested(self):
        """Description: Calculate and return list of derived data
        Inputs: None
        Outputs: ratio[] where each element is defined as: daily_confirmed[i] / daily_tested[i]
            daily_confirmed = self.confirmed_cases_time_series_data[i] - self.confirmed_cases_time_series_data[i-1]
            daily_tested = self.people_tested_time_series_data[i] - self.people_tested_time_series_data[i-1]
        """
        cases = self.get_daily_new_cases()
        tested = self.get_daily_new_people_tested()
        ratio = []
        for i in range(0, len(cases)):
            if cases[i] and tested[i] and tested[i] != 0:
                ratio.append(cases[i]/tested[i])
            else:
                ratio.append(None)
                
        return ratio
    
    def get_case_fatality_rate(self):
        fatality_rate = []
        for cases, deaths in zip(self.confirmed_cases_time_series_data, self.deaths_time_series_data):
            try:
                fatality_rate.append(deaths/cases)
            except ZeroDivisionError:
                fatality_rate.append(0)
            except TypeError:
                fatality_rate.append(None)
                
        return fatality_rate
                
    
    
    
class Covid19_Data(object):  
    
    def __init__(self):
        """Description: Reads a DSM spreadsheet tab into a DSM data structure
        Inputs: None
        Outputs: Initializes data structures
        """
        self.github_tree = github_directory_tree.GithubDirectoryTree("CSSEGISandData", "Covid-19")
        self.time_series_dates = []
        self.time_series_data_tree = Covid19_Tree_Node("World")
        # initialize header to cell map values in time series data file (-1 for unknown)"""
        self.__time_series_field_locations = {
            "HEADER_ROW": -1,
            "COUNTRY_NAME_COL": -1,
            "STATE_NAME_COL": -1,
            "COUNTY_NAME_COL": -1,
            "FIRST_DATE_COL": -1,
            "LAST_DATE_COL": -1
            }
        self.__us_data_field_locations = {
            "HEADER_ROW": -1,
            "COUNTRY_NAME_COL": -1,
            "STATE_NAME_COL": -1,
            "LATITUDE_COL": -1,
            "LONGITUDE_COL": -1,
            "CONFIRMED_CASES_COL": -1,
            "DEATHS_COL": -1,
            "PEOPLE_TESTED_COL": -1,
            "INCIDENT_RATE_COL": -1,
            "ACTIVE_CASES_COL": -1,
            "RECOVERED_CASES_COL": -1,
            "PEOPLE_HOSPITALIZED_COL": -1
            }
        self.__world_data_field_locations = {
                "HEADER_ROW": -1,
                "COUNTRY_NAME_COL": -1,
                "STATE_NAME_COL": -1,
                "COUNTY_NAME_COL": -1,
                "LATITUDE_COL": -1,
                "LONGITUDE_COL": -1,
                "CONFIRMED_CASES_COL": -1,
                "DEATHS_COL": -1,
                "INCIDENT_RATE_COL": -1,
                "ACTIVE_CASES_COL": -1,
                "RECOVERED_CASES_COL": -1
                }

        # list of countries to ignore data for from the world daily reports (already captured in other data files or is suspect)
        self.__world_daily_reports_exclusions_list = [
                "US"
                ]

        # list of countries or states to Not aggregate data up to the parent in world time series files (these have territories listed separately with the country
        # as a parent and their values do not add up to the total number for the country)
        self.__world_country_state_aggregration_exclusions_list = [
                "United Kingdom",
                "Netherlands",
                "France",
                "Denmark"
                ]
        
    def __set_node_data_values(self, node, data_types, data_values, index, aggregate_to_parent, absolute):
        """Description: Sets the specified data values in the data arrays for a tree node at the specified index.
        Inputs:
            node - the tree node whose data values are to be updated
            data_types - list containing which data types are to be updated.  Possible values are:
                            'DEATHS', 'CONFIRMED', 'TESTED', 'INCIDENT', 'ACTIVE', 'RECOVERED', 'HOSPITALIZED'
            data_values - list with the value to be set for the corresponding data type (list correspondance is 1 to 1 with data_types)
            index - the list index into which the data value is to be placed
            aggregate_to_parent - True or False to indicate whether the data should be summed into the parent node's data array
            absolute - True or False to indicate whether the data array should be set to the absolute value or should be aggregated with existing data
        Outputs:
            node.XYZ_time_series_data[index] is initialized if it wasn't already
            node.XYZ_time_series_data[index] is set as specified
        """
        i = 0
        for data_type in data_types:
            if data_type == 'DEATHS':
                if not node.deaths_time_series_data:
                    node.initialize_deaths(len(self.time_series_dates))
                if absolute or node.deaths_time_series_data[index] == None:
                    node.deaths_time_series_data[index] = data_values[i]
                elif data_values[i]:
                    node.deaths_time_series_data[index] = node.deaths_time_series_data[index] + data_values[i]
            elif data_type == 'CONFIRMED':
                if not node.confirmed_cases_time_series_data:
                    node.initialize_confirmed_cases(len(self.time_series_dates))
                if absolute or node.confirmed_cases_time_series_data[index] == None:
                    node.confirmed_cases_time_series_data[index] = data_values[i]
                elif data_values[i]:
                    node.confirmed_cases_time_series_data[index] = node.confirmed_cases_time_series_data[index] + data_values[i]
            elif data_type == 'TESTED':
                if not node.people_tested_time_series_data:
                    node.initialize_people_tested(len(self.time_series_dates))
                if absolute or node.people_tested_time_series_data[index] == None:
                    node.people_tested_time_series_data[index] = data_values[i]
                elif data_values[i]:
                    node.people_tested_time_series_data[index] = node.people_tested_time_series_data[index] + data_values[i]
            elif data_type == 'INCIDENT':
                if not node.incident_rate_time_series_data:
                    node.initialize_incident_rate(len(self.time_series_dates))
                if absolute or node.incident_rate_time_series_data[index] == None:
                    node.incident_rate_time_series_data[index] = data_values[i]
                elif data_values[i]:
                    node.incident_rate_time_series_data[index] = node.incident_rate_time_series_data[index] + data_values[i]
            elif data_type == 'ACTIVE':
                if not node.active_cases_time_series_data:
                    node.initialize_active_cases(len(self.time_series_dates))
                if absolute or node.active_cases_time_series_data[index] == None:
                    node.active_cases_time_series_data[index] = data_values[i]
                elif data_values[i]:
                    node.active_cases_time_series_data[index] = node.active_cases_time_series_data[index] + data_values[i]
            elif data_type == 'RECOVERED':
                if not node.recovered_cases_time_series_data:
                    node.initialize_recovered_cases(len(self.time_series_dates))
                if absolute or node.recovered_cases_time_series_data[index] == None:
                    node.recovered_cases_time_series_data[index] = data_values[i]
                elif data_values[i]:
                    node.recovered_cases_time_series_data[index] = node.recovered_cases_time_series_data[index] + data_values[i]
            elif data_type == 'HOSPITALIZED':
                if not node.hospitalizations_time_series_data:
                    node.initialize_hospitalizations(len(self.time_series_dates))
                if absolute or node.hospitalizations_time_series_data[index] == None:
                    node.hospitalizations_time_series_data[index] = data_values[i]
                elif data_values[i]:
                    node.hospitalizations_time_series_data[index] = node.hospitalizations_time_series_data[index] + data_values[i]
                    
            i = i + 1
            
        if aggregate_to_parent and node.parent != None:
            # recursive call for the parent node if we're supposed to aggregate.  Recursion ends when we get to the top of the tree since there is no parent.
            self.__set_node_data_values(node.parent, data_types, data_values, index, aggregate_to_parent, absolute=False)

         
    def read_time_series_data(self, url, filename=None):
        """Description: Reads the Johns Hopkins COVID-19 time series CSV file into the time_series_data dictionary
        Inputs:
            filename - optional string with name and path of file to be opened
            url - optional string with url name and path of file to be opened from github.
            
            Either filename or ulr should be supplied.  The value in filename if supplied takes prescendence
        Outputs:
          self.__time_series_field_locations - updated dictionary with locations added
          self.__time_series_data - dictionary containing the time series data that was read in, organized as:
                                    {"CONFIRMED CASES": {state 1, county 1}:cases[],
                                                        {state 1, county 2}:cases[],
                                     ...}
          return - True if successful, false if not
        """
        if filename != None:
            filename_split = filename.split(".")
            if filename_split[len(filename_split)-2].endswith("_US"):
                us_file_type = True
            else:
                us_file_type = False
    
            filename_split = filename.split("/")
            if 'deaths' in filename_split[len(filename_split)-1]:
                data_types = ['DEATHS']
            else:
                data_types = ['CONFIRMED']
            
            csv_file_obj = open(filename)
            reader_obj = csv.reader(csv_file_obj)
                
        else:
            filename_split = url.split(".")
            if filename_split[len(filename_split)-2].endswith("_US"):
                us_file_type = True
            else:
                us_file_type = False
    
            filename_split = url.split("/")
            if 'deaths' in filename_split[len(filename_split)-1]:
                data_types = ['DEATHS']
            else:
                data_types = ['CONFIRMED']
            
            response = requests.get(url)
            lines = response.content.decode("utf-8").splitlines()
    
            reader_obj = csv.reader(lines)
        
        
        header_row_found = False
        row_count = 1
        for row in reader_obj:
            if header_row_found == False:
                if us_file_type == True:
                    header_row_found = self.__map_time_series_us_locations(row, row_count)
                else:
                    header_row_found = self.__map_time_series_locations(row, row_count)

                if header_row_found:
                    date_list = []
                    for col in range(self.__time_series_field_locations["FIRST_DATE_COL"], self.__time_series_field_locations["LAST_DATE_COL"] + 1):
                        date_list.append(datetime.datetime.strptime(row[col],'%m/%d/%y'))

                    if not self.time_series_dates:
                        # save the first date list read in to self.time_series_dates
                        # this behavior assumes that the dates in any subsequenty time series files read in after the first one are within range
                        # of the dates from the first file.  If this is not true, this function will crash
                        # TODO: Come up with a better way to initialize the date list so that any file that is read in does not make the program crash and data already captured is updated to align to the new date list
                        self.time_series_dates = date_list

                elif row_count > 10:
                    print("ERROR: read_time_series_cases_data - invalid data file")
                    return False
                    
            else:
                country = row[self.__time_series_field_locations["COUNTRY_NAME_COL"]]
                state = row[self.__time_series_field_locations["STATE_NAME_COL"]]
                if us_file_type:
                    county = row[self.__time_series_field_locations["COUNTY_NAME_COL"]]
                else:
                    # this is a world data time series file so there is no county data
                    county = None
                    
                # add the country to the base tree if it's not already there
                country_node = self.time_series_data_tree.get_child_node(country)
                if country_node == None:
                    country_node = Covid19_Tree_Node(country)
                    self.time_series_data_tree.add_child(country_node)

                # add the state to the country tree node if it's not already there
                if state != "":
                    state_node = country_node.get_child_node(state)
                    if state_node == None:
                        state_node = Covid19_Tree_Node(state)
                        country_node.add_child(state_node)
                else:
                    state_node = None
                
                # add the county to the state tree node if it's not already there
                if county != None and county != "":
                    county_node = state_node.get_child_node(county)
                    if county_node == None:
                        county_node = Covid19_Tree_Node(county)
                        state_node.add_child(county_node)
                else:
                    county_node = None
                    
                # add data to the apprpriate entry in the tree for country/state/county and aggregate for whole state, and aggregate for whole country
                i = 0
                for col in range(self.__time_series_field_locations["FIRST_DATE_COL"], self.__time_series_field_locations["LAST_DATE_COL"] + 1):
                    j = self.time_series_dates.index(date_list[i])
                    data_val = [int(float(row[col]))]

                    if county_node != None:
                        self.__set_node_data_values(county_node, data_types, data_val, index=j, aggregate_to_parent=True, absolute=True)
                    elif state_node != None:
                        if country_node.node_name not in self.__world_country_state_aggregration_exclusions_list:
                            self.__set_node_data_values(state_node, data_types, data_val, index=j, aggregate_to_parent=True, absolute=True)
                        else:
                            self.__set_node_data_values(state_node, data_types, data_val, index=j, aggregate_to_parent=False, absolute=True)
                    elif country_node != None:
                        self.__set_node_data_values(country_node, data_types, data_val, index=j, aggregate_to_parent=False, absolute=True)

                    i = i + 1

            row_count = row_count + 1

        if filename != None:
            csv_file_obj.close()

        return header_row_found

    def read_us_daily_report_file(self, reader_obj, data_index):
        """Description: Reads the Johns Hopkins COVID-19 daily report CSV file into the time_series_data dictionary
        Inputs:
            reader_obj - csv reader object to iterate on for reading each row from the file
            data_index - array index that the data from this file is to be read into
        Outputs:
          self.__time_series_data_tree - nodes updated with data read in from the file
          return - True if successful, false if not
        """
        header_row_found = False
        row_count = 1
        for row in reader_obj:
            if header_row_found == False:
                header_row_found = self.__map_us_data_locations(row, row_count)
            elif row[self.__us_data_field_locations["COUNTRY_NAME_COL"]].upper() == "US":
                # only import data for US (since this is the US daily reports you would expect this to always be true, but 
                # some of the Johns Hopkins daily report files in the US folder have other countries mixed in
                country = row[self.__us_data_field_locations["COUNTRY_NAME_COL"]]
                state = row[self.__us_data_field_locations["STATE_NAME_COL"]]

                # add the country to the base tree if it's not already there
                country_node = self.time_series_data_tree.get_child_node(country)
                if country_node == None:
                    country_node = Covid19_Tree_Node(country)
                    self.time_series_data_tree.add_child(country_node)

                # add the state to the country tree node if it's not already there
                state_node = country_node.get_child_node(state)
                if state_node == None:
                    state_node = Covid19_Tree_Node(state)
                    country_node.add_child(state_node)
                    
                # add data to the appropriate data array for the state
                try:
                    cases = int(row[self.__us_data_field_locations["CONFIRMED_CASES_COL"]])
                except:
                    cases = None
                try:
                    deaths = int(row[self.__us_data_field_locations["DEATHS_COL"]])
                except:
                    deaths = None
                try:
                    tested = int(row[self.__us_data_field_locations["PEOPLE_TESTED_COL"]])
                except:
                    tested = None
                try:
                    rate = float(row[self.__us_data_field_locations["INCIDENT_RATE_COL"]])
                except:
                    rate = None
                try:
                    active = int(row[self.__us_data_field_locations["ACTIVE_CASES_COL"]])
                except:
                    active = None
                try:
                    recovered = int(row[self.__us_data_field_locations["RECOVERED_CASES_COL"]])
                except:
                    recovered = None
                try:
                    hospitalized = int(row[self.__us_data_field_locations["PEOPLE_HOSPITALIZED_COL"]])
                except:
                    hospitalized = None
                try:
                    latitude = float(row[self.__us_data_field_locations["LATITUDE_COL"]])
                except:
                    latitude = None
                try:
                    longitude = float(row[self.__us_data_field_locations["LONGITUDE_COL"]])
                except:
                    longitude = None

                if state_node.latitude == None:
                    state_node.latitude = latitude
                if state_node.longitude == None:
                    state_node.longitude = longitude

                # set values that will be aggregated to the parent
                data_types = ['TESTED', 'ACTIVE', 'RECOVERED', 'HOSPITALIZED']
                data_values = [tested, active, recovered, hospitalized]
                self.__set_node_data_values(state_node, data_types, data_values, data_index, aggregate_to_parent=True, absolute=True)

                # set values that will not be aggregated to the parent
                #todo may want to handle confirmed and deaths as aggregated to parent, but these data values have already been read in from the time series file so I'm skipping them for now
                data_types = ['CONFIRMED', 'DEATHS', 'INCIDENT']
                data_values = [cases, deaths, rate]
                self.__set_node_data_values(state_node, data_types, data_values, data_index, aggregate_to_parent=False, absolute=True)

            row_count = row_count + 1
        return header_row_found

    def read_world_daily_report_file(self, reader_obj, data_index):
        """Description: Reads the Johns Hopkins COVID-19 daily report CSV file into the time_series_data dictionary
        Inputs:
            reader_obj - csv reader object to iterate on for reading each row from the file
            data_index - array index that the data from this file is to be read into
        Outputs:
          self.__time_series_data_tree - nodes updated with data read in from the file
          return - True if successful, false if not
        """
        header_row_found = False
        row_count = 1
        for row in reader_obj:
            if header_row_found == False:
                header_row_found = self.__map_world_data_locations(row, row_count)
            else:
                country = row[self.__world_data_field_locations["COUNTRY_NAME_COL"]]
                state = row[self.__world_data_field_locations["STATE_NAME_COL"]]
                county = row[self.__world_data_field_locations["COUNTY_NAME_COL"]]

                if country not in self.__world_daily_reports_exclusions_list:
                    # add the country to the base tree if it's not already there
                    country_node = self.time_series_data_tree.get_child_node(country)
                    if country_node == None:
                        country_node = Covid19_Tree_Node(country)
                        self.time_series_data_tree.add_child(country_node)
                    data_node = country_node
    
                    # add the state to the country tree node if it's not already there
                    if state != "":
                        state_node = country_node.get_child_node(state)
                        if state_node == None:
                            state_node = Covid19_Tree_Node(state)
                            country_node.add_child(state_node)
                        data_node = state_node
                            
                        #add the county to the state if it's not already there
                        if county != "":
                            county_node = state_node.get_child_node(county)
                            if county_node == None:
                                county_node = Covid19_Tree_Node(county)
                                state_node.add_child(county_node)
                            data_node = county_node
                        else:
                            county_node = None
                    else:
                        state_node = None
                        county_node = None
    
                    # add data to the appropriate data array for the appropriate node
                    try:
                        cases = int(row[self.__world_data_field_locations["CONFIRMED_CASES_COL"]])
                    except:
                        cases = None
                    try:
                        deaths = int(row[self.__world_data_field_locations["DEATHS_COL"]])
                    except:
                        deaths = None
                    try:
                        rate = float(row[self.__world_data_field_locations["INCIDENT_RATE_COL"]])
                    except:
                        rate = None
                    try:
                        active = int(row[self.__world_data_field_locations["ACTIVE_CASES_COL"]])
                    except:
                        active = None
                    try:
                        recovered = int(row[self.__world_data_field_locations["RECOVERED_CASES_COL"]])
                    except:
                        recovered = None
                    try:
                        latitude = float(row[self.__world_data_field_locations["LATITUDE_COL"]])
                    except:
                        latitude = None
                    try:
                        longitude = float(row[self.__world_data_field_locations["LONGITUDE_COL"]])
                    except:
                        longitude = None
    
                    if data_node.latitude == None:
                        data_node.latitude = latitude
                    if data_node.longitude == None:
                        data_node.longitude = longitude
    
                    # set values that will be aggregated to the parent
                    data_types = ['ACTIVE', 'RECOVERED']
                    data_values = [active, recovered]
                    self.__set_node_data_values(data_node, data_types, data_values, data_index, aggregate_to_parent=True, absolute=True)
    
                    # set values that will not be aggregated to the parent
                    #todo may want to handle confirmed and deaths as aggregated to parent, but these data values have already been read in from the time series file so I'm skipping them for now
                    data_types = ['CONFIRMED', 'DEATHS', 'INCIDENT']
                    data_values = [cases, deaths, rate]
                    self.__set_node_data_values(data_node, data_types, data_values, data_index, aggregate_to_parent=False, absolute=True)

            row_count = row_count + 1
        return header_row_found
        
    def read_daily_reports_data(self, folder, data_location, on_disk=False):
        """Description: Reads the Johns Hopkins COVID-19 daily report CSV file into the time_series_data dictionary
        Inputs:
            folder - string with path of daily report files to be opened
            data_location - "world" if world daily reports files, "us" if folder contains US daily reports files
            local - True if folder is on the local file system, false if folder is on remote github repository
        Outputs:
          self.__world_data_field_locations - updated dictionary with locations added
          self.__time_series_data - dictionary containing the time series data that was read in, organized as:
                                    {"CONFIRMED CASES": {state 1, county 1}:cases[],
                                                        {state 1, county 2}:cases[],
                                     ...}
          return - True if successful, false if not
        """
        if on_disk:
            all_files = []
            for d in os.listdir(folder):
                bd = os.path.join(folder, d)
                if os.path.isfile(bd):
                    all_files.append([bd, d])
            
            for filename in all_files:
                filename_str_partition = filename[1].partition('.')
                if filename_str_partition[2].upper() == 'CSV':
                    file_date_val = datetime.datetime.strptime(filename_str_partition[0],'%m-%d-%Y')
                    print(filename[1], " - ", file_date_val)
                    
                    csv_file_obj = open(filename[0])
                    reader_obj = csv.reader(csv_file_obj)
                    i = self.time_series_dates.index(file_date_val)
                    
                    if data_location == "world":
                        status = self.read_world_daily_report_file(reader_obj, i)
                    elif data_location == "us":
                        status = self.read_us_daily_report_file(reader_obj, i)
                    else:
                        raise ValueError(data_location + " is not a valid option")
                        
                    if status == False:
                        return False
            csv_file_obj.close()
        else:
            for filename in self.github_tree.list_files(folder, extensions=".csv"):
                file_date_val = datetime.datetime.strptime(self.github_tree.split_file(filename),'%m-%d-%Y')
                print(filename, " - ", file_date_val)
                
                url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/"
                url += filename.strip("/")
                response = requests.get(url)
                lines = response.content.decode("utf-8").splitlines()
    
                reader_obj = csv.reader(lines)
                i = self.time_series_dates.index(file_date_val)

                if data_location == "world":
                    status = self.read_world_daily_report_file(reader_obj, i)
                elif data_location == "us":
                    status = self.read_us_daily_report_file(reader_obj, i)
                else:
                    raise ValueError(data_location + " is not a valid option")
                    
                if status == False:
                    return False

        return True
       
    def is_date(date):
        """Description: Determines whether a string is a valid date in the defined formats
        Inputs:
            date - string value for the date to be evaluated
        Outputs:
            return - True if string is a valid date, False if string is not a valid date
        """
        # Defined formats for valid dates
        fmts = ('%m/%d/%y', '%m/%d/%Y')

        for fmt in fmts:
            try:
                d = datetime.datetime.strptime(date, fmt)
                return True
            except:
                pass
        
        return False
        
    def __map_time_series_us_locations(self,row, row_num):
        """Description: Fills in the dictionary of locations with the associated row and column index
        Inputs:
            row - the comma separated row list to check for header columns
            row_num - the current row number
        Outputs:
          self.__time_series_field_locations - updated dictionary with locations added
          return - True if all locations found, false if not
        """
        found_everything = False
        self.__time_series_field_locations["HEADER_ROW"] = -1
        self.__time_series_field_locations["COUNTRY_NAME_COL"] = -1
        self.__time_series_field_locations["STATE_NAME_COL"] = -1
        self.__time_series_field_locations["COUNTY_NAME_COL"] = -1
        self.__time_series_field_locations["FIRST_DATE_COL"] = -1
        self.__time_series_field_locations["LAST_DATE_COL"] = -1

        i = 0
        while not found_everything and i < len(row):
            if row[i].upper() == "COUNTRY_REGION":
                self.__time_series_field_locations["COUNTRY_NAME_COL"] = i
                self.__time_series_field_locations["HEADER_ROW"] = row_num
            elif row[i].upper() == "ADMIN2":
                self.__time_series_field_locations["COUNTY_NAME_COL"] = i
                self.__time_series_field_locations["HEADER_ROW"] = row_num
            elif row[i].upper() == "PROVINCE_STATE":
                self.__time_series_field_locations["STATE_NAME_COL"] = i
                self.__time_series_field_locations["HEADER_ROW"] = row_num
            elif Covid19_Data.is_date(row[i].upper()):
                self.__time_series_field_locations["FIRST_DATE_COL"] = i
                self.__time_series_field_locations["LAST_DATE_COL"] = len(row)-1
                self.__time_series_field_locations["HEADER_ROW"] = row_num
            i = i + 1

            found_everything = True
            for x in self.__time_series_field_locations:
                if self.__time_series_field_locations[x] == -1:
                    found_everything = False
                    self.__time_series_field_locations["HEADER_ROW"] = -1

        return(found_everything)

    def __map_time_series_locations(self,row, row_num):
        """Description: Fills in the dictionary of locations with the associated row and column index
        Inputs:
            row - the comma separated row list to check for header columns
            row_num - the current row number
        Outputs:
          self.__time_series_field_locations - updated dictionary with locations added
          return - True if all locations found, false if not
        """
        found_everything = False
        self.__time_series_field_locations["HEADER_ROW"] = -1
        self.__time_series_field_locations["COUNTRY_NAME_COL"] = -1
        self.__time_series_field_locations["STATE_NAME_COL"] = -1
        self.__time_series_field_locations["COUNTY_NAME_COL"] = -1
        self.__time_series_field_locations["FIRST_DATE_COL"] = -1
        self.__time_series_field_locations["LAST_DATE_COL"] = -1

        i = 0
        while not found_everything and i < len(row):
            if row[i].upper() == "COUNTRY/REGION":
                self.__time_series_field_locations["COUNTRY_NAME_COL"] = i
                self.__time_series_field_locations["HEADER_ROW"] = row_num
            elif row[i].upper() == "PROVINCE/STATE":
                self.__time_series_field_locations["STATE_NAME_COL"] = i
                self.__time_series_field_locations["HEADER_ROW"] = row_num
            elif Covid19_Data.is_date(row[i].upper()):
                self.__time_series_field_locations["FIRST_DATE_COL"] = i
                self.__time_series_field_locations["LAST_DATE_COL"] = len(row)-1
                self.__time_series_field_locations["HEADER_ROW"] = row_num
            i = i + 1

            found_everything = True
            for x in self.__time_series_field_locations:
                if x != "COUNTY_NAME_COL" and self.__time_series_field_locations[x] == -1:
                    found_everything = False
                    self.__time_series_field_locations["HEADER_ROW"] = -1

        return(found_everything)

    def __map_us_data_locations(self,row, row_num):
        """Description: Fills in the dictionary of locations with the associated row and column index
        Inputs:
            row - the comma separated row list to check for header columns
            row_num - the current row number
        Outputs:
          self.__us_data_field_locations - updated dictionary with locations added
          return - True if all locations found, false if not
        """

        found_everything = False
        self.__us_data_field_locations["HEADER_ROW"] = -1
        self.__us_data_field_locations["COUNTRY_NAME_COL"] = -1
        self.__us_data_field_locations["STATE_NAME_COL"] = -1
        self.__us_data_field_locations["LATITUDE_COL"] = -1
        self.__us_data_field_locations["LONGITUDE_COL"] = -1
        self.__us_data_field_locations["CONFIRMED_CASES_COL"] = -1
        self.__us_data_field_locations["DEATHS_COL"] = -1
        self.__us_data_field_locations["PEOPLE_TESTED_COL"] = -1
        self.__us_data_field_locations["INCIDENT_RATE_COL"] = -1
        self.__us_data_field_locations["ACTIVE_CASES_COL"] = -1
        self.__us_data_field_locations["RECOVERED_CASES_COL"] = -1
        self.__us_data_field_locations["PEOPLE_HOSPITALIZED_COL"] = -1

        i = 0
        while not found_everything and i < len(row):
            if row[i].upper() == "COUNTRY_REGION":
                self.__us_data_field_locations["COUNTRY_NAME_COL"] = i
                self.__us_data_field_locations["HEADER_ROW"] = row_num                
            elif row[i].upper() == "PROVINCE_STATE":
                self.__us_data_field_locations["STATE_NAME_COL"] = i
                self.__us_data_field_locations["HEADER_ROW"] = row_num
            elif row[i].upper() == "CONFIRMED":
                self.__us_data_field_locations["CONFIRMED_CASES_COL"] = i
                self.__us_data_field_locations["HEADER_ROW"] = row_num
            elif row[i].upper() == "DEATHS":
                self.__us_data_field_locations["DEATHS_COL"] = i
                self.__us_data_field_locations["HEADER_ROW"] = row_num
            elif row[i].upper() == "PEOPLE_TESTED":
                self.__us_data_field_locations["PEOPLE_TESTED_COL"] = i
                self.__us_data_field_locations["HEADER_ROW"] = row_num
            elif row[i].upper() == "INCIDENT_RATE":
                self.__us_data_field_locations["INCIDENT_RATE_COL"] = i
                self.__us_data_field_locations["HEADER_ROW"] = row_num
            elif row[i].upper() == "RECOVERED":
                self.__us_data_field_locations["RECOVERED_CASES_COL"] = i
                self.__us_data_field_locations["HEADER_ROW"] = row_num
            elif row[i].upper() == "ACTIVE":
                self.__us_data_field_locations["ACTIVE_CASES_COL"] = i
                self.__us_data_field_locations["HEADER_ROW"] = row_num
            elif row[i].upper() == "PEOPLE_HOSPITALIZED":
                self.__us_data_field_locations["PEOPLE_HOSPITALIZED_COL"] = i
                self.__us_data_field_locations["HEADER_ROW"] = row_num
            elif row[i].upper() == "LAT":
                self.__us_data_field_locations["LATITUDE_COL"] = i
                self.__us_data_field_locations["HEADER_ROW"] = row_num
            elif row[i].upper() == "LONG_":
                self.__us_data_field_locations["LONGITUDE_COL"] = i
                self.__us_data_field_locations["HEADER_ROW"] = row_num

            i = i + 1

            found_everything = True
            for x in self.__us_data_field_locations:
                if self.__us_data_field_locations[x] == -1:
                    found_everything = False
                    self.__us_data_field_locations["HEADER_ROW"] = -1

        return(found_everything)

    def __map_world_data_locations(self,row, row_num):
        """Description: Fills in the dictionary of locations with the associated row and column index
        Inputs:
            row - the comma separated row list to check for header columns
            row_num - the current row number
        Outputs:
          self.__world_data_field_locations - updated dictionary with locations added
          return - True if all locations found, false if not
        """

        found_everything = False
        # fields marked as -1 are mandatory, -2 are optional
        self.__world_data_field_locations["HEADER_ROW"] = -1
        self.__world_data_field_locations["COUNTRY_NAME_COL"] = -1
        self.__world_data_field_locations["STATE_NAME_COL"] = -1
        self.__world_data_field_locations["COUNTY_NAME_COL"] = -2
        self.__world_data_field_locations["LATITUDE_COL"] = -2
        self.__world_data_field_locations["CONFIRMED_CASES_COL"] = -1
        self.__world_data_field_locations["LONGITUDE_COL"] = -2
        self.__world_data_field_locations["DEATHS_COL"] = -1
        self.__world_data_field_locations["INCIDENT_RATE_COL"] = -2
        self.__world_data_field_locations["ACTIVE_CASES_COL"] = -2
        self.__world_data_field_locations["RECOVERED_CASES_COL"] = -1

        for i in range(0,len(row)):
            if row[i].upper() == "COUNTRY_REGION" or row[i].upper() == "COUNTRY/REGION":
                self.__world_data_field_locations["COUNTRY_NAME_COL"] = i
                self.__world_data_field_locations["HEADER_ROW"] = row_num
            elif row[i].upper() == "PROVINCE_STATE" or "PROVINCE/STATE" in row[i].upper():
                self.__world_data_field_locations["STATE_NAME_COL"] = i
                self.__world_data_field_locations["HEADER_ROW"] = row_num
            elif row[i].upper() == "ADMIN2":
                self.__world_data_field_locations["COUNTY_NAME_COL"] = i
                self.__world_data_field_locations["HEADER_ROW"] = row_num
            elif row[i].upper() == "CONFIRMED":
                self.__world_data_field_locations["CONFIRMED_CASES_COL"] = i
                self.__world_data_field_locations["HEADER_ROW"] = row_num
            elif row[i].upper() == "DEATHS":
                self.__world_data_field_locations["DEATHS_COL"] = i
                self.__world_data_field_locations["HEADER_ROW"] = row_num
            elif row[i].upper() == "INCIDENT_RATE":
                self.__world_data_field_locations["INCIDENT_RATE_COL"] = i
                self.__world_data_field_locations["HEADER_ROW"] = row_num
            elif row[i].upper() == "RECOVERED":
                self.__world_data_field_locations["RECOVERED_CASES_COL"] = i
                self.__world_data_field_locations["HEADER_ROW"] = row_num
            elif row[i].upper() == "ACTIVE":
                self.__world_data_field_locations["ACTIVE_CASES_COL"] = i
                self.__world_data_field_locations["HEADER_ROW"] = row_num
            elif row[i].upper() == "LAT":
                self.__world_data_field_locations["LATITUDE_COL"] = i
                self.__world_data_field_locations["HEADER_ROW"] = row_num
            elif row[i].upper() == "LONG_":
                self.__world_data_field_locations["LONGITUDE_COL"] = i
                self.__world_data_field_locations["HEADER_ROW"] = row_num

        found_everything = True
        for x in self.__world_data_field_locations:
            if self.__world_data_field_locations[x] == -1:
                found_everything = False
                self.__world_data_field_locations["HEADER_ROW"] = -1

        return(found_everything)
               
    def get_cases(self,state, county):
        """Description: Accessor function to get cases data for a specified state and county
        Inputs:
            state - the state to retrieve cases data for
            county - the county to retrieve cases data for ("ALL" for aggregate of all counties)
        Outputs:
          return - [[date], [cases]] or None of invalid state / county
        """
        key = Covid19_Data.create_key(state, county)
        if key in self.__time_cases_data["CONFIRMED CASES"]:
            dates = self.__time_series_dates.copy()
            cases = self.__time_series_data["CONFIRMED CASES"][key].copy()
            return([dates,cases])
        else:
            return(None)
  
    def get_daily_new_cases(self,state, county, key):
        """Description: Accessor function to get new daily cases data for a specified state and county
        Inputs:
            state - optional, the state to retrieve cases data for (ignored if the key value is not None)
            county - optional, the county to retrieve cases data for ("ALL" for aggregate of all counties) (ignored if the key value is not None)
            key - optional, key in form "State, County" to retrieve cases data
        Outputs:
          return - [[date], [cases]] or None of invalid state / county
        """
        if key == None:
            key = Covid19_Data.create_key(state, county)

        dates = []
        new_cases = []
        if key in self.__time_series_data["CONFIRMED CASES"]:
            for i in range (1, len(self.__time_series_dates)):
                dates.append(self.__time_series_dates[i])
                if self.__time_series_data["CONFIRMED CASES"][key][i] != None:
                    if self.__time_series_data["CONFIRMED CASES"][key][i-1] != None:
                        new_case_val = self.__time_series_data["CONFIRMED CASES"][key][i] - self.__time_series_data["CONFIRMED CASES"][key][i-1]
                    else:
                        # first day that data appears should be set to 0 in new daily data because otherwise it would be a large jump
                        # of everything up to that point, not just on that day;  the actual amount on this day is unknown
                        new_case_val = 0
                else:
                    new_case_val = None
                new_cases.append(new_case_val)
            return([dates,new_cases])
        else:
            return(None)


    def get_daily_new_deaths(self,state, county, key):
        """Description: Accessor function to get new daily deaths data for a specified state and county
        Inputs:
            state - optional, the state to retrieve cases data for (ignored if the key value is not None)
            county - optional, the county to retrieve cases data for ("ALL" for aggregate of all counties) (ignored if the key value is not None)
            key - optional, key in form "State, County" to retrieve cases data
        Outputs:
          return - [[date], [cases]] or None of invalid state / county
        """
        if key == None:
            key = Covid19_Data.create_key(state, county)

        dates = []
        new_deaths = []
        if key in self.__time_series_data["DEATHS"]:
            for i in range (1, len(self.__time_series_dates)):
                dates.append(self.__time_series_dates[i])
                if self.__time_series_data["DEATHS"][key][i] != None:
                    if self.__time_series_data["DEATHS"][key][i-1] != None:
                        # first day that data appears should be set to 0 in new daily data because otherwise it would be a large jump
                        # of everything up to that point, not just on that day;  the actual amount on this day is unknown
                        new_deaths_val = self.__time_series_data["DEATHS"][key][i] - self.__time_series_data["DEATHS"][key][i-1]
                    else:
                        new_deaths_val = 0
                else:
                    new_deaths_val = None
                new_deaths.append(new_deaths_val)
            return([dates,new_deaths])
        else:
            return(None)


    def get_daily_new_people_tested(self,state, county, key):
        """Description: Accessor function to get new daily people tested data for a specified state and county
        Inputs:
            state - optional, the state to retrieve cases data for (ignored if the key value is not None)
            county - optional, the county to retrieve cases data for ("ALL" for aggregate of all counties) (ignored if the key value is not None)
            key - optional, key in form "State, County" to retrieve people tested data
        Outputs:
          return - [[date], [cases]] or None of invalid state / county
        """
        if key == None:
            key = Covid19_Data.create_key(state, county)

        dates = []
        new_cases = []
        if key in self.__time_series_data["PEOPLE TESTED"]:
            for i in range (1, len(self.__time_series_dates)):
                dates.append(self.__time_series_dates[i])
                if self.__time_series_data["PEOPLE TESTED"][key][i] != None:
                    if self.__time_series_data["PEOPLE TESTED"][key][i-1] != None:
                        new_case_val = self.__time_series_data["PEOPLE TESTED"][key][i] - self.__time_series_data["PEOPLE TESTED"][key][i-1]
                    else:
                        # first day that people tested data appears should be set to 0 in new daily tested data because otherwise it would be a large jump
                        # of all the testing done up to that point, not just on that day;  the actual amount tested on this day is unknown
                        new_case_val = 0
                else:
                    new_case_val = None
                new_cases.append(new_case_val)
            return([dates,new_cases])
        else:
            return(None)

    def get_state_county_cases_keys(self):
        """Description: Accessor function to get all of the state and counties in the time series data dicitionary under confirmed cases
        Inputs: None
        Outputs:
          return - [[states], [counties]]
        """
        states = []
        counties = []
        for key in self.__time_series_data["CONFIRMED CASES"]:
            values = key.partition(",")
            states.append(values[0])
            counties.append(values[2].lstrip())
        return([states, counties])

    def get_cases_keys(self):
        """Description: Accessor function to get all the keys in the time series data dictionary under confirmed cases
        Inputs: None
        Outputs:
          return - [keys]
        """
        keys = []
        for key in self.__time_series_data["CONFIRMED CASES"]:
            keys.append(key)
        return(keys)

    def get_deaths_keys(self):
        """Description: Accessor function to get all the keys in the time series data dictionary under deaths
        Inputs: None
        Outputs:
          return - [keys]
        """
        keys = []
        for key in self.__time_series_data["DEATHS"]:
            keys.append(key)
        return(keys)

    def get_people_tested_keys(self):
        """Description: Accessor function to get all the keys in the time series data dictionary under people tested
        Inputs: None
        Outputs:
          return - [keys]
        """
        keys = []
        for key in self.__time_series_data["PEOPLE TESTED"]:
            keys.append(key)
        return(keys)

    def get_state_county_incident_rate_keys(self):
        """Description: Accessor function to get all of the state and counties in the time series data dicitionary under incident rate
        Inputs: None
        Outputs:
          return - [[states], [counties]]
        """
        states = []
        counties = []
        for key in self.__time_series_data["INCIDENT RATE"]:
            values = key.partition(",")
            states.append(values[0])
            counties.append(values[2].lstrip())
        return([states, counties])
 
    def get_incident_rate_keys(self):
        """Description: Accessor function to get all the keys in the time series data dictionary under incidnet rate
        Inputs: None
        Outputs:
          return - [keys]
        """
        keys = []
        for key in self.__time_series_data["INCIDENT RATE"]:
            keys.append(key)
        return(keys)

    def get_dates(self):
        """Description: Accessor function to get a copy of the list of dates for data points
        Inputs: None
        Outputs:
          return - [dates]
        """
        dates = []
        for date in self.time_series_dates:
            dates.append(date)
        return(dates)

    def get_people_tested(self,state,county,key):
        """Description: Accessor function to get list of dates for data points
        Inputs: None
        Outputs:
          return - [dates]
        """
        if key == None:
            key = Covid19_Data.create_key(state,county)

        data = []
        for val in self.__time_series_data["PEOPLE TESTED"][key]:
            data.append(val)
        return(data)
    
    
    def create_lookup_tables(self, start_date, end_date):
        integer_to_dates_table = {}
        dates_to_integer_table = {}
        
        delta = datetime.timedelta(days=1)
        i = 0
        while start_date <= end_date:
            date = start_date.strftime("%m-%d-%Y")
            # create lookup table for converting to integers for math 
            # and back to dates for plotting
            integer_to_dates_table.update({i:date})
            dates_to_integer_table.update({date:i})
            
            start_date += delta  # increase day and integer count by 1
            i += 1     
        
        return integer_to_dates_table, dates_to_integer_table
        
    def plot_cases_data(self, country_list, state_list, county_list):
        """Description: function to create an XY plot of specified state/county pairs
        Inputs: 
            country_list - list of countries in country / state / county path
            state_list - optional, list of states in country / state / county path
            county_list - optional, list of counties in country / state / county path
        Outpus:
            A plot window is opened
        """
        start_dates = []
        end_dates = []
        
        x_datasets = []
        y_datasets = []
        labels = []

        for i in range(0, len(country_list)):
            country_node = self.time_series_data_tree.get_child_node(country_list[i])
            if (country_node == None):
                print("ERROR: plot_cases_data - invalid country: ", country_list[i])
                return(False)
            state_node = country_node.get_child_node(state_list[i])
            if (state_node == None):
                plot_node = country_node
                label_string = country_list[i] + " - All"
            else:
                county_node = state_node.get_child_node(county_list[i])                    
                if (county_node == None):
                    plot_node = state_node
                    label_string = country_list[i] + ", " + state_list[i] + " - All"
                else:
                    plot_node = county_node
                    label_string = country_list[i] + ", " + state_list[i] + ", " + county_list[i]
            
            if plot_node.confirmed_cases_time_series_data:
                x = self.time_series_dates
                
                datemin = datetime.date(x[0].year, x[0].month, 1)
                datemax = datetime.date(x[len(x)-1].year, x[len(x)-1].month + 1, 1)
                start_dates.append(datemin)
                end_dates.append(datemax)
                y = plot_node.confirmed_cases_time_series_data
                
                x_datasets.append(x)
                y_datasets.append(y)
                labels.append(label_string)

            else:
                print("No confirmed cases data for country / state / county path: ", country_list[i], state_list[i], county_list[i])
                return(False)
            

        integer_to_dates_table, dates_to_integer_table = self.create_lookup_tables(min(start_dates), max(end_dates))
        
        integer_x_datasets = []  # convert dataset x axis from dates to integers using lookup table
        for x_dataset in x_datasets:
            dataset = []
            for x in x_dataset:
                dataset.append(dates_to_integer_table.get(x.strftime("%m-%d-%Y")))
            integer_x_datasets.append(dataset)

        gui = matplotlib_gui.MatplotlibGUI(integer_to_dates_table, "Date", "Confirmed Cases")
        gui.new_figure(1, 1)

        gui.add_dataset(integer_x_datasets, y_datasets, labels)
        while gui.mainloop(): pass

        
    def plot_deaths_data(self, country_list, state_list, county_list):
        """Description: function to create an XY plot of specified state/county pairs
        Inputs: 
            country_list - list of countries in country / state / county path
            state_list - optional, list of states in country / state / county path
            county_list - optional, list of counties in country / state / county path
        Outpus:
            A plot window is opened
        """
        start_dates = []
        end_dates = []
        
        x_datasets = []
        y_datasets = []
        labels = []


        for i in range(0, len(country_list)):
            country_node = self.time_series_data_tree.get_child_node(country_list[i])
            if (country_node == None):
                print("ERROR: plot_cases_data - invalid country: ", country_list[i])
                return(False)
            state_node = country_node.get_child_node(state_list[i])
            if (state_node == None):
                plot_node = country_node
                label_string = country_list[i] + " - All"
            else:
                county_node = state_node.get_child_node(county_list[i])                    
                if (county_node == None):
                    plot_node = state_node
                    label_string = country_list[i] + ", " + state_list[i] + " - All"
                else:
                    plot_node = county_node
                    label_string = country_list[i] + ", " + state_list[i] + ", " + county_list[i]
            
            if plot_node.confirmed_cases_time_series_data:
                x = self.time_series_dates
                
                datemin = datetime.date(x[0].year, x[0].month, 1)
                datemax = datetime.date(x[len(x)-1].year, x[len(x)-1].month + 1, 1)
                start_dates.append(datemin)
                end_dates.append(datemax)
                y = plot_node.deaths_time_series_data
                
                x_datasets.append(x)
                y_datasets.append(y)
                labels.append(label_string)

            else:
                print("No deaths data for country / state / county path: ", country_list[i], state_list[i], county_list[i])
                return(False)

        integer_to_dates_table, dates_to_integer_table = self.create_lookup_tables(min(start_dates), max(end_dates))
        
        integer_x_datasets = []  # convert dataset x axis from dates to integers using lookup table
        for x_dataset in x_datasets:
            dataset = []
            for x in x_dataset:
                dataset.append(dates_to_integer_table.get(x.strftime("%m-%d-%Y")))
            integer_x_datasets.append(dataset)

        gui = matplotlib_gui.MatplotlibGUI(integer_to_dates_table, "Date", "Deaths")
        gui.new_figure(1, 1)

        gui.add_dataset(integer_x_datasets, y_datasets, labels)
        while gui.mainloop(): pass


    def plot_new_cases_data(self, state_list, county_list, key_list):
        """Description: function to create an XY plot of specified state/county pairs
        Inputs: 
            state_list - optional, list of states in state / county pair list (ignored if key_list is not None)
            county_list - optional, list of counties in state / county pair list (ignored if key_list is not None)
            key_list - optional, list of key values ("State, County") to plot data for
        Outpus:
            A plot window is opened
        """
        # create list of keys
        if key_list == None:
            key_list = []
            for i in range(0, len(state_list)):
                key_val = Covid19_Data.create_key(state_list[i], county_list[i])
                key_list.append(key_val)
                
        start_dates = []
        end_dates = []
        
        x_datasets = []
        y_datasets = []
        labels = []
        
        for key_val in key_list:
            if key_val in self.__time_series_data["CONFIRMED CASES"]:
                [x, y] = self.get_daily_new_cases(state=None, county=None, key=key_val)
                datemin = datetime.date(x[0].year, x[0].month, 1)
                datemax = datetime.date(x[len(x)-1].year, x[len(x)-1].month + 1, 1)
                
                start_dates.append(datemin)
                end_dates.append(datemax)
                
                x_datasets.append(x)
                y_datasets.append(y)
                labels.append(key_val)

            else:
                print("invalid state / county pair value: ", key_val)
                return(False)

        integer_to_dates_table, dates_to_integer_table = self.create_lookup_tables(min(start_dates), max(end_dates))
        
        integer_x_datasets = []  # convert dataset x axis from dates to integers using lookup table
        for x_dataset in x_datasets:
            dataset = []
            for x in x_dataset:
                dataset.append(dates_to_integer_table.get(x.strftime("%m-%d-%Y")))
            integer_x_datasets.append(dataset)
            
        gui = matplotlib_gui.MatplotlibGUI(integer_to_dates_table, "Date", "Daily New Cases")
        gui.new_figure(1, 1)

        gui.add_dataset(integer_x_datasets, y_datasets, labels)
        while gui.mainloop(): pass 


    def plot_new_deaths_data(self, state_list, county_list, key_list):
        """Description: function to create an XY plot of specified state/county pairs
        Inputs: 
            state_list - optional, list of states in state / county pair list (ignored if key_list is not None)
            county_list - optional, list of counties in state / county pair list (ignored if key_list is not None)
            key_list - optional, list of key values ("State, County") to plot data for
        Outpus:
            A plot window is opened
        """
        # create list of keys
        if key_list == None:
            key_list = []
            for i in range(0, len(state_list)):
                key_val = Covid19_Data.create_key(state_list[i], county_list[i])
                key_list.append(key_val)
                
        start_dates = []
        end_dates = []
        
        x_datasets = []
        y_datasets = []
        labels = []
        
        for key_val in key_list:
            if key_val in self.__time_series_data["DEATHS"]:
                [x, y] = self.get_daily_new_deaths(state=None, county=None, key=key_val)
                datemin = datetime.date(x[0].year, x[0].month, 1)
                datemax = datetime.date(x[len(x)-1].year, x[len(x)-1].month + 1, 1)
                
                start_dates.append(datemin)
                end_dates.append(datemax)
                
                x_datasets.append(x)
                y_datasets.append(y)
                labels.append(key_val)

            else:
                print("invalid state / county pair value: ", key_val)
                return(False)

        integer_to_dates_table, dates_to_integer_table = self.create_lookup_tables(min(start_dates), max(end_dates))
        
        integer_x_datasets = []  # convert dataset x axis from dates to integers using lookup table
        for x_dataset in x_datasets:
            dataset = []
            for x in x_dataset:
                dataset.append(dates_to_integer_table.get(x.strftime("%m-%d-%Y")))
            integer_x_datasets.append(dataset)
            
        gui = matplotlib_gui.MatplotlibGUI(integer_to_dates_table, "Date", "Daily New Deaths")
        gui.new_figure(1, 1)

        gui.add_dataset(integer_x_datasets, y_datasets, labels)
        while gui.mainloop(): pass 

        
    def plot_incident_rate_data(self, state_list, county_list, key_list):
        """Description: function to create an XY plot of specified state/county pairs
        Inputs: 
            state_list - optional, list of states in state / county pair list (ignored if key_list is not None)
            county_list - optional, list of counties in state / county pair list (ignored if key_list is not None)
            key_list - optional, list of key values ("State, County") to plot data for
        Outpus:
            A plot window is opened
        """
        # create list of keys
        if key_list == None:
            key_list = []
            for i in range(0, len(state_list)):
                key_val = Covid19_Data.create_key(state_list[i], county_list[i])
                key_list.append(key_val)

        start_dates = []
        end_dates = []
        
        x_datasets = []
        y_datasets = []
        labels = []
        

        for key_val in key_list:
            if key_val in self.__time_series_data["INCIDENT RATE"]:
                x = self.__time_series_dates
                datemin = datetime.date(x[0].year, x[0].month, 1)
                datemax = datetime.date(x[len(x)-1].year, x[len(x)-1].month + 1, 1)

                y = self.__time_series_data["INCIDENT RATE"][key_val].copy()
                
                start_dates.append(datemin)
                end_dates.append(datemax)
                
                x_datasets.append(x)
                y_datasets.append(y)
                labels.append(key_val)
            else:
                print("invalid state / county pair value: ", key_val)
                return(False)
            
        integer_to_dates_table, dates_to_integer_table = self.create_lookup_tables(min(start_dates), max(end_dates))
        
        integer_x_datasets = []  # convert dataset x axis from dates to integers using lookup table
        for x_dataset in x_datasets:
            dataset = []
            for x in x_dataset:
                dataset.append(dates_to_integer_table.get(x.strftime("%m-%d-%Y")))
            integer_x_datasets.append(dataset)
            
        gui = matplotlib_gui.MatplotlibGUI(integer_to_dates_table, "Date", "Confirmed Cases per 100000 Population", "Incident Rate")
        gui.new_figure(1, 1)

        gui.add_dataset(integer_x_datasets, y_datasets, labels)
        while gui.mainloop(): pass 


    def plot_people_tested_data(self, state_list, county_list, key_list):
        """Description: function to create an XY plot of specified state/county pairs
        Inputs: 
            state_list - optional, list of states in state / county pair list (ignored if key_list is not None)
            county_list - optional, list of counties in state / county pair list (ignored if key_list is not None)
            key_list - optional, list of key values ("State, County") to plot data for
        Outpus:
            A plot window is opened
        """
        # create list of keys
        if key_list == None:
            key_list = []
            for i in range(0, len(state_list)):
                key_val = Covid19_Data.create_key(state_list[i], county_list[i])
                key_list.append(key_val)

        start_dates = []
        end_dates = []
        
        x_datasets = []
        y_datasets = []
        labels = []
        
        
        for key_val in key_list:
            if key_val in self.__time_series_data["INCIDENT RATE"]:
                x = self.__time_series_dates
                datemin = datetime.date(x[0].year, x[0].month, 1)
                datemax = datetime.date(x[len(x)-1].year, x[len(x)-1].month + 1, 1)

                y = self.__time_series_data["PEOPLE TESTED"][key_val].copy()
                
                start_dates.append(datemin)
                end_dates.append(datemax)
                
                x_datasets.append(x)
                y_datasets.append(y)
                labels.append(key_val)
            else:
                print("invalid state / county pair value: ", key_val)
                return(False)

        integer_to_dates_table, dates_to_integer_table = self.create_lookup_tables(min(start_dates), max(end_dates))
        
        integer_x_datasets = []  # convert dataset x axis from dates to integers using lookup table
        for x_dataset in x_datasets:
            dataset = []
            for x in x_dataset:
                dataset.append(dates_to_integer_table.get(x.strftime("%m-%d-%Y")))
            integer_x_datasets.append(dataset)
            
        gui = matplotlib_gui.MatplotlibGUI(integer_to_dates_table, "Date", "People Tested")
        gui.new_figure(1, 1)

        gui.add_dataset(integer_x_datasets, y_datasets, labels)
        while gui.mainloop(): pass 
    

    def plot_new_people_tested_data(self, state_list, county_list, key_list):
        """Description: function to create an XY plot of specified state/county pairs
        Inputs: 
            state_list - optional, list of states in state / county pair list (ignored if key_list is not None)
            county_list - optional, list of counties in state / county pair list (ignored if key_list is not None)
            key_list - optional, list of key values ("State, County") to plot data for
        Outpus:
            A plot window is opened
        """
        # create list of keys
        if key_list == None:
            key_list = []
            for i in range(0, len(state_list)):
                key_val = Covid19_Data.create_key(state_list[i], county_list[i])
                key_list.append(key_val)

        start_dates = []
        end_dates = []
        
        x_datasets = []
        y_datasets = []
        labels = []

        for key_val in key_list:
            if key_val in self.__time_series_data["PEOPLE TESTED"]:
                [x, y] = self.get_daily_new_people_tested(state=None, county=None, key=key_val)
                datemin = datetime.date(x[0].year, x[0].month, 1)
                datemax = datetime.date(x[len(x)-1].year, x[len(x)-1].month + 1, 1)

                start_dates.append(datemin)
                end_dates.append(datemax)
                
                x_datasets.append(x)
                y_datasets.append(y)
                labels.append(key_val)
            else:
                print("invalid state / county pair value: ", key_val)
                return(False)

        integer_to_dates_table, dates_to_integer_table = self.create_lookup_tables(min(start_dates), max(end_dates))
        
        integer_x_datasets = []  # convert dataset x axis from dates to integers using lookup table
        for x_dataset in x_datasets:
            dataset = []
            for x in x_dataset:
                dataset.append(dates_to_integer_table.get(x.strftime("%m-%d-%Y")))
            integer_x_datasets.append(dataset)
            
        gui = matplotlib_gui.MatplotlibGUI(integer_to_dates_table, "Date", "Daily Number of People Tested", "Daily New People Tested")
        gui.new_figure(1, 1)

        gui.add_dataset(integer_x_datasets, y_datasets, labels)
        while gui.mainloop(): pass 
    

    def plot_daily_ratio_cases_to_people_tested_data(self, country_list, state_list, county_list):
        """Description: function to create an XY plot of specified state/county pairs
        Inputs: 
            country_list - list of countries in country / state / county path
            state_list - optional, list of states in country / state / county path
            county_list - optional, list of counties in country / state / county path
        Outpus:
            A plot window is opened
        """
        start_dates = []
        end_dates = []
        
        x_datasets = []
        y_datasets = []
        labels = []


        for i in range(0, len(country_list)):
            country_node = self.time_series_data_tree.get_child_node(country_list[i])
            if (country_node == None):
                print("ERROR: plot_cases_data - invalid country: ", country_list[i])
                return(False)
            state_node = country_node.get_child_node(state_list[i])
            if (state_node == None):
                plot_node = country_node
                label_string = country_list[i] + " - All"
            else:
                county_node = state_node.get_child_node(county_list[i])                    
                if (county_node == None):
                    plot_node = state_node
                    label_string = country_list[i] + ", " + state_list[i] + " - All"
                else:
                    plot_node = county_node
                    label_string = country_list[i] + ", " + state_list[i] + ", " + county_list[i]
            
            if plot_node.confirmed_cases_time_series_data and plot_node.people_tested_time_series_data:
                x = self.time_series_dates
                ratio = plot_node.get_daily_ratio_confirmed_cases_to_people_tested()
                    
                datemin = datetime.date(x[0].year, x[0].month, 1)
                datemax = datetime.date(x[len(x)-1].year, x[len(x)-1].month + 1, 1)

                start_dates.append(datemin)
                end_dates.append(datemax)
                
                x_datasets.append(x)
                y_datasets.append(ratio)
                labels.append(label_string)
                
            else:
                print("invalid country / state / county node value: ", country_list[i], state_list[i], county_list[i])
                return(False)

        integer_to_dates_table, dates_to_integer_table = self.create_lookup_tables(min(start_dates), max(end_dates))
        
        integer_x_datasets = []  # convert dataset x axis from dates to integers using lookup table
        for x_dataset in x_datasets:
            dataset = []
            for x in x_dataset:
                dataset.append(dates_to_integer_table.get(x.strftime("%m-%d-%Y")))
            integer_x_datasets.append(dataset)
            
        gui = matplotlib_gui.MatplotlibGUI(integer_to_dates_table, "Date", "Daily Ratio of Confirmed Cases to People Tested", "Percentage of Positive Test Results")
        gui.new_figure(1, 1)

        gui.add_dataset(integer_x_datasets, y_datasets, labels)
        while gui.mainloop(): pass 
