import csv
import datetime
import os

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
            children_list.append(child)
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

    
class Covid19_Data(object):  
    
    def __init__(self):
        """Description: Reads a DSM spreadsheet tab into a DSM data structure
        Inputs: None
        Outputs: Initializes data structures
        """
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
            "COUNTRY_COL": -1,
            "STATE_NAME_COL": -1,
            "CONFIRMED_CASES_COL": -1,
            "DEATHS_COL": -1,
            "PEOPLE_TESTED_COL": -1,
            "INCIDENT_RATE_COL": -1
            }

         
    def read_time_series_cases_data(self, filename):
        """Description: Reads the Johns Hopkins COVID-19 time series CSV file into the time_series_data dictionary
        Inputs:
            filename - string with name and path of file to be opened
        Outputs:
          self.__time_series_field_locations - updated dictionary with locations added
          self.__time_series_data - dictionary containing the time series data that was read in, organized as:
                                    {"CONFIRMED CASES": {state 1, county 1}:cases[],
                                                        {state 1, county 2}:cases[],
                                     ...}
          return - True if successful, false if not
        """
        csv_file_obj = open(filename)
        reader_obj = csv.reader(csv_file_obj)
        header_row_found = False
        row_count = 1
        for row in reader_obj:
            if header_row_found == False:
                if row[0].upper() == "UID":
                    if not self.__map_time_series_locations(row, row_count):
                        print("ERROR: read_time_series_cases_data - invalid data file")
                        return False
                    else:
                        date_list = []
                        for col in range(self.__time_series_field_locations["FIRST_DATE_COL"], self.__time_series_field_locations["LAST_DATE_COL"] + 1):
                            date_list.append(datetime.datetime.strptime(row[col],'%m/%d/%y'))
                            
                        # TODO: date list should already be initialized, so no need to do this here - need to add initialize code
                        self.time_series_dates = date_list
                        header_row_found = True
            else:
                country = row[self.__time_series_field_locations["COUNTRY_NAME_COL"]]
                state = row[self.__time_series_field_locations["STATE_NAME_COL"]]
                county = row[self.__time_series_field_locations["COUNTY_NAME_COL"]]
                # add the country to the base tree if it's not already there
                country_node = self.time_series_data_tree.get_child_node(country)
                if country_node == None:
                    country_node = Covid19_Tree_Node(country)
                    self.time_series_data_tree.add_child(country_node)
                    country_node.initialize_confirmed_cases(len(self.time_series_dates))

                # add the state to the country tree node if it's not already there
                state_node = country_node.get_child_node(state)
                if state_node == None:
                    state_node = Covid19_Tree_Node(state)
                    country_node.add_child(state_node)
                    state_node.initialize_confirmed_cases(len(self.time_series_dates))
                
                # add the county to the state tree node if it's not already there (if it is already there that is an error condition because the same county should not be encountered twice in the data)
                county_node = state_node.get_child_node(county)
                if county_node == None:
                    county_node = Covid19_Tree_Node(county)
                    state_node.add_child(county_node)
                    county_node.initialize_confirmed_cases(len(self.time_series_dates))
                else:
                    print("ERROR: read_time_series_cases_data - duplicate county found")
                    return False
                    
                # add data to the apprpriate entry in the dictionary for state/county and aggregate for whole state, and aggregate for whole country
                i = 0
                for col in range(self.__time_series_field_locations["FIRST_DATE_COL"], self.__time_series_field_locations["LAST_DATE_COL"] + 1):
                    j = self.time_series_dates.index(date_list[i])
                    county_node.confirmed_cases_time_series_data[j] = int(float(row[col]))
                    
                    if state_node.confirmed_cases_time_series_data[j] == None:
                        state_node.confirmed_cases_time_series_data[j] = int(float(row[col]))
                    else:
                        state_node.confirmed_cases_time_series_data[j] = state_node.confirmed_cases_time_series_data[j] + int(row[col])

                    if country_node.confirmed_cases_time_series_data[j] == None:
                        country_node.confirmed_cases_time_series_data[j] = int(float(row[col]))
                    else:
                        country_node.confirmed_cases_time_series_data[j] = country_node.confirmed_cases_time_series_data[j] + int(float(row[col]))
                    i = i + 1

            row_count = row_count + 1

        csv_file_obj.close()
        return header_row_found

    def read_us_daily_reports_data(self, folder):
        """Description: Reads the Johns Hopkins COVID-19 daily report CSV file into the time_series_data dictionary
        Inputs:
            folder - string with path of daily report files to be opened
        Outputs:
          self.__us_data_field_locations - updated dictionary with locations added
          self.__time_series_data - dictionary containing the time series data that was read in, organized as:
                                    {"CONFIRMED CASES": {state 1, county 1}:cases[],
                                                        {state 1, county 2}:cases[],
                                     ...}
          return - True if successful, false if not
        """
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
                header_row_found = False
                row_count = 1
                for row in reader_obj:
                    if header_row_found == False:
                        if not self.__map_us_data_locations(row, row_count):
                            return(False)
                        else:
                            header_row_found = True
                    elif row[self.__us_data_field_locations["COUNTRY_COL"]].upper() == "US":
                        # only import data for US (since this is the US daily reports you would expect this to always be true, but 
                        # some of the Johns Hopkins daily report files in the US folder have other countries mixed in
                        country = row[self.__us_data_field_locations["COUNTRY_COL"]]
                        state = row[self.__us_data_field_locations["STATE_NAME_COL"]]

                        # add the country to the base tree if it's not already there
                        country_node = self.time_series_data_tree.get_child_node(country)
                        if country_node == None:
                            country_node = Covid19_Tree_Node(country)
                            self.time_series_data_tree.add_child(country_node)
                            country_node.initialize_confirmed_cases(len(self.time_series_dates))
                            country_node.initialize_deaths(len(self.time_series_dates))
                            country_node.initialize_people_tested(len(self.time_series_dates))
                            country_node.initialize_incident_rate(len(self.time_series_dates))
                        else:
                            #check to make sure all data series for the country have been initialized
                            if not country_node.confirmed_cases_time_series_data:
                                country_node.initialize_confirmed_cases(len(self.time_series_dates))
                            if not country_node.deaths_time_series_data:
                                country_node.initialize_deaths(len(self.time_series_dates))
                            if not country_node.people_tested_time_series_data:
                                country_node.initialize_people_tested(len(self.time_series_dates))
                            if not country_node.incident_rate_time_series_data:
                                country_node.initialize_incident_rate(len(self.time_series_dates))

                        # add the state to the country tree node if it's not already there
                        state_node = country_node.get_child_node(state)
                        if state_node == None:
                            state_node = Covid19_Tree_Node(state)
                            country_node.add_child(state_node)
                            for date in self.time_series_dates:
                                state_node.confirmed_cases_time_series_data.append(None)
                                state_node.deaths_time_series_data.append(None)
                                state_node.people_tested_time_series_data.append(None)
                                state_node.incident_rate_time_series_data.append(None)
                        else:
                            #check to make sure all data series for the state have been initialized
                            if not state_node.confirmed_cases_time_series_data:
                                state_node.initialize_confirmed_cases(len(self.time_series_dates))
                            if not state_node.deaths_time_series_data:
                                state_node.initialize_deaths(len(self.time_series_dates))
                            if not state_node.people_tested_time_series_data:
                                state_node.initialize_people_tested(len(self.time_series_dates))
                            if not state_node.incident_rate_time_series_data:
                                state_node.initialize_incident_rate(len(self.time_series_dates))
                            
                        # add data to the appropriate data array for the state
                        i = self.time_series_dates.index(file_date_val)
                        try:
                            cases = int(row[self.__us_data_field_locations["CONFIRMED_CASES_COL"]])
                        except:
                            cases = 0
                        try:
                            deaths = int(row[self.__us_data_field_locations["DEATHS_COL"]])
                        except:
                            deaths = 0
                        try:
                            tested = int(row[self.__us_data_field_locations["PEOPLE_TESTED_COL"]])
                        except:
                            tested = 0
                        try:
                            rate = float(row[self.__us_data_field_locations["INCIDENT_RATE_COL"]])
                        except:
                            rate = 0
                        state_node.confirmed_cases_time_series_data[i] = cases
                        state_node.deaths_time_series_data[i] = deaths
                        state_node.people_tested_time_series_data[i] = tested
                        state_node.incident_rate_time_series_data[i] = rate

                        # aggregate the state data into the data array for the country
                        if country_node.confirmed_cases_time_series_data[i] == None:
                            country_node.confirmed_cases_time_series_data[i] = cases
                            #todo handle situation where confirmed cases data is already present (overwrite it, skip, etc.)
                        if country_node.deaths_time_series_data[i] == None:
                            country_node.deaths_time_series_data[i] = deaths
                        else:
                            country_node.deaths_time_series_data[i] = country_node.deaths_time_series_data[i] + deaths
                        if country_node.people_tested_time_series_data[i] == None:
                            country_node.people_tested_time_series_data[i] = tested
                        else:
                            country_node.people_tested_time_series_data[i] = country_node.people_tested_time_series_data[i] + tested
                        if country_node.incident_rate_time_series_data[i] == None:
                            country_node.incident_rate_time_series_data[i] = rate
                        else:
                            country_node.incident_rate_time_series_data[i] = country_node.incident_rate_time_series_data[i] + rate

                    row_count = row_count + 1
    
                csv_file_obj.close()   
                 
        return(True)
       
        
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
        while not found_everything and i < 1000:
            if row[i].upper() == "COUNTRY_REGION":
                self.__time_series_field_locations["COUNTRY_NAME_COL"] = i
                self.__time_series_field_locations["HEADER_ROW"] = row_num
            elif row[i].upper() == "ADMIN2":
                self.__time_series_field_locations["COUNTY_NAME_COL"] = i
                self.__time_series_field_locations["HEADER_ROW"] = row_num
            elif row[i].upper() == "PROVINCE_STATE":
                self.__time_series_field_locations["STATE_NAME_COL"] = i
                self.__time_series_field_locations["HEADER_ROW"] = row_num
            elif row[i].upper() == "COMBINED_KEY":
                self.__time_series_field_locations["FIRST_DATE_COL"] = i+1
                self.__time_series_field_locations["LAST_DATE_COL"] = len(row)-1
                self.__time_series_field_locations["HEADER_ROW"] = row_num
            i = i + 1

            found_everything = True
            for x in self.__time_series_field_locations:
                if self.__time_series_field_locations[x] == -1:
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
        self.__us_data_field_locations["COUNTRY_COL"] = -1
        self.__us_data_field_locations["STATE_NAME_COL"] = -1
        self.__us_data_field_locations["CONFIRMED_CASES_COL"] = -1
        self.__us_data_field_locations["DEATHS_COL"] = -1
        self.__us_data_field_locations["PEOPLE_TESTED_COL"] = -1
        self.__us_data_field_locations["INCIDENT_RATE_COL"] = -1

        i = 0
        while not found_everything and i < 1000:
            if row[i].upper() == "COUNTRY_REGION":
                self.__us_data_field_locations["COUNTRY_COL"] = i
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

            i = i + 1

            found_everything = True
            for x in self.__us_data_field_locations:
                if self.__us_data_field_locations[x] == -1:
                    found_everything = False
                    self.__us_data_field_locations["HEADER_ROW"] = -1

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
        """Description: Accessor function to get list of dates for data points
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

        
    def plot_deaths_data(self, state_list, county_list, key_list):
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
                x = self.__time_series_dates
                
                datemin = datetime.date(x[0].year, x[0].month, 1)
                datemax = datetime.date(x[len(x)-1].year, x[len(x)-1].month + 1, 1)
                start_dates.append(datemin)
                end_dates.append(datemax)
                y = self.__time_series_data["DEATHS"][key_val]
                
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
    

    def plot_daily_ratio_cases_to_people_tested_data(self, state_list, county_list, key_list):
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
                [x, cases] = self.get_daily_new_cases(state=None, county=None, key=key_val)
                [x, tested] = self.get_daily_new_people_tested(state=None, county=None, key=key_val)
                ratio = []
                for i in range(0,len(x)):
                    if cases[i] == None or tested[i] == None:
                        ratio.append(None)
                    elif tested[i] == 0:
                        ratio.append(None)
                    else:
                        ratio.append(cases[i]/tested[i])
                    
                datemin = datetime.date(x[0].year, x[0].month, 1)
                datemax = datetime.date(x[len(x)-1].year, x[len(x)-1].month + 1, 1)

                start_dates.append(datemin)
                end_dates.append(datemax)
                
                x_datasets.append(x)
                y_datasets.append(ratio)
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
            
        gui = matplotlib_gui.MatplotlibGUI(integer_to_dates_table, "Date", "Daily Ratio of Confirmed Cases to People Tested", "Percentage of Positive Test Results")
        gui.new_figure(1, 1)

        gui.add_dataset(integer_x_datasets, y_datasets, labels)
        while gui.mainloop(): pass 
