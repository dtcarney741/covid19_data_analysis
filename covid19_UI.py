import easygui as eg
import covid19_data
import os
 
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
