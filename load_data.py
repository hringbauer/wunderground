# Never give up my son. Trust your instincts.

'''
Created on May 6th, 2017
Class that locally stores the Data from Wunderground.
Stores everything in .csv Files that are grouped with respect to Month
Has methods to Update it everyime one calls it.
Has methods to Hand out the Data.
All dates are given as DateTime objects
@author: hringbauer
'''

import numpy as np
import pandas as pd
import StringIO
import requests
from dateutil import parser
from dateutil.rrule import rrule, MONTHLY
import datetime
import calendar
import os
import pickle as pickle
import warnings
import matplotlib.pyplot as plt

# Some helper functions:
def clean_data(f):
    '''Decorator Function; that gives back only
    the clean data. First call the original function
    and then extract the cleaned data'''
    def decorated(*args, **kwargs):
        df = f(*args, **kwargs) # Call original Function
        df = df[df['solar'] >= 0]
        return df
    return decorated

def give_dt_date(string):
    '''Gives back date from string'''
    dt_object = datetime.datetime.strptime(string, '%Y-%m-%d %H:%M:%S') # Convert to DateTime
    date=dt_object.date()
    return date

def give_dt_object(string):
    '''Gives back datetime object from string'''
    dt_object = datetime.datetime.strptime(string, '%Y-%m-%d %H:%M:%S') # Convert to DateTime
    return dt_object
    
#############################################################


