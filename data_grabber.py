from datetime import date
import shutil
import subprocess
import zipfile
import os

def retrieve_data():
    """
    uses git shell command to retrieve the data
    returns output directory
    
    returns path of folder that data in contained in
    ex. ./"date"/"folder name"
    """
    if os.path.isfile("./data.zip"):  # remove old zipped data
        os.remove("./data.zip")
        
    subprocess.Popen("curl -L https://api.github.com/repos/CSSEGISandData/COVID-19/zipball/master --output data.zip", shell=True, stdout=subprocess.PIPE).wait()
    
    
    #make directories for data to be held
    if not os.path.isdir("./data"):
        os.mkdir("./data")
    
    output_folder = "./data/" + str(date.today())
    if os.path.isdir(output_folder):  # force remake of data folder
        shutil.rmtree(output_folder)
    os.mkdir(output_folder)
    
    with zipfile.ZipFile("./data.zip", 'r') as zip_ref:
        zip_ref.extractall(output_folder)


    os.remove("./data.zip")  # cleanup
    
    data_folder = output_folder + "/" + str(os.listdir(output_folder)[0])
    return data_folder


if __name__ == "__main__":  # debug
    print(retrieve_data())
    
    
    