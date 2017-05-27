'''
Created on 17.10.2014
This is the main file; where everything comes together.
It is in a do it yourself adventure style.
@author: Harald Ringbauer
'''
from load_data import WeatherData
from visualize_data import Analyze_WD

print("Heyyaa hope u doing well future Harald.")

wd = WeatherData()

while True:
    int1 = input("\nWhat do you want to do? \n(1) Download Weather Data" 
                                            "\n(2) Analyze Weather Data"
                                            "\n(9) Exit\n")
    
    if int1==1:
        int2 = input("""Download what? \n(1) Since Last Update
        \n(2) All Data \n(3) Specific Dates\n""")
        
        if int2 ==1:
            wd.update_local()
            
        elif int2 == 2:
            wd.update_local(all=1)
            
    
    elif int1==2:
            v_wd = Analyze_WD(WeatherData)  # Create the Analysis Object
            
            while True:
                int3 = input("What Analysis? \n(9) Break\n")
                
                if int3 == 9:
                    break
                
            
        
        
    if int1==9: break
    
print("see u later alligata")
