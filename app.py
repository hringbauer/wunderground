'''
Created on 24.12.2017
This is the main App; where everything comes together.
Uses a subclass of tkinter to have a GUI!!
@author: Harald Ringbauer
'''

from load_data import WeatherData2, SummaryData
from visualize_data import Analyze_WD
import numpy as np
import datetime
import tkinter as tk  # change to Python 3
from tkinter import messagebox, ttk
import sys


#######################################
#######################################
def doNothing():
    '''A small Testing Function'''
    print("DO NOTHING LINK. I AM LAZY")


class DatWunderApp(tk.Tk):
    '''The Graphic Interface for the Wunder App.'''
    wd = 0  # The Data Object
    sd = 0  # The Summary Statistics Object
    v_wd = 0  # The Visualization Object
    status_text = ""  # The Status Text

    def __init__(self):
        tk.Tk.__init__(self)

        # Load the Data and visualization Objects
        self.wd = WeatherData2(gui=self)  # Load the Data
        # Create The Statistics Object
        self.sd = SummaryData(self.wd, gui=self)
        # Create the Analysis Object
        self.v_wd = Analyze_WD(self.wd, sd=self.sd, gui=self)

        # Set Window Properties
        self.title("DatWunder by Harald")
        self.minsize(400, 300)  # Minimal Size
        self.geometry("700x500")  # Set it straight away

        # Set the Status Text
        self.status_text = tk.StringVar()
        self.status_text.set("Waiting")

        # ## Create the Menu
        menu = tk.Menu(self)
        self.config(menu=menu)

        # ##
        ### The Main Dropdown Menu ###
        dataMenu = tk.Menu(menu)
        menu.add_cascade(label="Data", menu=dataMenu)
        dataMenu.add_command(label="All Days", command=self.all)
        dataMenu.add_command(label="Load Month", command=self.load_month)
        dataMenu.add_command(label="Since Last Update",
                             command=self.lastupdate)
        dataMenu.add_command(label="Exit", command=quit)

        # subMenu.add_command(label="Exit", command=doNothing)

        ### The Summary Statistics Menu ###
        summstat_Menu = tk.Menu(menu)
        menu.add_cascade(label="Statistics", menu=summstat_Menu)
        summstat_Menu.add_command(
            label="Calculate Statistics", command=self.calc_summary)
        summstat_Menu.add_command(
            label="Since Last Update", command=self.calc_summary_update)
        dataMenu.add_separator()  # Creates a Line

        ### The Visualization Menu ###
        visMenu = tk.Menu(menu)  # Create Visualization Menu
        menu.add_cascade(label="Visualization", menu=visMenu)
        visMenu.add_command(label="Monthly Rain Plot",
                            command=self.monthly_rain)
        visMenu.add_command(label="Monthly Sun Plot", command=self.monthly_sun)
        visMenu.add_command(label="Stats Month Print",
                            command=self.print_summary_month)
        visMenu.add_command(label="Stats Year Print",
                            command=self.print_summary_year)

        visMenu.add_separator()  # Creates a Line
        visMenu.add_command(label="Max/Min per Month Plot",
                            command=self.maxminmonth)
        visMenu.add_command(label="Temperature Single Day Plot",
                            command=self.daytemp)
        visMenu.add_command(label="Temperature Period Plot",
                            command=self.period_temp)
        visMenu.add_separator()  # Creates a Line
        visMenu.add_command(label="Print Records", command=self.records)
        visMenu.add_separator()  # Creates a Line
        visMenu.add_command(label="Mean Month Temp (over years)",
                            command=self.mean_monthtemp)
        visMenu.add_command(label="Sum Month Rain (over years)",
                            command=self.sum_monthrain)
        visMenu.add_command(label="Sum Month Sun (over years)",
                            command=self.sum_monthsun)

        ### The Text Output ###
        self.text = tk.Text(self, wrap="word")
        self.text.pack(side="top", fill="both", expand=True)
        self.text.tag_configure("stderr", foreground="#b22222")

        sys.stdout = TextRedirector(self.text, "stdout")
        sys.stderr = TextRedirector(self.text, "stderr")

        ### Toolbar ###
        toolbar = tk.Frame(self, bg="cyan")
        insert_butt = tk.Button(
            toolbar, text="Insert Image", command=doNothing)
        insert_butt.pack(side=tk.LEFT, padx=2, pady=2)
        insert_butt2 = tk.Button(toolbar, text="Print", command=doNothing)
        insert_butt2.pack(side=tk.LEFT, padx=2, pady=2)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        ### Status Bar ###
        status = tk.Label(self, textvariable=self.status_text,
                          bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status.pack(side=tk.BOTTOM, fill=tk.X)

    ###################
    # Functions for the Menu
    def lastupdate(self):
        self.set_status_text("Loading the Data")
        self.wd.update_local()
        # Recreate the Analysis Object
        self.v_wd = Analyze_WD(self.wd, self.sd)
        self.set_status_text("Completed")

    def load_month(self):
        self.set_status_text("Loading the Data of Month")

        month = self.get_month()
        self.wd.local_save_month(month)
        # Recreate the Analysis Object
        self.v_wd = Analyze_WD(self.wd, self.sd)
        self.set_status_text("Completed")

    def all(self):
        self.wd.update_local(all=1)
        # Recreate the Analysis Object
        self.v_wd = Analyze_WD(self.wd, self.sd)

    def monthly_rain(self):
        self.set_status_text("Loading the Data...")
        date = self.get_month()
        self.v_wd.visualize_rain_month(date_month=date)
        self.set_status_text("Waiting")
        print("Here!!")

    def monthly_sun(self):
        self.set_status_text("Loading the Data...")
        date = self.get_month()
        self.v_wd.visualize_solar_month(date_month=date)
        self.set_status_text("Waiting")

    def maxminmonth(self):
        self.set_status_text("Loading the Data...")
        date = self.get_month()
        dtype = self.get_data_type()
        self.v_wd.visualize_max_min_month(date, column=dtype)
        self.set_status_text("Waiting")

    def meanpermonth(self):
        self.set_status_text("Loading the Data...")
        date = self.get_month()
        dtype = get_data_type()
        self.v_wd.visualize_mean_month(date_month=date, column=dtype)
        self.set_status_text("Waiting...")

    def daytemp(self):
        date = self.get_day()  # Get the Date (via Input)
        self.v_wd.visualize_day_data(date, column="temp")

    def period_temp(self):
        sdt = self.get_day()
        edt = self.get_day()
        self.v_wd.visualize_temp_period(start_date=sdt, end_date=edt)

    def records(self):
        self.set_status_text("Loading the Data...")
        date = self.get_month()
        minimum = self.ask_minimum()
        dtype = self.get_data_type()
        self.v_wd.visualize_records(date_month=date, date_year=0, minimum=minimum,
                                    column=dtype)
        self.set_status_text("Waiting...")

    def mean_monthtemp(self):
        self.set_status_text("Loading the Data...")
        years = self.get_year_range()
        self.v_wd.plot_monthdata_years(years=years, col="MeanT",
                                       ylabel="Monthly Mean Temperature [C]", sum=False)
        self.set_status_text("Waiting...")

    def sum_monthrain(self):
        self.set_status_text("Loading the Data...")
        years = self.get_year_range()
        self.v_wd.plot_monthdata_years(years=years, col="TotR",
                                       ylabel="Monthly Sum Rain [ml]", sum=True)
        self.set_status_text("Waiting...")

    def sum_monthsun(self):
        self.set_status_text("Loading the Data...")
        years = self.get_year_range()
        self.v_wd.plot_monthdata_years(years=years, col="TotS",
                                       ylabel="Monthly Sum Sun [kwH]", sum=True)
        self.set_status_text("Waiting...")

    def print_summary_year(self):
        """Print Summary Statistics of one Year"""
        self.set_status_text("Loading the Data...")
        year = int(self.get_input(["Year [YYYY]"])[0])
        start_date = datetime.date(year, 1, 1)
        end_date = datetime.date(year, 12, 31)
        self.sd.give_stats_period(start_date, end_date, prt=True)
        self.set_status_text("Waiting...")

    def print_summary_month(self):
        """Print Summary Statistics of one Year"""
        self.set_status_text("Loading the Data...")
        vals = self.get_input(["Year [YYYY]", "Month [M]"])
        year, month = int(vals[0]), int(vals[1])
        start_date = datetime.date(year, month, 1)
        end_date = datetime.date(year, month + 1, 1) - \
            datetime.timedelta(days=1)
        self.sd.give_stats_period(start_date, end_date, prt=True)
        self.set_status_text("Waiting...")

    ###################
    # Summary Statistics

    def calc_summary(self):
        """Calculate Summary Stats between two days"""
        self.set_status_text("Calculating Summary Statistics...")
        self.pb = ttk.Progressbar(self, orient="horizontal",
                                  length=350, mode="determinate")  # Make progressbar
        self.pb.pack()
        
        ### Input
        beg_date = self.get_day()
        end_date = self.get_day()
        
        ### Do the job
        self.sd.set_summary_statistics(beg_date, end_date)
        print("Test successful. YOU ROCK HARALD")
        
        ### Destroy Progress Bar
        self.pb.destroy()  # Delete Progressbar
        self.set_status_text("Waiting...")

    def calc_summary_update(self):
        self.set_status_text(
            "Calculating Summary Statistics since last update...")
        self.pb = ttk.Progressbar(self, orient="horizontal",
                                  length=350, mode="determinate")  # Make progressbar
        self.pb.pack()

        self.sd.update_sum_days()
        print("Test successful. YOU ROCK HARD HARALD")
        self.pb.destroy()  # Delete Progressbar
        self.set_status_text("Waiting...")

    ###################
    # User Input Functions

    def get_data_type(self):
        '''Call Window for which Datatype'''
        options = ["temp", "total_rain"]

        popup = SelectionWindow(self, texts=options)
        self.wait_window(popup.top)
        dtype = str(popup.val.get())  # Reads out the String Variable
        return dtype

    def ask_minimum(self):
        '''Window to ask for the Minimum'''
        options = ["Minimum", "Maximum"]

        popup = SelectionWindow(self, texts=options)
        self.wait_window(popup.top)
        val = str(popup.val.get())  # Reads out the String Variable

        if val == "Minimum":
            minimum = 1
        elif val == "Maximum":
            minimum = 0

        return minimum

    def get_month(self):
        '''Input for year/month'''
        texts = ["Year", "Month"]
        popup = PopupWindow(self, texts=texts)
        # Wait until TopLevel of Widget is destroyed
        self.wait_window(popup.top)
        vals = popup.values
        return datetime.date(year=int(vals[0]), month=int(vals[1]), day=1)

    def get_input(self, texts=[]):
        '''Input for as many fields as in texts (array)
        By default return these values'''
        if len(texts) == 0:
            texts = ["Begin Year", "End Year"]
        popup = PopupWindow(self, texts=texts)
        # Wait until TopLevel of Widget is destroyed
        self.wait_window(popup.top)
        return popup.values

    def get_year_range(self):
        """Get continuous array of years from Input"""
        vals = self.get_input(["Begin Year [YYYY]", "End Year [YYYY], incl."])
        years = np.arange(int(vals[0]), int(vals[1]) + 1)
        return years

    def get_day(self):
        '''Run Window for Day Input'''
        texts = ["Year", "Month", "Day"]
        popup = PopupWindow(self, texts=texts)
        # Wait until TopLevel of Widget is destroyed
        self.wait_window(popup.top)
        vals = popup.values
        return datetime.date(year=int(vals[0]), month=int(vals[1]), day=int(vals[2]))

    ###################
    # Status Functions

    def set_status_text(self, text):
        '''Method to set the Status Text'''
        self.status_text.set(text)
        self.update_idletasks()

################################################################


class TextRedirector(object):

    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, str):
        self.widget.configure(state="normal")
        self.widget.insert("end", str, (self.tag,))
        self.widget.configure(state="disabled")
        self.widget.see("end")
