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
import io as io
#from io import StringIO
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
        df = f(*args, **kwargs)  # Call original Function
        df = df[df['solar'] >= 0]
        return df
    return decorated

def give_dt_date(string):
    '''Give back date from string'''
    dt_object = datetime.datetime.strptime(string, '%Y-%m-%d %H:%M:%S')  # Convert to DateTime
    date = dt_object.date()
    return date

def give_dt_object(string):
    '''Give back datetime object from string'''
    dt_object = datetime.datetime.strptime(string, '%Y-%m-%d %H:%M:%S')  # Convert to DateTime
    return dt_object
    
#############################################################


class WeatherData(object):
    '''Simple class that loads and gives back 
    specific data.'''
    station_name = "IDRSING3"
    url = "http://www.wunderground.com/weatherstation/WXDailyHistory.asp?ID={station}&day={day}&month={month}&year={year}&graphspan=day&format=1"
    
    
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
    
    def save_local(self, begin_date=None, end_date=None, gui=None):
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
            self.local_save_month(dt, gui)
        
    def update_local(self, end_date=None, all=0, gui=None): 
        '''Updates all local files up until end_date.
        If all reload EVERYTHING!''' 
        if end_date == None:
            end_date = datetime.datetime.now()
            
        begin_date = self.load_last_date()  # Load the last time something was updated     
        
        print("Download starting from:")
        print(self.station_name)
        
        if gui:
            gui.update_idletasks()
        
        if all == 0:
            self.save_local(begin_date, end_date, gui)
        
        elif all == 1:
            self.save_local(end_date=end_date, gui=gui)  # Locally saves everything!
        
        self.save_last_date(end_date)  # Save the End Date
        print("Update successfully finished!")     
        
    def local_save_month(self, date, gui=None):
        '''Locally saves data of a specific month.
        Date is dateutil object; data is save to its month.'''
        year = date.year
        month = date.month
        print("Downloading Year: %i Month: %i" % (year, month))
        
        if gui:
            gui.update_idletasks()
        
        df = self.download_data_month(date, gui)
        
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
    
    def download_data_month(self, date, gui=None):
        '''Loads all Data from one month in pandas a data-frame.
        Gets raw data from all days and concatenates them'''
        day = 1
        
        dfs = []
        for day in range(1, calendar.monthrange(date.year, date.month)[1] + 1):
            df = self.download_data_day(day, date.month, date.year, gui=gui)
            if len(df) == 0:
                break
            dfs.append(df)
        if gui:
            print("Data Rows per Month loaded: %i" % len(dfs))
        df = pd.concat(dfs, ignore_index=True)
        return df
    
        
         
    def download_data_day(self, day, month, year, station="", gui=None):
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
        
        print("Downloading: Year: %s Month: %s Day: %s " % (year, month, day))
        if gui:
            gui.update_idletasks()
            
        # print("Loading Data for Station:  %s" % self.station_name)
        # url = "http://www.wunderground.com/weatherstation/WXDailyHistory.asp?ID={station}&day={day}&month={month}&year={year}&graphspan=day&format=1"
        full_url = self.url.format(station=station, day=day, month=month, year=year)
        print("Download in progress from:")
        print(full_url)
        # Request data from wunderground data
        response = requests.get(full_url,
                                headers={'User-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'})
        data = response.text
        # remove the excess <br> from the text data
        data = data.replace('<br>', '')	
        # Convert to pandas dataframe
        df = pd.read_csv(io.StringIO(data), index_col=False)  # Python 2.7 StringIO.StringIO
		
        print(df.dtypes) # Debugging
		
        if len(df) == 0:
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
        
        # print("Observations: %i" % df.shape[0])
        # print(df1.dtypes)
        
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
        month = date.month
        year = date.year
        
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
        df = self.give_data_month(date)
        dates = np.array(map(give_dt_date, df['date']))  # Extract only the dates
        
        df = df[dates == date]  # Compare to wished date; not minor information
        
        if len(df) == 0:
            warnings.warn("Error: Data Set not found!!", RuntimeWarning)
        return df
    
    def give_daily_maximum_month(self, date, column="temp", minimum=False):
        '''Gives the maximum amount per day.
        date: Which Month. Datetime Object
        column: Which Data column to use
        min=True give minmum
        Return Numpy Array'''
        df = self.give_data_month_clean(date)
        col = df[column]
        
        # Get all Days in month
        year = date.year
        month = date.month
        num_days = calendar.monthrange(year, month)[1]  # Number of days of Month
        days = [datetime.date(year, month, day) for day in range(1, num_days + 1)]
        
        res_vec, _ = self.give_daily_max(datetime.date(year, month, 1), datetime.date(year, month, num_days),
                            column=column, minimum=minimum)
            
        return np.array(res_vec)
    
    def give_tot_rain(self, date, column="total_rain", gui=None):
        '''Give maximum rain for a day
        date: Which day - Datetime Object'''
        print("Loading Rain from: %s" % str(date))
        
        rain_vals = self.give_data_day_clean(date)[column]
        
        if len(rain_vals) != 0:
            max_rain = np.max(rain_vals)  # Gets the Maximum of total Rain
            print("Max Rain: %.2f" % max_rain)
        else:
            max_rain = -0.1  # Default rain value to -1.
        
        if gui:
            gui.update_idletasks()
            
        return max_rain
    
    def give_tot_solar(self, date, column="solar"):
        '''Gives Integrated total solar Radiation per Day'''
        df = self.give_data_day_clean(date)
        solar_vals = df[column].values
        # solar_vals = self.give_data_day_clean(date)[column].values
        time_points = self.give_data_day_clean(date)["date"]
        
        if len(solar_vals) != 0:
            mid_bin_solar = (solar_vals[1:] + solar_vals[:-1]) / 2.0  # Linear Interpolation
            times = np.array(map(give_dt_object, time_points), dtype="object")
            delta_time_points = times[1:] - times[:-1]
            second_delta = np.array([x.total_seconds() for x in delta_time_points], dtype="float")
            # Measures time Difference in Hours and kilo watt
            tot_solar = np.sum(second_delta * mid_bin_solar) / (1000.0 * 3600.0)
            
            
        else:
            tot_solar = -0.1  # Default rain value to -1.
        return tot_solar
    
    def give_days_mean(self, start_date, end_date, column="total_rain"):
        '''Give daily means between Start and End Date.
        Return Day as well as Mean array.'''
        day_array = self.dates_between(start_date, end_date)
        mean_array = np.array([self.give_day_mean(date, column) for date in day_array])
        return day_array, mean_array
        
        
        
    def give_day_mean(self, date, column=""):
        '''Gives the daily mean of a Value (For instance Temperature)'''
        df = self.give_data_day_clean(date)
        vals = df[column].values
        t = df["date"]
        
        # Calculate the means
        if len(vals) != 0:
            mid_vals = (vals[1:] + vals[:-1]) / 2.0  # Linear Interpolation
            times = np.array(map(give_dt_object, t), dtype="object")
            delta_time_points = times[1:] - times[:-1]  # Calculate bin lengths
            second_delta = np.array([x.total_seconds() for x in delta_time_points], dtype="float")
            
            tot_sec = np.sum(second_delta)
            max_period = np.max(second_delta)  # Check wether not too big interval missing
            
            if not (75000 < tot_sec < 86401):  # Check whether enough total seconds
                print(tot_sec)
                warnings.warn("Something seems wrong with total seconds!", RuntimeWarning)
                mean_val = np.nan
            
            elif max_period > 7200:  # More than one hour is missing!
                print("Too big timeinterval: %.2f" % max_period)
                warnings.warn("Too big time interval!", RuntimeWarning)
                print(date)
                mean_val = np.nan
            
            # print("Total Seconds: %.2f" % tot_sec)  # For debugging.
            else: 
                mean_val = np.sum(second_delta * mid_vals) / tot_sec  # Average Value
              
        else:
            raise RuntimeWarning("Data does not exist!!")
            print("For Date:")
            print(date)
            mean_val = np.nan  # Default rain value to -1.
        
        return mean_val
     
    def give_daily_max(self, date_start, date_end, column="total_rain", minimum=False, gui=None):
        '''Return daily maximum for given period.
        Give back Numpy Array and array of days'''
        days_between = self.dates_between(date_start, date_end)
        
        # Get maximum/minimum per day:
        # Load all daily column Data into vector:
        print("Loading Data between: %s and %s" % (str(date_start), str(date_end)))
        
        if gui:
            gui.update_idletasks()
            
        day_data_vec = [self.give_data_day_clean(day)[column] for day in days_between]
        
        if minimum == True:
            res_vec = [np.min(day_data) for day_data in day_data_vec]
            
        elif minimum == False:
            res_vec = [np.max(day_data) for day_data in day_data_vec]
            
        else:
            raise ValueError("Min. must be Boolean!!")
        
            
        return np.array(res_vec), np.array(days_between)  # Return the Results and the days
        
        
    def give_daily_rain(self, date_start, date_end, gui=None):
        '''Give daily rain in Period from date_start to date_end.
        Return numpy array
        
        date_start: Start of the Period
        date_end: End of the Period.
        If month; take date_start and date_end from there'''
        
        # Create Date Vector: From Beginning to End
        
        # If Month given; overwrite start/end days:
            
        days_between = self.dates_between(date_start, date_end)
    
        # Extract Total Rain Vector:
        rain_tots = [self.give_tot_rain(date, gui=gui) for date in days_between]
        return days_between, rain_tots
    
    def give_daily_solar(self, date_start, date_end):
        '''Give daily integrated Sunshine in Period from date_start to date_end.
        Return date array and numpy array
        
        date_start: Start of the Period
        date_end: End of the Period.
        If month; take date_start and date_end from there'''
        days_between = self.dates_between(date_start, date_end)
    
        # Extract Total Rain Vector:
        solar_tots = np.array([self.give_tot_solar(date) for date in days_between], dtype="float")
        return days_between, solar_tots
    
    def dates_between(self, d1, d2):
        '''Return Array of Dates between d1 and and d2
        d1, d2: Datetime Objects'''
        delta = d2 - d1  # timedelta
        days_between = [d1 + datetime.timedelta(days=i) for i in range(delta.days + 1)]
        return days_between

        
    @clean_data
    def give_data_day_clean(self, date):
        '''Extract a Day cleaned up'''
        return self.give_data_day(date)
    
