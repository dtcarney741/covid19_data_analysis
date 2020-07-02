import covid19_data
import easygui as eg
import os

import covid19_data
 
class Covid19_UI(object):
    """Description: This class is used to provide some text based UI and GUI interfaces for the DSM entry and analysis tool
    """
# def __init__(self):
    def choose_file(folder):
        all_files_and_folders = os.listdir(folder)
        qualified_filenames = (os.path.join(folder, filename) for filename in all_files_and_folders)
        all_files = []
        for f in qualified_filenames:
            if os.path.isfile(f):
                all_files.append(f)
            else:
                print(f,' is not a file')
        print(all_files)
        filtered_files = []
        i = 0
        for f in all_files:
            if f.endswith(".csv"):
                print("(", i, ")", f)
                filtered_files.append(f)
                i = i + 1

        choice = input("Choose file to analyze by index or type filename: ")
        try:
            index = int(choice)
            fileName = filtered_files[index]
        except ValueError:
            fileName = choice
        return (fileName)

    def enter_items():
        itemEntry = True
        itemList = []
        while itemEntry:
            item = input("Enter Item (blank if no more items to enter): ")
            if item:
                itemList.append(item)
            else:
                itemEntry = False
        return(itemList)

    def print_state_names(c19_data):
        [states, counties] = c19_data.get_state_county_cases_keys()
        state_list = []
        for state in states:
            if state not in state_list:
                state_list.append(state)
        print("Confirmed Cases Data Dictionary States")
        print(state_list)
        [states, counties] = c19_data.get_state_county_incident_rate_keys()
        state_list = []
        for state in states:
            if state not in state_list:
                state_list.append(state)
        print("Incident Rate Data Dictionary States")
        print(state_list)
            
    def get_integer_input(promptString):
        retVal = ''
        try:    
            retVal = int(input(promptString))
        except ValueError:
            print("Invalid entry")
            
        return(retVal)

 
    def select_keys(title, question, key_list):
        """Description: Prompts user to select a subset of keys on a list
        Inputs: title - string with title of the window
                question - string with what the user is asked to select
                key_list - list of key values to select from
        Outputs:
        returns a list of item indices that were selected
        """
        key_list.sort()
        option_list = []
        for key in key_list:
            option_list.append(key)
         
        choices = eg.multchoicebox(question, title, option_list)

        return(choices)

    def select_key(title, question, key_list):
        """Description: Prompts user to select one key on a list
        Inputs: title - string with title of the window
                question - string with what the user is asked to select
                key_list - list of key values to select from
        Outputs:
        returns item index that was selected or None if none selected
        """
        key_list.sort()
        option_list = []
        for key in key_list:
            option_list.append(key)
         
        choice = eg.choicebox(question, title, option_list)

        return(choice)

    def select_states_counties(title, key_list):
        """Description: Prompts user to select one key on a list
        Inputs: title - string with title of the window
                key_list - list of [state,county] to select from
        Outputs:
        returns item index that was selected or None if none selected
        """
        select_only_states = eg.boolbox("Do you want to select only states, or individual counties?", "Selection Type", ["States", "States + Counties"])
        state_list = []
        option_list = []
        for key in key_list:
            [state, county] = covid19_data.Covid19_Data.split_state_county_from_key(key)
            if state not in state_list:
                state_list.append(state)
        selected_states = Covid19_UI.select_keys(title, "Select states to plot", state_list)
        if select_only_states:
            for state in selected_states:
                key = covid19_data.Covid19_Data.create_key(state, None)
                option_list.append(key)
        else:
            for state in selected_states:
                state_county_list = []
                for key in key_list:
                    [key_state, key_county] = covid19_data.Covid19_Data.split_state_county_from_key(key)
                    if  key_state == state:
                        state_county_list.append(key)
                selected_states_counties = Covid19_UI.select_keys(title, "For " + state + ", select counties to plot", state_county_list)
                for key in selected_states_counties:
                    option_list.append(key)
        
        print(option_list)
        return(option_list)