# covid19_data_analysis
script for parsing and plotting data from Johns Hopkins COVID-19 data repository

https://github.com/CSSEGISandData/COVID-19

This script allows users to plot many different graphs relating to COVID-19 data:
* Daily Rate of Confirmed Cases to People Tested vs. Date
* Daily Number of People Tested vs. Date
* Daily Cases per 1mil population vs. Date
* Confirmed Cases vs. Date

This project was built using python3 and curl (to automatically grab data)

## Install

Clone repository and run ```pip install -r requirements.txt```. This will install all python dependencies

Other dependencies include ```curl```

## Usage

Run ```python covid19_data_analysis.py``` or ```python3 covid19_data_analysis.py``` depending on os

## Sample Output 
<p align="center">
  <img src="img.jpeg" width="350">
</p>

## License
[gpl-3.0](https://opensource.org/licenses/lgpl-3.0.html)

## Project Status
In development with daily to weekly commits

## Features coming soon
* Better error handling
* Easier UI
* Increased Portability
* Portability Testing
* Derivative Graphs
* Example Output
