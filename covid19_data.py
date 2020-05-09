import csv
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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
            "STATE_NAME_COL": -1,
            "CONFIRMED_CASES_COL": -1,
            "DEATHS_COL": -1,
            "PEOPLE_TESTED_COL": -1,
            "INCIDENT_RATE_COL": -1
            }

         
    def read_time_series_cases_data(self, filename):
        """Description: Reads the Johns Hopkins COVID-19 time series CSV file a DSM spreadsheet tab into a DSM data structure
        Inputs:
            filename - string with name and path of file to be opened
        Outputs:
          self.__time_series_field_locations - updated dictionary with locations added
          self.__time_series_cases_data - dictionary containing the time series data that was read in, organized as:
                                    {state 1, county 1: time_series[date[], cases[]]
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
                key =  state + ", " + county
                    
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
        self.__us_data_field_locations["STATE_NAME_COL"] = -1
        self.__us_data_field_locations["CONFIRMED_CASES_COL"] = -1
        self.__us_data_field_locations["DEATHS_COL"] = -1
        self.__us_data_field_locations["PEOPLE_TESTED_COL"] = -1
        self.__us_data_field_locations["INCIDENT_RATE_COL"] = -1

        i = 0
        while not found_everything and i < 1000:
            if row[i].upper() == "PROVINCE_STATE":
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

    def get_state_county_cases_keys(self):
        """Description: Accessor function to get all of the state and counties in the confirmed cases dictionary
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
        """Description: Accessor function to get all the keys in the confirmed cases dictionary
        Inputs: None
        Outputs:
          return - [keys]
        """
        keys = []
        for key in self.__time_series_data["CONFIRMED CASES"]:
            keys.append(key)
        return(keys)
        
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
        
        # rotates and right aligns the x labels, and moves the bottom of the
        # axes up to make room for them
        fig.autofmt_xdate()

        plt.show()    