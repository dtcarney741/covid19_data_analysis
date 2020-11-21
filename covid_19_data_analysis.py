import colorama
import os

import covid19_data
import covid19_UI
import data_grabber


TIME_SERIES_PATH = '/csse_covid_19_data/csse_covid_19_time_series'
US_DAILY_REPORTS_PATH = '/csse_covid_19_data/csse_covid_19_daily_reports_us'
DAILY_REPORTS_PATH = '/csse_covid_19_data/csse_covid_19_daily_reports'
POPULATION_PATH = '/csse_covid_19_data/'

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
    world_daily_reports_folder = latest_subdir + '/' + os.listdir(latest_subdir)[0] + DAILY_REPORTS_PATH
    population_file = latest_subdir + '/' + os.listdir(latest_subdir)[0] + POPULATION_PATH + 'UID_ISO_FIPS_LookUp_Table.csv'
else:
    data_folder = '.'
    us_daily_reports_folder = None
    world_daily_reports_folder = None
    population_file = None
    
print("Default Data Folder: ", data_folder)

c19_data = covid19_data.Covid19_Data()
while (choice.upper() != 'Q'):
    c = colorama.Fore.YELLOW
    r = colorama.Fore.RESET
    print("")
    print("Options")
    print(c + "(R)" + r + "etrieve Johns Hopkins Data")
    print(c + "(L)" + r + "oad Time Series Data File, Load " + c + "(U)" + r + "S Daily Reports, Load " + c + "(W)" + r + "orld Daily Reports")
    print("Load " + c + "(P)" + r + "opulation File")
    print("Plot " + c + "(M)" + r + "y Saved Plots, Plot User " + c + "(D)" + r + "efined Plot")
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
            if c19_data.read_daily_reports_data(us_daily_reports_folder,data_location="us",on_disk=True):
                print("US daily reports files read in successfully")
            else:
                print("ERROR: US daily report files not read in successfully")
        else:
            print("ERROR: Invalid US daily reports directory, US daily report files not read in successfully")

    elif (choice.upper() == 'W'):
        if (us_daily_reports_folder != None):
            if c19_data.read_daily_reports_data(world_daily_reports_folder,data_location="world",on_disk=True):
                print("World daily reports files read in successfully")
            else:
                print("ERROR: World daily report files not read in successfully")
        else:
            print("ERROR: Invalid World daily reports directory, World daily report files not read in successfully")
        
    elif (choice.upper() == 'L'):
        file_name = covid19_UI.Covid19_UI.choose_file(data_folder)
        if c19_data.read_time_series_data(filename=file_name, url=None):
            print("Time series data file read in successfully")
        else:
            print("ERROR: time series data file not read in succesfully")
    elif (choice.upper() == 'P'):
        if c19_data.read_population_data(filename=population_file, url=None):
            print("Population file read in successfully")
        else:
            print("ERROR: population file not read in successfully")
            
    elif (choice.upper() == "DEBUG1"):
        print("Debug 1 command")
        node = c19_data.get_tree_node("US", None, None)
        print(node.get_log_moving_average_daily_new_cases_incident_rate(7))
    elif (choice.upper() == "DEBUG2"):
        print("Debug 2 command")
    elif (choice.upper() == 'M'):
        selected_countries = []
        selected_states = []
        selected_counties = []
        selected_countries.append("US")
        selected_states.append('Wisconsin')
        selected_counties.append('Brown')
        selected_countries.append("US")
        selected_states.append('Wisconsin')
        selected_counties.append('Calumet')
        selected_countries.append("US")
        selected_states.append('Wisconsin')
        selected_counties.append('Outagamie')
        selected_countries.append("US")
        selected_states.append('Wisconsin')
        selected_counties.append('Winnebago')
        c19_data.plot_data(selected_countries, selected_states, selected_counties, "CONFIRMED_CASES")
        c19_data.plot_data(selected_countries, selected_states, selected_counties, "DEATHS")
        
        selected_countries = []
        selected_states = []
        selected_counties = []
        selected_countries.append("US")
        selected_states.append('Wisconsin')
        selected_counties.append('None')
        selected_countries.append("US")
        selected_states.append('Wisconsin')
        selected_counties.append('Calumet')
        selected_countries.append("US")
        selected_states.append('Wisconsin')
        selected_counties.append('Outagamie')
        selected_countries.append("US")
        selected_states.append('Wisconsin')
        selected_counties.append('Winnebago')
        selected_countries.append("US")
        selected_states.append('Alabama')
        selected_counties.append('None')
        selected_countries.append("US")
        selected_states.append('Alabama')
        selected_counties.append('Jefferson')
        c19_data.plot_data(selected_countries, selected_states, selected_counties, "CONFIRMED_CASES")
        c19_data.plot_data(selected_countries, selected_states, selected_counties, "DEATHS")
       
        selected_countries = []
        selected_states = []
        selected_counties = []
        selected_countries.append("US")
        selected_states.append('Florida')
        selected_counties.append('None')
        selected_countries.append("US")
        selected_states.append('Texas')
        selected_counties.append('None')
        selected_countries.append("US")
        selected_states.append('California')
        selected_counties.append('None')
        selected_countries.append("US")
        selected_states.append('Arizona')
        selected_counties.append('None')
        selected_countries.append("US")
        selected_states.append('North Carolina')
        selected_counties.append('None')
        selected_countries.append("US")
        selected_states.append('Georgia')
        selected_counties.append('None')
        selected_countries.append("US")
        selected_states.append('Wisconsin')
        selected_counties.append('None')
        c19_data.plot_data(selected_countries, selected_states, selected_counties, "CONFIRMED_CASES")
        c19_data.plot_data(selected_countries, selected_states, selected_counties, "DEATHS")
        c19_data.plot_data(selected_countries, selected_states, selected_counties, "DAILY_RATIO_CONFIRMED_CASES_TO_PEOPLE_TESTED")
        c19_data.plot_data(selected_countries, selected_states, selected_counties, "CALCULATED_CASES_INCIDENT_RATE")
    elif (choice.upper() == 'D'):
        selected_countries = []
        selected_states = []
        selected_counties = []
        selected_countries.append("US")
        selected_states.append('Wisconsin')
        selected_counties.append('None')
        selected_countries.append("US")
        selected_states.append('Ohio')
        selected_counties.append('None')
        selected_countries.append("US")
        selected_states.append('Indiana')
        selected_counties.append('None')
        selected_countries.append("US")
        selected_states.append('Alabama')
        selected_counties.append('None')
        c19_data.plot_data(selected_countries, selected_states, selected_counties, "DAILY_NEW_CASES")
        c19_data.plot_data(selected_countries, selected_states, selected_counties, "DAILY_RATIO_CONFIRMED_CASES_TO_PEOPLE_TESTED")
        c19_data.plot_data(selected_countries, selected_states, selected_counties, "DAILY_NEW_CASES_INCIDENT_RATE")
        
