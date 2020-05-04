import covid19_data
import os

def choose_file():
    allFiles = [f for f in os.listdir('.') if os.path.isfile(f)]
    filteredFiles = []
    i = 0
    for f in allFiles:
        fileExtension = f.partition('.')[2]
        if fileExtension == "csv":
            print("(",i,")",f)
            filteredFiles.append(f)
            i = i + 1

    choice = input("Choose file to analyze by index or type filename: ")
    try:
        index = int(choice)
        fileName = filteredFiles[index]
    except ValueError:
        fileName = choice
        
    return(fileName)
    


choice = ''
c19_data = covid19_data.Covid19_Data()
while (choice.upper() != 'Q'):
    print("")
    print("Options")
    print("(L)oad Data, Plot Total (C)onfirmed Cases, Plot (N)ew Cases, Plot Total (D)eaths")
    print("(Q)uit")
    choice = input("What is your choice? ")
    
    if (choice.upper() == 'L'):
        file_name = choose_file()
        c19_data.read_time_series_cases_data(file_name)
    elif (choice.upper() == "DEBUG"):
        [states, counties] = c19_data.get_state_county_keys()
        for i in range (0,len(states)):
            print("State: ", states[i], ", County: ", counties[i])
            print(c19_data.get_cases(states[i], counties[i]))
            print(c19_data.get_daily_new_cases(states[i], counties[i]))
    elif (choice.upper() == 'C'):
        states = []
        counties = []
        states.append("Wisconsin")
        counties.append("ALL")
        states.append("Wisconsin")
        counties.append("Outagamie")
        states.append("Wisconsin")
        counties.append("Brown")
        states.append("Wisconsin")
        counties.append("Milwaukee")
        states.append("Wisconsin")
        counties.append("Dane")
#        states.append("Ohio")
#        counties.append("ALL")
#        states.append("Michigan")
#        counties.append("ALL")
#        states.append("Florida")
#        counties.append("ALL")
#        states.append("California")
#        counties.append("ALL")
#        states.append("New York")
#        counties.append("ALL")
        c19_data.plot_cases_data(states, counties)
    elif (choice.upper() == 'N'):
        states = []
        counties = []
        states.append("Wisconsin")
        counties.append("ALL")
        states.append("Wisconsin")
        counties.append("Outagamie")
        states.append("Wisconsin")
        counties.append("Brown")
        states.append("Wisconsin")
        counties.append("Milwaukee")
        states.append("Wisconsin")
        counties.append("Dane")
#        states.append("Ohio")
#        counties.append("ALL")
#        states.append("Michigan")
#        counties.append("ALL")
#        states.append("Florida")
#        counties.append("ALL")
#        states.append("California")
#        counties.append("ALL")
#        states.append("New York")
#        counties.append("ALL")
        c19_data.plot_new_cases_data(states, counties)
