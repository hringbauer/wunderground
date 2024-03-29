# Never give up my son. Trust your instincts.

'''
Created on May 6th, 2017
Class that analyzes and visualizes WunderGround data.
Access it over a wunderground data object;
data has methods to give the raw data (as PandasFrames)
'''

import numpy as np
import pandas as pd
from io import StringIO
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
import matplotlib.cm as cm
from matplotlib.dates import DateFormatter


class Analyze_WD(object):
    '''
    Created on May 6th, 2017
    Class that locally analyzes the Data from Wunderground.
    Stores WeatherData object that has methods to access the data and
    can give it
    '''
    wd = 0  # For the exact Data
    sd = 0  # For the statistical Data
    gui = 0  # For the GUI

    def __init__(self, wd, sd=None, gui=None):
        '''Initializes the Class. If nothing passed default to Harald's WS'''
        self.wd = wd
        if sd:
            self.sd = sd
        if gui:
            self.gui = gui

    def visualize_day_data(self, date, column="temp"):
        '''Visualizes the Temperature for a given date.
        Date: datetime.date object'''
        print("Visualizing Day: %s" % str(date))
        df = self.wd.give_data_day_clean(date)

        # Extract Data
        temps = df[column]
        dates = df.index  # Extract the datetime objects
        # Fix for Python 3.
        dates = [matplotlib.dates.date2num(date) for date in dates]

        plt.figure()
        plt.title("Date: %s" % date)
        plt.plot_date(dates, temps, label=column)
        plt.legend(loc="upper right")
        plt.gca().xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
        plt.grid()
        plt.show()

    def visualize_data_month(self, date, column="temp", minimum=False):
        '''Function that visualizes rain data of a given Month
        in a heat map Form'''
        rain_vec = self.wd.give_daily_maximum_month(
            date, column=column, minimum=minimum)
        print(rain_vec)
        print(len(rain_vec))

    def visualize_max_min_month(self, date, column="temp"):
        '''Plot Minimum and Maximum of a given Month '''
        print("Getting Mins...")

        mins = self.wd.give_daily_maximum_month(date, column=column, minimum=1)

        print("Getting Maxs...")
        maxs = self.wd.give_daily_maximum_month(date, column=column, minimum=0)

        days = np.arange(len(maxs)) + 1

        plt.figure()
        plt.plot(days, mins, "bo", label="Minimum")
        plt.plot(days, maxs, "ro", label="Maximum")
        plt.title("Date: %s" % date)
        plt.xlabel("Day")
        plt.ylabel(column)
        plt.xticks(days)
        plt.legend()
        plt.show()

    def visualize_rain_month(self, date_start=0, date_end=0, date_month=0):
        '''Visualize the monthly rain in form of a heatmap.
        start_date, end_date: Date Object.
        If month given; overwrite start_date and end_date'''

        # 0) If month given; update start_date and end_date
        date_start, date_end = get_month_start_end(date_month)

        # 1) Load the Rain
        dates, rain_tots = self.wd.give_daily_rain(date_start, date_end)
        rain_tots = np.array(rain_tots, dtype="float")
        # for i in range(len(rain_tots)):
        #    print("%s: %.1f ml" % (dates[i], rain_tots[i]))
        x_vec = range(1, len(dates) + 1)

        # Plot the Rain
        plt.figure(figsize=(10, 5))
        ax = plt.gca()
        rects1 = ax.bar(x_vec, rain_tots, width=0.8)
        ax.set_ylabel("Rain Amount [ml]", fontsize=14)
        ax.set_xlabel("Day", fontsize=14)
        ax.set_xticks(x_vec)
        ax.set_ylim([0, np.max(rain_tots) + 3])
        ax.set_title(date_start.strftime("%B %Y"), fontsize=14)
        ax.text(0.6, 0.85, 'Total Rain: %.1f ml' %
                np.sum(rain_tots), transform=ax.transAxes, fontsize=14)
        autolabel(rects1, ax)  # Puts the Label on
        plt.show()
        print("Done!!")

    def visualize_solar_month(self, date_start=0, date_end=0, date_month=0):
        '''Visualizes the solar Radiation of a Month.
        Depicts Integrals of Daily Values'''
        # 0) If month given; update start_date and end_date
        date_start, date_end = get_month_start_end(date_month)

        # 1) Load the Rain
        dates, solar_tots = self.wd.give_daily_solar(date_start, date_end)
        for i in range(len(solar_tots)):
            print("%s: %.1f kWh" % (dates[i], solar_tots[i]))
        x_vec = range(1, len(dates) + 1)

        # Do the Plot
        plt.figure(figsize=(10, 5))
        ax = plt.gca()
        rects1 = plt.bar(x_vec, solar_tots, width=0.8, color="yellow")
        ax.set_ylabel("Solar Radiation [kwH]", fontsize=14)
        ax.set_xlabel("Day", fontsize=14)
        ax.set_xticks(x_vec)
        ax.set_ylim([0, np.max(solar_tots) + 1.0])
        ax.set_title(date_start.strftime("%B %Y"), fontsize=14)
        ax.text(0.6, 0.85, 'Mean Solar Power: %.1f kwH' %
                np.mean(solar_tots), transform=ax.transAxes, fontsize=14)
        autolabel(rects1, ax)  # Puts the Label on
        plt.show()

    def visualize_records(self, date_start=0, date_end=0, date_month=0, date_year=0, minimum=False,
                          column="Temp"):
        '''Print and return the maximum Value of a given Period
        Minimum: Print and return Minimum'''

        if date_month:
            date_start, date_end = get_month_start_end(date_month)

        elif date_year:
            date_start, date_end = get_year_start_end(date_year)

        res, days = self.wd.give_daily_max(
            date_start, date_end, column=column, minimum=minimum)

        # Remove Days with missing data
        inds_fin = np.isfinite(res)
        res, days = res[inds_fin], days[inds_fin]

        if minimum:
            extreme = np.min(res)
            day = days[np.argmin(res)]

        else:
            extreme = np.max(res)
            day = days[np.argmax(res)]

        print("Extreme Value: %.4f" % extreme)
        print("On Day: %s" % day)

    def visualize_mean_month(self, date_month=None, start_date=None, end_date=None, column="rain", smoothing=False):
        '''Visualizes the mean Values per Month
        smoothing: Whether to use some form of smoothing (for instance lowess)'''

        # In case that month given - use it:
        if date_month:
            date_start, date_end = get_month_start_end(date_month)

        # Get the data:
        days, res = self.wd.give_days_mean(date_start, date_end, column=column)

        # Smooth Data (and produce middle Curve)

        # Give Text Output:
        for i in zip(days, res):
            print(i[0])
            print("%.3f" % i[1])

        # Visualize the data
        plt.figure()
        plt.plot(days, res, "ro", label="Daily Mean")
        plt.legend()
        plt.title("")
        # Plot Day Lines
        plt.title(date_month.strftime("%B %Y"), fontsize=18)
        plt.ylabel("Daily Mean of " + column, fontsize=14)
        plt.xlabel("Day", fontsize=14)
        ax = plt.gca()
        plt.text(0.6, 0.85, 'Mean Value: %.2f' %
                 np.nanmean(res), transform=ax.transAxes, fontsize=14)
        plt.show()

    ##############################################################
    ##############################################################
    # Visualize Statistics

    def visualize_temp_period(self, date_month=None, start_date=None, end_date=None, smoothing=False):
        """Visualize Temperature Data for a whole time period, from start o end_date"""
        if date_month:
            # Extract first and last day
            f, l = calendar.monthrange(date_month.year, date_month.month)
            start_date = date_month.replace(day=f)
            end_date = date_month.replace(day=l)

        df = self.sd.give_summary_statistics(start_date, end_date)
        # ["MinT", "MaxT", "MeanT", "TotR", "TotS"]

        dates = df.index

        plt.figure(figsize=(12, 6))
        plt.plot_date(dates, df.MinT, marker="o", linestyle="",
                      label="Min Temp", color="steelblue")
        plt.plot_date(dates, df.MeanT,  marker="o", linestyle="--",
                      label="Mean Temp", color="goldenrod")
        plt.plot_date(dates, df.MaxT, marker="o", linestyle="",
                      label="Max Temp", color="firebrick")
        plt.legend()
        plt.ylabel("Temp. [C]")
        plt.xlabel("Date")
        plt.show()

    def plot_monthdata_years(self, years=[2017, 2018, 2019], col="MeanT", cmap="viridis_r",
                         fs_l=14, figsize=(10, 5), xlabel="Month",
                         ylabel="Monthly Mean Temperature [C]", sum=False):
        """Plot monthly mean Temperature over the Years.
        years: Which years to plot
        cmap: What color to plot
        sum: If true plot sum rather than mean per month"""
        cmap = cm.get_cmap(cmap)
        cmap_i = np.linspace(0, 1, len(years))
        if sum:
            data_months = [self.sd.get_sum_month(year, col) for year in years]
        else:
            data_months = [self.sd.get_mean_month(year, col) for year in years]
        assert(len(data_months) > 0)   # Sanity Check

        x_vec = range(1, len(data_months[0]) + 1)  # x-Vector to Plot

        plt.figure(figsize=figsize)
        ax = plt.gca()
        ax.set_ylabel(ylabel, fontsize=fs_l)
        ax.set_xlabel(xlabel, fontsize=fs_l)

        for i, y in enumerate(years):
            ax.plot(x_vec, data_months[i].values, "o--",
                    c=cmap(cmap_i[i]), label=y, lw=1, ms=8)
            ax.set_xticks(x_vec)
        plt.legend(fontsize=fs_l, loc="upper left")
        plt.show()

##############################################################
##############################################################
# Some Helper Functions:
def get_month_start_end(date_month):
    '''Gets start and end date of a month.
    date: Date object of month. Return Start and
    End Date'''
    year = date_month.year
    month = date_month.month
    num_days = calendar.monthrange(year, month)[1]  # Number of days of Month
    date_start = datetime.date(year, month, 1)
    date_end = datetime.date(year, month, num_days)
    return date_start, date_end


def get_year_start_end(date_year):
    '''Get star and end of given year.
    Return first and last date.'''
    year = date_year
    date_start = datetime.date(year, 1, 1)
    date_end = datetime.date(year, 12, 31)
    return date_start, date_end


def autolabel(rects, ax):
    """
    Attach a text label above each bar displaying its height
    """
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width() / 2., 1.05 * height,
                '%.1f' % float(height),
                ha='center', va='bottom')


# Some testing functions:
if __name__ == "__main__":
    date = datetime.date(year=2017, month=5, day=27)

    wd = WeatherData()
    vis = Analyze_WD(wd)
    vis.visualize_day_data(date, column="pressure")