################################################################


################################################################
class PopupWindow(object):
    '''Pop Up Window for Input.
    Texts is array of strings of inputs'''
    k = 0  # Nr of Fields
    fields = 0  # Stores the Row Fields (Later on List)
    values = 0  # Stores the Entered Values after OK (Later on List)

    def __init__(self, master, texts):
        self.top = tk.Toplevel(master)
        self.k = len(texts)
        self.values = np.zeros(self.k)  # Create the Space for the Values
        self.fields = []

        for s in texts:
            self.l = tk.Label(self.top, text=s)
            self.l.pack(side=tk.TOP, fill=tk.X)
            self.fields.append(tk.Entry(self.top))
            self.fields[-1].pack(side=tk.TOP, fill=tk.X)

        self.b = tk.Button(self.top, text='Enter', command=self.enter)
        self.b.pack(side=tk.TOP)

    def enter(self):
        for i in range(self.k):
            self.values[i] = self.fields[i].get()  # Stores the Values
        self.top.destroy()  # Closes the Dialog Window
################################################################


class SelectionWindow(object):
    '''Pop Up Window for Input.
    Texts is array of strings of inputs'''
    k = 0  # Nr of Fields
    rb = 0  # Stores the Row Fields (Later on List)
    val = 0  # The Selected String Variable

    def __init__(self, master, texts):
        self.top = tk.Toplevel(master)
        self.k = len(texts)
        self.val = tk.StringVar()

        for s in texts:
            self.rb = tk.Radiobutton(
                self.top, text=s, variable=self.val, value=s)
            self.rb.pack(side=tk.TOP, fill=tk.X)

        # The Button for Enter
        self.b = tk.Button(self.top, text='Enter', command=self.enter)
        self.b.pack(side=tk.TOP)

    def enter(self):
        self.top.destroy()  # Closes the Dialog Window


#################################################################
# ## Call the main loop
if __name__ == "__main__":
    print("Starting the App :-)")
    app = DatWunderApp()
    app.mainloop()
    print("Ending the App :-(")