class WeatherData(object):
    '''Simple class that loads and gives back 
    specific data.'''
    station_name = "IDRSING3"
    local_folder = "./Data/"  # Where to find the data
    last_date = 0  # Last date for which data is available
    fn_last_updated = "last_updated.p"  # Name of File that saves when there was the last update
    
    first_year = 2017
    first_month = 5
    
    
    def __init__(self, station_name=None, local_folder="", first_year=None, first_month=None):
        '''Initializes the Class. If nothing passed default to Harald's WS;
        but can also be run for other WS'''
        # Sets Station Name if not given:
        if station_name:
            self.station_name = station_name
            
        # Sets local Folder if not given to default:
        if len(local_folder) > 0:
            self.local_folder = local_folder
        
        # If initial Date given save it:
        if first_year:
            self.first_year = first_year
            
        if first_month:
            self.first_month = first_month
            
        # self.load_data(self.station_name, day=4, month=5, year=2017)
        
    
    def save_last_date(self, date):
        '''Pickle the last save date.'''
        path = self.local_folder + self.fn_last_updated
        
        print("Saving New Last Date. Year: %i Month: %i" % (date.year, date.month))
        pickle.dump(date, open(path, "wb"))
        
    def load_last_date(self):
        '''Pickle loads the last save date.'''
        path = self.local_folder + self.fn_last_updated
        
        # If it exists; otherwise go back all the way to the beginning
        if os.path.exists(path):  
            date = pickle.load(open(path, "rb"))
            
        else: date = datetime.date(year=self.first_year, month=self.first_month, day=1)
        
        print("Loading last Save Date. Year: %i Month: %i" % (date.year, date.month))
        return date
    
    def save_local(self, begin_date=None, end_date=None):
        '''Saves the date locally within the given time period
        from begin to end date. Format should be in Datetime objects
        '''
        
        # In case no begin given set to very beginning of Measurements
        if begin_date == None:
            year_l = self.first_year
            month_l = self.first_month
            begin_date = datetime.date(year=year_l, month=month_l, day=1)
        
        # If no end_time set it to now
        if end_date == None:
            end_date = datetime.datetime.now()
          
        for dt in rrule(MONTHLY, dtstart=begin_date, until=end_date):
            self.local_save_month(dt)
        
    def update_local(self, end_date=None, all=0): 
        '''Updates all local files up until end_date.
        If all reload EVERYTHING!''' 
        if end_date == None:
            end_date = datetime.datetime.now()
            
        begin_date = self.load_last_date()  # Load the last time something was updated     
        
        if all == 0:
            self.save_local(begin_date, end_date)
        
        elif all == 1:
            self.save_local(end_date=end_date)  # Locally saves everything!
        
        self.save_last_date(end_date)  # Save the End Date
        print("Update successfully finished!")
        
        
    def local_save_month(self, date):
        '''Locally saves data of a specific month.
        Date is dateutil object; data is save to its month.'''
        year = date.year
        month = date.month
        print("Downloading Year: %i Month: %i" % (year, month))
        
        df = self.download_data_month(date)
        
        path = self.local_folder + str(year) + "/" + str(month) + ".csv"
        
        # Create Directory if not existent
        directory = os.path.dirname(path)  # Extract Directory
        if not os.path.exists(directory):  # Creates Folder if not already existing
            os.makedirs(directory)
        
        # Save: 
        df.to_csv(path)
        
    
    def load_local(self, date):
        '''Method to load local Data from .csv'''
        year = date.year
        month = date.month
        
        path = self.local_folder + str(year) + "/" + str(month) + ".csv"
        df = pd.read_csv('../data/example.csv')
        
        return df
    
    def download_data_month(self, date):
        '''Loads all Data from one month in pandas a data-frame.
        Gets raw data from all days and concatenates them'''
        day=1
        
        dfs=[]
        for day in xrange(1,calendar.monthrange(date.year, date.month)[1]+1):
            df = self.download_data_day(day, date.month, date.year)
            if len(df)==0:
                break
            dfs.append(df)
        print(len(dfs))
        df = pd.concat(dfs, ignore_index=True)
        return df
    
        
         
    def download_data_day(self, day, month, year, station=""):
        """
        Function to return a data frame of weather data for Wunderground PWS station.
        Returns all data for a single day
        Args:
            station (string): Station code from the Wunderground website
            day (int): Day of month for which data is requested
            month (int): Month for which data is requested
            year (int): Year for which data is requested
        
        Returns:
            Pandas Dataframe with weather data for specified station and date.
        """
        # If no station Name given use default:
        if len(station) == 0:
            station = self.station_name
        
        print("Loading Data for Station:  %s" % self.station_name)
        url = "http://www.wunderground.com/weatherstation/WXDailyHistory.asp?ID={station}&day={day}&month={month}&year={year}&graphspan=day&format=1"
        full_url = url.format(station=station, day=day, month=month, year=year)
        print("Download in progress from:")
        print(full_url)
        # Request data from wunderground data
        response = requests.get(full_url,
                                headers={'User-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'})
        data = response.text
        # remove the excess <br> from the text data
        data = data.replace('<br>', '')
        # Convert to pandas dataframe
        df = pd.read_csv(StringIO.StringIO(data), index_col=False)
        
        if len(df)==0:
             warnings.warn("Error: Empty Data Set!!", RuntimeWarning)
             return df
         
        df['station'] = station
        
        # Convert to more easily readable columns
        df1 = pd.DataFrame()
        # Some Data Cleaning:
        df1['temp'] = df['TemperatureC'].astype(float)
        df1['hour_rain'] = df['HourlyPrecipMM'].astype(float)
        df1['total_rain'] = df['dailyrainMM'].astype(float)
        df1['date'] = df['DateUTC'].apply(parser.parse)
        df1['humidity'] = df['Humidity'].astype(float)
        df1['wind_direction'] = df['WindDirectionDegrees'].astype(float)
        df1['wind'] = df['WindSpeedKMH'].astype(float)
        df1['wind_gust'] = df['WindSpeedGustKMH'].astype(float)
        df1['pressure'] = df['PressurehPa'].astype(float)
        df1['humidity'] = df['Humidity'].astype(float)
        df1['solar'] = df['SolarRadiationWatts/m^2'].astype(float)
        df1['dewpoint'] = df['DewpointC'].astype(float)
        df1['station'] = df['station'].astype(str)
        
        print("Observations: %i" % df.shape[0])
        print(df1.dtypes)
        
        self.data = df1
        
        return df1
    
    def test_data(self):
        '''Some Text to test the Data'''
        print(self.data.head(1))
        print("Done")
        return self.data
    
    def give_data_day(self):
        '''Gives Data of the Weather Station.'''
        return self.data
        
    def give_clean_data(self, df):
        '''Cleans missing columns'''
        df = df[df['solar'] >= 0]
        return df
    
    
    def give_data_month(self, date):
        '''Loads data from month in date (date object)
        from local data base.'''
        month=date.month
        year =date.year
        
        path = self.local_folder + str(year) + "/" + str(month) + ".csv"
        
        # In case file is not there:
        if not os.path.exists(path):  # Creates Folder if not already existing
            warnings.warn("Error: Date does not exist!!", RuntimeWarning)
            return pd.DataFrame()
        
        df = pd.read_csv(path)
        return df
    
    @clean_data
    def give_data_month_clean(self, date):
        '''Give clean Data'''
        return self.give_data_month(date)
    
    def give_data_day(self, date):
        '''Extracts only a day. Takes a date-time as input'''
        df=self.give_data_month(date)
        dates = np.array(map(give_dt_date, df['date'])) # Extract only the dates

        df=df[dates==date]  # Compare to wished date; not minor information
        
        if len(df)==0:
            warnings.warn("Error: Data Set not found!!", RuntimeWarning)
        return df
    
    def give_daily_maximum_month(self, date, column="temp", min=False):
        '''Gives the maximum amount per day.
        date: Which Month. Datetime Object
        column: Which Data column to use
        min=True give minmum'''
        df = self.give_data_month_clean(date)
        col=df[column]
        
        # Get all Days in month
        year = date.year
        month = date.month
        num_days = calendar.monthrange(year, month)[1] # Number of days of Month
        days = [datetime.date(year, month, day) for day in range(1, num_days+1)]
        
        print("Loading Data...")
        # Load all daily column Data into vector:
        day_data_vec = [self.give_data_day_clean(day)[column] for day in days]
        
        
        # Get maximum/minimum per day:
        if min==True:
            res_vec = [np.min(day_data) for day_data in day_data_vec]
            
        elif min==False:
            res_vec = [np.max(day_data) for day_data in day_data_vec]
            
        else:
            raise ValueError("Min must be Boolean!!")
            
        return np.array(res_vec)
    
            
        
    @clean_data
    def give_data_day_clean(self, date):
        '''Extract a Day cleeaned up'''
        return self.give_data_day(date)
    
    

#################################
if __name__ == "__main__":
    date = datetime.date(year=2017, month=5, day=5)
# Test the Class:
    wd = WeatherData()
    # wd.update_local(all=1)
    # wd.update_local()
    #df=wd.give_data_month(date)
    #df = wd.give_data_month_clean(date)
    df = wd.give_data_day_clean(date)
    
    
    plt.figure()
    plt.plot(df["temp"],'ro')
    plt.show()
    print(df.head(10))
    #print(np.shape(df))
    # wd.download_data_day(1, 5, 2017)
    # data = wd.give_clean_data()
    # print(data.head(1))

    
        
