# Never give up my son. Trust your instincts.

'''
Created on May 6th, 2017
Class that analyzes and visualizes WunderGround data.
Access it over a wunderground data object;
data has methods to give the raw data (as PandasFrames)
'''

import numpy as np
import pandas as pd
import StringIO
import requests
from dateutil import parser
from dateutil.rrule import rrule, MONTHLY
from load_data import WeatherData, give_dt_object

import datetime
import calendar
import os
import pickle as pickle
import warnings
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.dates import  DateFormatter


class Analyze_WD(object):
    '''
    Created on May 6th, 2017
    Class that locally analyzes the Data from Wunderground.
    Stores WeatherData object that has methods to access the data and 
    can give it
    '''
    
    wd = 0
    
    def __init__(self, wd_object):
        '''Initializes the Class. If nothing passed default to Harald's WS'''
        self.wd = wd_object
    
    def visualize_temperature(self, date, column="temp"):
        '''Visualizes the Temperature for a given date.
        Date: datetime.date object'''
        df=self.wd.give_data_day_clean(date)
        
        # Extract Data
        temps = df[column]
        dates = map(give_dt_object, df['date'])
        dates = matplotlib.dates.date2num(dates)
        
        plt.figure()
        plt.title("Date: %s" % date)
        plt.plot_date(dates, temps, label=column)
        plt.legend(loc="upper right")
        plt.gca().xaxis.set_major_formatter(DateFormatter('%H:%M:%S') )
        plt.grid()
        plt.show()
        
        
#### Some testing functions:
if __name__ == "__main__":
    date = datetime.date(year=2017, month=5, day=27)
    
    wd = WeatherData()
    vis = Analyze_WD(wd)
    vis.visualize_temperature(date, column="temp")
    
    