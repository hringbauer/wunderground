'''
Created on 17.10.2014
This is the main file; where everything comes together.
It is in a do it yourself adventure style.
@author: Harald Ringbauer
'''
from load_data import WeatherData
from visualize_data import Analyze_WD
import datetime
import tkinter as tk  # For the graphical user interface

def menu_text():
    print("Heyyaa hope u doing well future Harald.")
    
    wd = WeatherData()
    
    while True:
        int1 = input("\nWhat do you want to do? \n(1) Download Weather Data" 
                        "\n(2) Calculate Summary Statistics \n(3) Analyze Weather Data"
                                                "\n(9) Exit\n")
        
        if int1 == 1:
            while True:
                int2 = input("""Download what? \n(1) Since Last Update"""
                """\n(2) All Data \n(3) Specific Dates \n(4) Back\n""")
                
                if int2 == 1:
                    wd.update_local()
                
                if int2 == 2:
                    int3 = input("\nWhat do you want to do?")
                    
                    raise NotImplementedError("Implement this")
                    
                elif int2 == 3:
                    wd.update_local(all=1)
                    
                elif int2 == 4:
                    break
                
        elif int1 == 3:
                v_wd = Analyze_WD(wd)  # Create the Analysis Object
                
                while True:
                    int3 = input("What Analysis? \n(1) Monthly Rain Analysis \n(2) Monthly Sun Analysis" 
                    "\n(3) Show Max/Min Month \n(4) Plot Mean per Month \n(5) Day Temperature\n(6) Show Records \n(9) Break\n")
                    
                    if int3 == 1:
                        date = get_month()  # Get the Date (via Input)
                        v_wd.visualize_rain_month(date_month=date)
                    
                    elif int3 == 2:
                        date = get_month()
                        v_wd.visualize_solar_month(date_month=date)  
                        
                    elif int3 == 3:
                        date = get_month()
                        dtype = get_data_type()
                        v_wd.visualize_max_min_month(date, column=dtype)
                    
                    elif int3 == 4:
                        date = get_month()
                        dtype = get_data_type()
                        v_wd.visualize_mean_month(date_month=date, column=dtype)        
                        
                    elif int3 == 5:
                        date = get_day()  # Get the Date (via Input)
                        v_wd.visualize_day_data(date, column="temp")
                    
                    elif int3 == 6:
                        date = get_month()
                        minimum = int(input("Value? \n(0) Maximum \n(1) Minimum\n"))
                        print(minimum)
                        dtype = get_data_type()
                        
                        v_wd.visualize_records(date_month=date, date_year=0, minimum=minimum,
                          column=dtype)
                        
                    elif int3 == 9:
                        break
                    
                    else:
                        print("Invalid Input!!")
        
        if int1 == 9: break
        
    print("see u later alligata")
    return 0

#######################################
#######################################
def doNothing():
    print("lolol")
    

# ## Helper Input Functions; that will get called quite a bit
def get_day(year=None, month=None, day=None):
    '''Return the Day Date object'''
    if year == None:
        year = input("What year?\n")
        
    if month == None:
        month = input("What month?\n")
        
    if day == None:
        day = input("What day?\n")
        
    return datetime.date(year=year, month=month, day=day)
    
def get_month(year=None, month=None, day=None):
    '''Return the Month Date object'''
    if year == None:
        year = input("What year?\n")
        
    if month == None:
        month = input("What month?\n")
        
    return datetime.date(year=year, month=month, day=1)

def get_data_type():
    '''What Data to visualize'''
    i = input("What Data to you want to analyze?"
                  "\n(1) Temperature \n(2) Rain Total \n(3) Whateva\n")
    if i == 1:
        dtype = "temp"
        
    elif i == 2:
        dtype = "total_rain"
    
    return dtype

# ## Call the main loop
if __name__ == "__main__":
    menu_text()
    
    
    
    
