import colorama
import os

import covid19_data
import covid19_UI
import data_grabber


TIME_SERIES_PATH = '/csse_covid_19_data/csse_covid_19_time_series'
US_DAILY_REPORTS_PATH = '/csse_covid_19_data/csse_covid_19_daily_reports_us'
DAILY_REPORTS_PATH = '/csse_covid_19_data/csse_covid_19_daily_reports'

choice = ''
if os.path.isdir('./data'):
    all_subdirs = []
    for d in os.listdir('./data'):
        bd = os.path.join('./data', d)
        if os.path.isdir(bd):
            all_subdirs.append(bd)
    latest_subdir = max(all_subdirs, key=os.path.getmtime)
    
    data_folder = latest_subdir + '/' + os.listdir(latest_subdir)[0] + TIME_SERIES_PATH
    us_daily_reports_folder = latest_subdir + '/' + os.listdir(latest_subdir)[0] + US_DAILY_REPORTS_PATH
    daily_reports_folder = latest_subdir + '/' + os.listdir(latest_subdir)[0] + DAILY_REPORTS_PATH
else:
    data_folder = '.'
    us_daily_reports_folder = None
    daily_reports_folder = None
    
print("Default Data Folder: ", data_folder)

c19_data = covid19_data.Covid19_Data()
while (choice.upper() != 'Q'):
    c = colorama.Fore.YELLOW
    r = colorama.Fore.RESET
    print("")
    print("Options")
    print(c + "(R)" + r + "etrieve Johns Hopkins Data")
    print(c + "(L)" + r + "oad Time Series Data File, Load " + c + "(U)" + r + "S Daily Reports")
    print("Plot Total " + c + "(C)" + r + "onfirmed Cases, Plot " + c + "(N)" + r + "ew Daily Cases, Plot Total " + c + "(D)" + r + "eaths, Plot Ne" + c + "(W)" + r + " Daily Deaths")
    print(r+ "Plot " + c + "(I)" + r + "ncident Rate")
    print("Plot " + c + "(P)" + r + "eople Tested, Plot New Daily P" + c + "(E)" + r + "ople Tested, Plot Daily R" + c + "(A)" + r + "tio of Confirmed Cases to People Tested")
    print("Plot " + c + "(M)" + r + "y Saved Plots")
    print(c + "(Q)" + r + "uit")
    choice = input("What is your choice? ")
    
    if (choice.upper() == 'R'):
        retrieve_path = data_grabber.retrieve_data()
        data_folder = retrieve_path + TIME_SERIES_PATH
        us_daily_reports_folder = retrieve_path + US_DAILY_REPORTS_PATH
        daily_reports_folder = retrieve_path + DAILY_REPORTS_PATH
        print("Data downloaded to: ", data_folder)

    elif (choice.upper() == 'U'):
        if (us_daily_reports_folder != None):
            if c19_data.read_us_daily_reports_data(us_daily_reports_folder):
                print("US daily reports files read in successfully")
            else:
                print("ERROR: US daily report files not read in successfully")
        else:
            print("ERROR: Invalid US daily reports directory, US daily report files not read in successfully")

    elif (choice.upper() == 'L'):
        file_name = covid19_UI.Covid19_UI.choose_file(data_folder)
        if c19_data.read_time_series_cases_data(file_name):
            print("Time series data file read in successfully")
        else:
            print("ERROR: time series data file not read in succesfully")
    elif (choice.upper() == "DEBUG1"):
        covid19_UI.Covid19_UI.print_state_names(c19_data)
    elif (choice.upper() == "DEBUG2"):
        dates = c19_data.get_dates()
        tested = c19_data.get_people_tested(state="Wisconsin", county="ALL", key=None)
        for i in range(0, len(dates)):
            print(dates[i], tested[i])
    elif (choice.upper() == 'C'):
        key_list = c19_data.get_cases_keys()
        selected_keys = covid19_UI.Covid19_UI.select_states_counties("Plot Confirmed Cases", key_list)
        c19_data.plot_cases_data(state_list=None, county_list=None, key_list = selected_keys)
    elif (choice.upper() == 'N'):
        key_list = c19_data.get_cases_keys()
        selected_keys = covid19_UI.Covid19_UI.select_states_counties("Plot Daily New Cases", key_list)
        c19_data.plot_new_cases_data(state_list=None, county_list=None, key_list = selected_keys)
    elif (choice.upper() == 'D'):
        key_list = c19_data.get_deaths_keys()
        selected_keys = covid19_UI.Covid19_UI.select_states_counties("Plot Deaths", key_list)
        c19_data.plot_deaths_data(state_list=None, county_list=None, key_list = selected_keys)
    elif (choice.upper() == 'W'):
        key_list = c19_data.get_deaths_keys()
        selected_keys = covid19_UI.Covid19_UI.select_states_counties("Plot Daily New Deaths", key_list)
        c19_data.plot_new_deaths_data(state_list=None, county_list=None, key_list = selected_keys)
    elif (choice.upper() == 'I'):
        key_list = c19_data.get_incident_rate_keys()
        selected_keys = covid19_UI.Covid19_UI.select_states_counties("Plot Incident Rate", key_list)
        c19_data.plot_incident_rate_data(state_list=None, county_list=None, key_list = selected_keys)
    elif (choice.upper() == 'P'):
        key_list = c19_data.get_people_tested_keys()
        selected_keys = covid19_UI.Covid19_UI.select_states_counties("Plot People Tested", key_list)
        c19_data.plot_people_tested_data(state_list=None, county_list=None, key_list = selected_keys)
    elif (choice.upper() == 'E'):
        key_list = c19_data.get_people_tested_keys()
        selected_keys = covid19_UI.Covid19_UI.select_states_counties("Plot Daily New People Tested", key_list)
        c19_data.plot_new_people_tested_data(state_list=None, county_list=None, key_list = selected_keys)
    elif (choice.upper() == 'A'):
        key_list = c19_data.get_people_tested_keys()
        selected_keys = covid19_UI.Covid19_UI.select_states_counties("Plot Daily Ratio of Confirmed Cases to People Tested", key_list)
        c19_data.plot_daily_ratio_cases_to_people_tested_data(state_list=None, county_list=None, key_list = selected_keys)
    elif (choice.upper() == 'M'):
        selected_states = []
        selected_counties = []
        selected_states.append('Wisconsin')
        selected_counties.append('ALL')
        selected_states.append('Wisconsin')
        selected_counties.append('Brown')
        selected_states.append('Wisconsin')
        selected_counties.append('Calumet')
        selected_states.append('Wisconsin')
        selected_counties.append('Outagamie')
        selected_states.append('Wisconsin')
        selected_counties.append('Winnebago')
        c19_data.plot_new_cases_data(state_list=selected_states, county_list=selected_counties, key_list=None)
        selected_states = []
        selected_counties = []
        selected_states.append('Wisconsin')
        selected_counties.append('ALL')
        c19_data.plot_daily_ratio_cases_to_people_tested_data(state_list=selected_states, county_list=selected_counties, key_list=None)
        selected_states.append('Illinois')
        selected_counties.append('ALL')
        selected_states.append('Minnesota')
        selected_counties.append('ALL')
        selected_states.append('Indiana')
        selected_counties.append('ALL')
        selected_states.append('Michigan')
        selected_counties.append('ALL')
        selected_states.append('Iowa')
        selected_counties.append('ALL')
        selected_states.append('Ohio')
        selected_counties.append('ALL')
        c19_data.plot_daily_ratio_cases_to_people_tested_data(state_list=selected_states, county_list=selected_counties, key_list=None)
        c19_data.plot_new_people_tested_data(state_list=selected_states, county_list=selected_counties, key_list=None)
        c19_data.plot_new_cases_data(state_list=selected_states, county_list=selected_counties, key_list=None)
