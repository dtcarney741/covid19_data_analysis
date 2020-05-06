import covid19_data
import covid19_UI


choice = ''
c19_data = covid19_data.Covid19_Data()
while (choice.upper() != 'Q'):
    print("")
    print("Options")
    print("(L)oad Data, Plot Total (C)onfirmed Cases, Plot (N)ew Cases, Plot Total (D)eaths")
    print("(Q)uit")
    choice = input("What is your choice? ")
    
    if (choice.upper() == 'L'):
        file_name = covid19_UI.Covid19_UI.choose_file()
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
