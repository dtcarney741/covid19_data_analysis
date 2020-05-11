import csv
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

class Covid19_Data(object):  
    
    def __init__(self):
        """Description: Reads a DSM spreadsheet tab into a DSM data structure
        Inputs: None
        Outputs: Initializes data structures
        """
        self.__time_series_dates = []
        data_values = {
            "CONFIRMED CASES" : {},
            "DEATHS" : {},
            "PEOPLE TESTED" : {},
            "INCIDENT RATE": {}
            }
        self.__time_series_data = data_values
        # initialize header to cell map values in time series data file (-1 for unknown)"""
        self.__time_series_field_locations = {
            "HEADER_ROW": -1,
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
                        return(False)
                    else:
                        date_list = []
                        for col in range(self.__time_series_field_locations["FIRST_DATE_COL"], self.__time_series_field_locations["LAST_DATE_COL"] + 1):
                            date_list.append(datetime.datetime.strptime(row[col],'%m/%d/%y'))
                            
                        # TODO: date list should already be initialized, so no need to do this here - need to add initialize code
                        self.__time_series_dates = date_list
                        header_row_found = True
            else:
                state = row[self.__time_series_field_locations["STATE_NAME_COL"]]
                county = row[self.__time_series_field_locations["COUNTY_NAME_COL"]]
                key = self.__create_key(state, county)
                    
                # add state,county to the dictionary if not already in there data to the dictionary if it's in there
                if key not in self.__time_series_data["CONFIRMED CASES"]:
                    # initialize cases data list for each corresponding date
                    cases = []
                    for date in self.__time_series_dates:
                        cases.append(None)
                    self.__time_series_data["CONFIRMED CASES"][key] = cases
                    agg_key = state + ", ALL"
                    # add the aggregate state entry to the dictionary if not already in there
                    if agg_key not in self.__time_series_data["CONFIRMED CASES"]:
                        # initialize cases data list for each corresponding date
                        cases = []
                        for date in self.__time_series_dates:
                            cases.append(None)

                        self.__time_series_data["CONFIRMED CASES"][agg_key] = cases

                # add data to the apprpriate entry in the dictionary for state/county and aggregate for whole state
                agg_key = state + ", ALL"
                i = 0
                for col in range(self.__time_series_field_locations["FIRST_DATE_COL"], self.__time_series_field_locations["LAST_DATE_COL"] + 1):
                    j = self.__get_date_list_index(date_list[i])
                    self.__time_series_data["CONFIRMED CASES"][key][j] = int(row[col])
                    
                    if self.__time_series_data["CONFIRMED CASES"][agg_key][j] == None:
                        self.__time_series_data["CONFIRMED CASES"][agg_key][j] = int(row[col])
                    else:
                        self.__time_series_data["CONFIRMED CASES"][agg_key][j] = self.__time_series_data["CONFIRMED CASES"][agg_key][j] + int(row[col])

                    i = i + 1

            row_count = row_count + 1

        csv_file_obj.close()
        return(header_row_found)

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
                        state = row[self.__us_data_field_locations["STATE_NAME_COL"]]
                        key = self.__create_key(state, "ALL")
                            
                        # add state,county to the dictionary if not already in there data to the dictionary if it's in there
                        if key not in self.__time_series_data["CONFIRMED CASES"]:
                            # initialize cases data list for each corresponding date
                            cases = []
                            for date in self.__time_series_dates:
                                cases.append(None)
                            self.__time_series_data["CONFIRMED CASES"][key] = cases
                        if key not in self.__time_series_data["DEATHS"]:
                            # initialize cases data list for each corresponding date
                            deaths = []
                            for date in self.__time_series_dates:
                                deaths.append(None)
                            self.__time_series_data["DEATHS"][key] = deaths
                        if key not in self.__time_series_data["PEOPLE TESTED"]:
                            # initialize cases data list for each corresponding date
                            tested = []
                            for date in self.__time_series_dates:
                                tested.append(None)
                            self.__time_series_data["PEOPLE TESTED"][key] = tested
                        if key not in self.__time_series_data["INCIDENT RATE"]:
                            # initialize cases data list for each corresponding date
                            rate = []
                            for date in self.__time_series_dates:
                                rate.append(None)
                            self.__time_series_data["INCIDENT RATE"][key] = rate
                            
                        # add data to the apprpriate entry in the dictionary for state/county and aggregate for whole state
                        i = self.__get_date_list_index(file_date_val)
                        try:
                            cases = int(row[self.__us_data_field_locations["CONFIRMED_CASES_COL"]])
                        except:
                            cases = 0
                        try:
                            deaths = int(row[self.__us_data_field_locations["DEATHS"]])
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
                        self.__time_series_data["CONFIRMED CASES"][key][i] = cases
                        self.__time_series_data["DEATHS"][key][i] = deaths
                        self.__time_series_data["PEOPLE TESTED"][key][i] = tested
                        self.__time_series_data["INCIDENT RATE"][key][i] = rate
    
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
        self.__time_series_field_locations["STATE_NAME_COL"] = -1
        self.__time_series_field_locations["COUNTY_NAME_COL"] = -1
        self.__time_series_field_locations["FIRST_DATE_COL"] = -1
        self.__time_series_field_locations["LAST_DATE_COL"] = -1

        i = 0
        while not found_everything and i < 1000:
            if row[i].upper() == "ADMIN2":
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

    def __create_key(self,state, county):
        """Desccrition: Function to create a key value for data structure dictionaries
        Inputs: state - string containing name of state to create key for
                county - string containing name of county ot create key for
        Outputs:
                return - key value
        """
        key = state + ", " + county
        return(key)

    def __get_date_list_index(self,date):
        """Description: Returns the list index of a specified date in the time series dates list
        Inputs:
            date - the date to find the index of in self.__time_series_dates
        Outputs:
          return - index of the specified date in the date list (-1 if not found)
        """
        date_index = -1
        i = 0
        for search_date in self.__time_series_dates:
            if date == search_date:
                return(i)
            i = i + 1
        return(date_index)
       
    def get_cases(self,state, county):
        """Description: Accessor function to get cases data for a specified state and county
        Inputs:
            state - the state to retrieve cases data for
            county - the county to retrieve cases data for ("ALL" for aggregate of all counties)
        Outputs:
          return - [[date], [cases]] or None of invalid state / county
        """
        key = self.__create_key(state, county)
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
            key = self.__create_key(state, county)

        dates = []
        new_cases = []
        if key in self.__time_series_data["CONFIRMED CASES"]:
            for i in range (1, len(self.__time_series_dates)):
                dates.append(self.__time_series_dates[i])
                if self.__time_series_data["CONFIRMED CASES"][key][i] != None:
                    if self.__time_series_data["CONFIRMED CASES"][key][i-1] != None:
                        new_case_val = self.__time_series_data["CONFIRMED CASES"][key][i] - self.__time_series_data["CONFIRMED CASES"][key][i-1]
                    else:
                        new_case_val = self.__time_series_data["CONFIRMED CASES"][key][i]
                else:
                    new_case_val = None
                new_cases.append(new_case_val)
            return([dates,new_cases])
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
            key = self.__create_key(state, county)

        dates = []
        new_cases = []
        if key in self.__time_series_data["PEOPLE TESTED"]:
            for i in range (1, len(self.__time_series_dates)):
                dates.append(self.__time_series_dates[i])
                if self.__time_series_data["PEOPLE TESTED"][key][i] != None:
                    if self.__time_series_data["PEOPLE TESTED"][key][i-1] != None:
                        new_case_val = self.__time_series_data["PEOPLE TESTED"][key][i] - self.__time_series_data["PEOPLE TESTED"][key][i-1]
                    else:
                        new_case_val = self.__time_series_data["PEOPLE TESTED"][key][i]
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
        for date in self.__time_series_dates:
            dates.append(date)
        return(dates)

    def get_people_tested(self,state,county,key):
        """Description: Accessor function to get list of dates for data points
        Inputs: None
        Outputs:
          return - [dates]
        """
        if key == None:
            key = self.__create_key(state,county)

        data = []
        for val in self.__time_series_data["PEOPLE TESTED"][key]:
            data.append(val)
        return(data)
      
    def plot_cases_data(self, state_list, county_list, key_list):
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
                key_val = self.__create_key(state_list[i], county_list[i])
                key_list.append(key_val)
       
        fig, ax = plt.subplots()
        for key_val in key_list:
            if key_val in self.__time_series_data["CONFIRMED CASES"]:
                x = self.__time_series_dates
                datemin = datetime.date(x[0].year, x[0].month, 1)
                datemax = datetime.date(x[len(x)-1].year, x[len(x)-1].month + 1, 1)

                y = self.__time_series_data["CONFIRMED CASES"][key_val]
            else:
                print("invalid state / county pair value: ", key_val)
                return(False)
            ax.plot(x,y, marker='o', label=key_val)

        # format the ticks
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m'))
#        ax.xaxis.set_minor_locator(mdates.DayLocator())
        ax.set_xlim(datemin, datemax)

        ax.set_xlabel('Date')
        ax.set_ylabel('Confirmed Cases')               
        # format the coords message box
        ax.format_xdata = mdates.DateFormatter('%m-%d-%Y')
        ax.grid(True)
        
        ax.legend()

        fig.suptitle('Covid-19 Confirmed Cases Plot')
        
        # rotates and right aligns the x labels, and moves the bottom of the
        # axes up to make room for them
        fig.autofmt_xdate()

        plt.show()    
        
        
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
                key_val = self.__create_key(state_list[i], county_list[i])
                key_list.append(key_val)

        fig, ax = plt.subplots()
        for key_val in key_list:
            if key_val in self.__time_series_data["CONFIRMED CASES"]:
                [x, y] = self.get_daily_new_cases(state=None, county=None, key=key_val)
                datemin = datetime.date(x[0].year, x[0].month, 1)
                datemax = datetime.date(x[len(x)-1].year, x[len(x)-1].month + 1, 1)

            else:
                print("invalid state / county pair value: ", key_val)
                return(False)
            ax.plot(x,y, marker='o', label=key_val)

        # format the ticks
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m'))
#        ax.xaxis.set_minor_locator(mdates.DayLocator())
        ax.set_xlim(datemin, datemax)

        ax.set_xlabel('Date')
        ax.set_ylabel('Confirmed Cases')               
        # format the coords message box
        ax.format_xdata = mdates.DateFormatter('%m-%d-%Y')
        ax.grid(True)
        
        ax.legend()

        fig.suptitle('Covid-19 Daily New Cases Plot')
        
        # rotates and right aligns the x labels, and moves the bottom of the
        # axes up to make room for them
        fig.autofmt_xdate()

        plt.show()    
        
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
                key_val = self.__create_key(state_list[i], county_list[i])
                key_list.append(key_val)

        fig, ax = plt.subplots()
        for key_val in key_list:
            if key_val in self.__time_series_data["INCIDENT RATE"]:
                x = self.__time_series_dates
                datemin = datetime.date(x[0].year, x[0].month, 1)
                datemax = datetime.date(x[len(x)-1].year, x[len(x)-1].month + 1, 1)

                y = self.__time_series_data["INCIDENT RATE"][key_val].copy()
            else:
                print("invalid state / county pair value: ", key_val)
                return(False)
            ax.plot(x,y, marker='o', label=key_val)

        # format the ticks
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m'))
#        ax.xaxis.set_minor_locator(mdates.DayLocator())
        ax.set_xlim(datemin, datemax)

        ax.set_xlabel('Date')
        ax.set_ylabel('Confirmed Cases per 100000 Population')               
        # format the coords message box
        ax.format_xdata = mdates.DateFormatter('%m-%d-%Y')
        ax.grid(True)
        
        ax.legend()
        
        fig.suptitle('Covid-19 Incident Rate Plot')

        # rotates and right aligns the x labels, and moves the bottom of the
        # axes up to make room for them
        fig.autofmt_xdate()

        plt.show()    

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
                key_val = self.__create_key(state_list[i], county_list[i])
                key_list.append(key_val)

        fig, ax = plt.subplots()
        for key_val in key_list:
            if key_val in self.__time_series_data["INCIDENT RATE"]:
                x = self.__time_series_dates
                datemin = datetime.date(x[0].year, x[0].month, 1)
                datemax = datetime.date(x[len(x)-1].year, x[len(x)-1].month + 1, 1)

                y = self.__time_series_data["PEOPLE TESTED"][key_val].copy()
            else:
                print("invalid state / county pair value: ", key_val)
                return(False)
            ax.plot(x,y, marker='o', label=key_val)

        # format the ticks
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m'))
#        ax.xaxis.set_minor_locator(mdates.DayLocator())
        ax.set_xlim(datemin, datemax)

        ax.set_xlabel('Date')
        ax.set_ylabel('Number of People Tested')
        # format the coords message box
        ax.format_xdata = mdates.DateFormatter('%m-%d-%Y')
        ax.grid(True)
        
        ax.legend()
        
        fig.suptitle('Covid-19 People Tested Plot')

        # rotates and right aligns the x labels, and moves the bottom of the
        # axes up to make room for them
        fig.autofmt_xdate()

        plt.show()    

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
                key_val = self.__create_key(state_list[i], county_list[i])
                key_list.append(key_val)

        fig, ax = plt.subplots()
        for key_val in key_list:
            if key_val in self.__time_series_data["PEOPLE TESTED"]:
                [x, y] = self.get_daily_new_people_tested(state=None, county=None, key=key_val)
                datemin = datetime.date(x[0].year, x[0].month, 1)
                datemax = datetime.date(x[len(x)-1].year, x[len(x)-1].month + 1, 1)

            else:
                print("invalid state / county pair value: ", key_val)
                return(False)
            ax.plot(x,y, marker='o', label=key_val)

        # format the ticks
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m'))
#        ax.xaxis.set_minor_locator(mdates.DayLocator())
        ax.set_xlim(datemin, datemax)

        ax.set_xlabel('Date')
        ax.set_ylabel('Daily Number of People Tested')
        # format the coords message box
        ax.format_xdata = mdates.DateFormatter('%m-%d-%Y')
        ax.grid(True)
        
        ax.legend()

        fig.suptitle('Covid-19 Daily New People Tested Plot')
        
        # rotates and right aligns the x labels, and moves the bottom of the
        # axes up to make room for them
        fig.autofmt_xdate()

        plt.show()    

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
                key_val = self.__create_key(state_list[i], county_list[i])
                key_list.append(key_val)

        fig, ax = plt.subplots()
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

            else:
                print("invalid state / county pair value: ", key_val)
                return(False)
            ax.plot(x,ratio, marker='o', label=key_val)

        # format the ticks
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m'))
#        ax.xaxis.set_minor_locator(mdates.DayLocator())
        ax.set_xlim(datemin, datemax)

        ax.set_xlabel('Date')
        ax.set_ylabel('Daily Ratio of Confirmed Cases to People Tested')
        # format the coords message box
        ax.format_xdata = mdates.DateFormatter('%m-%d-%Y')
        ax.grid(True)
        
        ax.legend()

        fig.suptitle('Covid-19 Percentage of Positive Test Results')
        
        # rotates and right aligns the x labels, and moves the bottom of the
        # axes up to make room for them
        fig.autofmt_xdate()

        plt.show()    
