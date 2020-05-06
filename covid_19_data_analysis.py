import covid19_data
import covid19_UI
import data_grabber
import os

TIME_SERIES_PATH = '/csse_covid_19_data/csse_covid_19_time_series'
choice = ''
if os.path.isdir('./data'):
    all_subdirs = []
    for d in os.listdir('./data'):
        bd = os.path.join('./data', d)
        if os.path.isdir(bd):
            all_subdirs.append(bd)
    latest_subdir = max(all_subdirs, key=os.path.getmtime)
    
    data_folder = latest_subdir + '/' + os.listdir(latest_subdir)[0] + TIME_SERIES_PATH
else:
    data_folder = '.'
    
print("Default Data Folder: ", data_folder)

c19_data = covid19_data.Covid19_Data()
while (choice.upper() != 'Q'):
    print("")
    print("Options")
    print("(R)etrieve Johns Hopkins Data")
    print("(L)oad Data, Plot Total (C)onfirmed Cases, Plot (N)ew Cases, Plot Total (D)eaths")
    print("(Q)uit")
    choice = input("What is your choice? ")
    
    if (choice.upper() == 'R'):
        data_folder = data_grabber.retrieve_data()
        data_folder = data_folder + TIME_SERIES_PATH
        print("Data downloaded to: ", data_folder)
    elif (choice.upper() == 'L'):
        file_name = covid19_UI.Covid19_UI.choose_file(data_folder)
        c19_data.read_time_series_cases_data(file_name)
    elif (choice.upper() == "DEBUG1"):
        covid19_UI.Covid19_UI.print_state_names(c19_data)
    elif (choice.upper() == 'C'):
        key_list = c19_data.get_cases_keys()
        selected_keys = covid19_UI.Covid19_UI.select_keys("Plot Confirmed Cases", "Select states / counties for plot", key_list)
        c19_data.plot_cases_data(state_list=None, county_list=None, key_list = selected_keys)
    elif (choice.upper() == 'N'):
        key_list = c19_data.get_cases_keys()
        selected_keys = covid19_UI.Covid19_UI.select_keys("Plot Daily New Cases", "Select states / counties for plot", key_list)
        c19_data.plot_new_cases_data(state_list=None, county_list=None, key_list = selected_keys)