#################################
class SummaryData(object):
    '''Class that calculates and loads
    Summary Statistics from Data for every Day/Month/Year
    Data is stored in csv.tables that are accessed via Pandas.
    Columns: DayMinT, DayMaxT, DayMeanT, DayTotR, DayTotS
    
    It is different than Weatherdata; as here processed Data is looked into.
    
    '''
    local_folder = "./Data/Summary/"  # Where to find the data
    fn_last_updated = "last_updated.p"  # Name of File that saves when there was the last update
    local_file_name_days = "/sum_days.csv"
    local_file_name_months = "/sum_months.csv"
    local_file_name_years = "/sum_years.csv"
    
    last_date = 0  # Last date for which data is available
    
    # The Default Values for first Data
    first_year = 2017
    first_month = 5
    
    last_data = ""
    
    wd = 0  # The Weather station data.

    def __init__(self, wd):
        '''Initializes the Class. If nothing passed default to Harald's WS;
        but can also be run for other WS'''
        self.wd = wd  # 
        assert(self.wd.station_name == "IDRSING3")  # Check wether it is my whether Station
        
    def update_sum_days(self):
        '''Updates Summary Statistics since last day'''
        # Find out last day save
        last_save_date = self.load_last_date()
        
        # Find out last day of data
        last_data_date = wd.load_last_date()
        
        
        # Assert Last day > Last Day Save
        assert(last_save_date <= last_data_date)
        
        # Calculate Summary Statistics for inbetween
        new_summary_stats = calculate_summary_statistics_day()
        
        # Add them to Pandas Data Table
        
        
        # Save Everything
        save_last_date(date=last_data_date)
        
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
    
    
    def calculate_summary_statistics_day(self, start_date, end_date):
        '''Calculate Summary Statistics Day'''
        raise NotImplementedError("Implement this!")
        
    def give_summary_statistics_day(self, start, end_date, column):
        '''Load Summary Statistics Day. Give back array.'''
        raise NotImplementedError("Implement this!")
        
    def calculate_summary_statistics_year(self, start_date, end_date):
        '''Calculate Summary Statistics Year'''
        raise NotImplementedError("Implement this!")
    
    def give_summary_statistics_year(self, start_date, end_date, column="Total"):
        '''Load Summary Statistics Year. Give back array.'''
        raise NotImplementedError("Implement this!")
        


#################################
if __name__ == "__main__":
    date = datetime.date(year=2017, month=6, day=1)
# Test the Class:
    wd = WeatherData()
    # wd.update_local(all=1)
    # wd.update_local()
    # df=wd.give_data_month(date)
    # df = wd.give_data_month_clean(date)
    df = wd.give_data_day_clean(date)
    
    
    plt.figure()
    plt.plot(df["temp"], 'ro')
    plt.show()
    print(df.head(10))
    df = wd.give_data_day_clean(date)
    print(df[:2])
    solar_vals = df["solar"].values
    # solar_vals = self.give_data_day_clean(date)[column].values
    
    print(solar_vals[0])
    print(type(solar_vals[0]))
    # print(np.shape(df))
    # wd.download_data_day(1, 5, 2017)
    # data = wd.give_clean_data()
    # print(data.head(1))

    
        
