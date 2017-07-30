'''
Created on 17.10.2014
This is the main file; where everything comes together.
It is in a do it yourself adventure style.
@author: Harald Ringbauer
'''
from load_data import WeatherData
from visualize_data import Analyze_WD
import datetime

def menu():
    print("Heyyaa hope u doing well future Harald.")
    
    wd = WeatherData()
    
    while True:
        int1 = input("\nWhat do you want to do? \n(1) Download Weather Data" 
                                                "\n(2) Analyze Weather Data"
                                                "\n(9) Exit\n")
        
        if int1==1:
            int2 = input("""Download what? \n(1) Since Last Update"""
            """\n(2) All Data \n(3) Specific Dates\n""")
            
            if int2 ==1:
                wd.update_local()
                
            elif int2 == 2:
                wd.update_local(all=1)
                
        
        elif int1==2:
                v_wd = Analyze_WD(wd)  # Create the Analysis Object
                
                while True:
                    int3 = input("What Analysis? \n(1) Monthly Rain Analysis \n(2) Monthly Sun Analysis" 
                    "\n(3) Show Max/Min Month \n(4) Day Temperature\n(5) Show Records \n(9) Break\n")
                    
                    if int3 == 1:
                        date = get_month() # Get the Date (via Input)
                        v_wd.visualize_rain_month(date_month=date)
                    
                    elif int3 == 2:
                        date = get_month()
                        v_wd.visualize_solar_month(date_month=date)  
                        
                    elif int3 == 3:
                        date = get_month()
                        dtype = get_data_type()
                        v_wd.visualize_max_min_month(date, column=dtype)
                        
                    elif int3 == 4:
                        date = get_day() # Get the Date (via Input)
                        v_wd.visualize_day_data(date, column="temp")
                        
                    elif int3 == 9:
                        break
                    
                    else:
                        print("Invalid Input!!")
        
                    
                
            
            
        if int1==9: break
        
    print("see u later alligata")
    return 0


### Helper Input Functions; that will get called quite a bit
def get_day(year=None, month=None, day=None):
    '''Function to get the Day Date object'''
    if year == None:
        year = input("What year?\n")
        
    if month == None:
        month = input("What month?\n")
        
    if day== None:
        day = input("What day?\n")
        
    return datetime.date(year=year, month=month, day=day)
    
def get_month(year=None, month=None, day=None):
    '''Function to get the Month Date object'''
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

### Call the main loop
if __name__ == "__main__":
    menu()
    
    
    