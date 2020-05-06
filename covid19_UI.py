import easygui as eg
import covid19_data
import os
 
class Covid19_UI(object):
    """Description: This class is used to provide some text based UI and GUI interfaces for the DSM entry and analysis tool
    """
# def __init__(self):
    def choose_file():
        allFiles = [f for f in os.listdir(".") if os.path.isfile(f)]
        filteredFiles = []
        i = 0
        for f in allFiles:
            fileExtension = f.partition(".")[2]
            if fileExtension == "csv":
                print("(", i, ")", f)
                filteredFiles.append(f)
                i = i + 1

        choice = input("Choose file to analyze by index or type filename: ")
        try:
            index = int(choice)
            fileName = filteredFiles[index]
        except ValueError:
            fileName = choice
        return fileName

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
