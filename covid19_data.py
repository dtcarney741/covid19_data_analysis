from collections import Counter
import csv
import networkx as nx
import datetime
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Arc

class Covid19_Data(object):  
    
    def __init__(self):
        """Description: Reads a DSM spreadsheet tab into a DSM data structure
        Inputs: None
        Outputs: Initializes data structures
        """
        self.__time_series_cases_data = {}
        self.__time_series_deaths_data = {}
        # initialize header to cell map values in formation (row,col) ((-1,-1) for unknown)"""
        self.__field_locations = {
            "HEADER_ROW": -1,
            "STATE_NAME_COL": -1,
            "COUNTY_NAME_COL": -1,
            "FIRST_DATE_COL": -1,
            "LAST_DATE_COL": -1
        }

         
    def read_time_series_cases_data(self, filename):
        """Description: Reads the Johns Hopkins COVID-19 time series CSV file a DSM spreadsheet tab into a DSM data structure
        Inputs:
            filename - string with name and path of file to be opened
        Outputs:
          self.__field_locations - updated dictionary with locations added
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
                    if not self.__map_locations(row, row_count):
                        return(False)
                    else:
                        date_list = []
                        for col in range(self.__field_locations["FIRST_DATE_COL"], self.__field_locations["LAST_DATE_COL"] + 1):
                            date_list.append(datetime.datetime.strptime(row[col],'%m/%d/%y'))
                        header_row_found = True
            else:
                state = row[self.__field_locations["STATE_NAME_COL"]]
                county = row[self.__field_locations["COUNTY_NAME_COL"]]
                key =  state + ", " + county
                    
                # add state,county to the dictionary if not already in there data to the dictionary if it's in there
                if key not in self.__time_series_cases_data:
                    date = []
                    cases = []
                    self.__time_series_cases_data[key] = [date, cases]
                    agg_key = state + ", ALL"
                    # add the aggregate state entry to the dictionary if not already in there
                    if agg_key not in self.__time_series_cases_data:
                        date = []
                        cases = []
                        self.__time_series_cases_data[agg_key] = [date, cases]

                # add data to the apprpriate entry in the dictionary
                self.__time_series_cases_data[key][0] = date_list
                for col in range(self.__field_locations["FIRST_DATE_COL"], self.__field_locations["LAST_DATE_COL"] + 1):
                    self.__time_series_cases_data[key][1].append(int(row[col]))

                # update aggregate state data
                agg_key = state + ", ALL"
                if agg_key in self.__time_series_cases_data:
                    if len(self.__time_series_cases_data[agg_key][0]) == 0:
                        # first time this state has been encountered, so need to add entries to the list
                        self.__time_series_cases_data[agg_key][0] = date_list
                        first_time_for_state = True
                    else:
                        first_time_for_state = False
                    i = 0
                    for col in range(self.__field_locations["FIRST_DATE_COL"], self.__field_locations["LAST_DATE_COL"] + 1):
                        if first_time_for_state == True:
                            self.__time_series_cases_data[agg_key][1].append(int(row[col]))
                        else:
                            self.__time_series_cases_data[agg_key][1][i] = self.__time_series_cases_data[agg_key][1][i] + int(row[col])
                            i = i + 1
            row_count = row_count + 1

        csv_file_obj.close()
        return(header_row_found)
        
    def __map_locations(self,row, row_num):
        """Description: Fills in the dictionary of locations with the associated row and column index
        Inputs:
            row - the comma separated row list to check for header columns
            row_num - the current row number
        Outputs:
          self.__field_locations - updated dictionary with locations added
          return - True if all locations found, false if not
        """
        found_everything = False
        i = 0
        while not found_everything and i < 1000:
            if row[i].upper() == "ADMIN2":
                self.__field_locations["COUNTY_NAME_COL"] = i
                self.__field_locations["HEADER_ROW"] = row_num
            elif row[i].upper() == "PROVINCE_STATE":
                self.__field_locations["STATE_NAME_COL"] = i
                self.__field_locations["HEADER_ROW"] = row_num
            elif row[i].upper() == "COMBINED_KEY":
                self.__field_locations["FIRST_DATE_COL"] = i+1
                self.__field_locations["LAST_DATE_COL"] = len(row)-1
                self.__field_locations["HEADER_ROW"] = row_num
            i = i + 1

            found_everything = True
            for x in self.__field_locations:
                if self.__field_locations[x] == -1:
                    found_everything = False
                    self.__field_locations["HEADER_ROW"] = -1

        return(found_everything)

    def get_cases(self,state, county):
        """Description: Accessor function to get cases data for a specified state and county
        Inputs:
            state - the state to retrieve cases data for
            county - the county to retrieve cases data for ("ALL" for aggregate of all counties)
        Outputs:
          return - [[date], [cases]] or None of invalid state / county
        """
        key = state + ", " + county
        if key in self.__time_series_cases_data:
            date = self.__time_series_cases_data[key][0].copy()
            cases = self.__time_series_cases_data[key][1].copy()
            return([date,cases])
        else:
            return(None)
  
    def get_daily_new_cases(self,state, county):
        """Description: Accessor function to get new daily cases data for a specified state and county
        Inputs:
            state - the state to retrieve cases data for
            county - the county to retrieve cases data for ("ALL" for aggregate of all counties)
        Outputs:
          return - [[date], [cases]] or None of invalid state / county
        """
        key = state + ", " + county
        date = []
        new_cases = []
        if key in self.__time_series_cases_data:
            for i in range (1, len(self.__time_series_cases_data[key][0])):
                date.append(self.__time_series_cases_data[key][0][i])
                new_case_val = self.__time_series_cases_data[key][1][i] - self.__time_series_cases_data[key][1][i-1]
                new_cases.append(new_case_val)
            return([date,new_cases])
        else:
            return(None)

    def get_state_county_keys(self):
        """Description: Accessor function to get new daily cases data for a specified state and county
        Inputs: None
        Outputs:
          return - [[states], [counties]]
        """
        states = []
        counties = []
        for key in self.__time_series_cases_data:
            values = key.partition(",")
            states.append(values[0])
            counties.append(values[2].lstrip())
        return([states, counties])
        
    def plot_cases_data(self, state_list, county_list):
        """Description: function to create an XY plot of specified state/county pairs
        Inputs: 
            state_list - list of states in state / county pair list
            county_list - list of counties in state / county pair list
        Outpus:
            A plot window is opened
        """
        fig, ax = plt.subplots()
        for i in range(0, len(state_list)):
            key_val = state_list[i] + ", " + county_list[i]
            if key_val in self.__time_series_cases_data:
                x = self.__time_series_cases_data[key_val][0]
                datemin = datetime.date(min(self.__time_series_cases_data[key_val][0]).year, min(self.__time_series_cases_data[key_val][0]).month, 1)
                datemax = datetime.date(max(self.__time_series_cases_data[key_val][0]).year, max(self.__time_series_cases_data[key_val][0]).month + 1, 1)

                y = self.__time_series_cases_data[key_val][1]
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
        
        
    def plot_new_cases_data(self, state_list, county_list):
        """Description: function to create an XY plot of specified state/county pairs
        Inputs: 
            state_list - list of states in state / county pair list
            county_list - list of counties in state / county pair list
        Outpus:
            A plot window is opened
        """
        fig, ax = plt.subplots()
        for i in range(0, len(state_list)):
            key_val = state_list[i] + ", " + county_list[i]
            if key_val in self.__time_series_cases_data:
                [x, y] = self.get_daily_new_cases(state_list[i], county_list[i])
                datemin = datetime.date(min(x).year, min(x).month, 1)
                datemax = datetime.date(max(x).year, max(x).month + 1, 1)

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