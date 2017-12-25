'''
Created on 24.12.2017
This is the main App; where everything comes together.
Uses a subclass of tkinter to have a GUI!!
@author: Harald Ringbauer
'''


from load_data import WeatherData
from visualize_data import Analyze_WD
import numpy as np
import datetime
import Tkinter as tk  # For the graphical user interface
import sys


#######################################
#######################################
def doNothing():
    '''A small Testing Function'''
    print("lolol")

class DatWunderApp(tk.Tk):
    '''The Graphic Interface for the Wunder App.'''
    wd = 0  # The Data Object
    v_wd = 0  # The Visualization Object
    status_text = ""  # The Status Text
       
    def __init__(self):
        tk.Tk.__init__(self)
        
        # Load the Data and visualization Objects
        self.wd = WeatherData()  # Load the Data
        self.v_wd = Analyze_WD(self.wd)  # Create the Analysis Object
        
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
        dataMenu.add_command(label="Since Last Update", command=self.lastupdate)
        dataMenu.add_command(label="Specific Date", command=self.specific_dates)
        dataMenu.add_separator()  # Creates a Line
        dataMenu.add_command(label="Exit", command=quit)
        
        # subMenu.add_command(label="Exit", command=doNothing)
        
        ### The Summary Statistics Menu ###
        summstat_Menu = tk.Menu(menu)
        menu.add_cascade(label="Statistics", menu=summstat_Menu)
        summstat_Menu.add_command(label="Placeholder", command=doNothing)
        
        ### The Visualization Menu ###
        visMenu = tk.Menu(menu)  # Create Visualization Menu 
        menu.add_cascade(label="Visualization", menu=visMenu)
        visMenu.add_command(label="Monthly Rain", command=self.monthly_rain)
        visMenu.add_command(label="Monthly Sun", command=self.monthly_sun)
        visMenu.add_separator()  # Creates a Line
        visMenu.add_command(label="Max/Min per Month", command=self.maxminmonth)
        visMenu.add_command(label="Day Temperature", command=self.daytemp)
        visMenu.add_separator()  # Creates a Line
        visMenu.add_command(label="Show Records", command=self.records)
        
        ### The Text Output ###
        self.text = tk.Text(self, wrap="word")
        self.text.pack(side="top", fill="both", expand=True)
        self.text.tag_configure("stderr", foreground="#b22222")

        sys.stdout = TextRedirector(self.text, "stdout")
        sys.stderr = TextRedirector(self.text, "stderr")
        
        ### Toolbar ###
        toolbar = tk.Frame(self, bg="cyan")
        insert_butt = tk.Button(toolbar, text="Insert Image", command=doNothing)
        insert_butt.pack(side=tk.LEFT, padx=2, pady=2)
        insert_butt2 = tk.Button(toolbar, text="Print", command=doNothing)
        insert_butt2.pack(side=tk.LEFT, padx=2, pady=2)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        ### Status Bar ###
        status = tk.Label(self, textvariable=self.status_text, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status.pack(side=tk.BOTTOM, fill=tk.X)
        
    # Write the Functions for the Menu
    def lastupdate(self):
        self.set_status_text("Loading the Data")
        self.wd.update_local(gui=self)
        self.v_wd = Analyze_WD(self.wd)  # Recreate the Analysis Object
        self.set_status_text("Completed")
        
    def all(self):
        self.wd.update_local(all=1, gui=self)
        self.v_wd = Analyze_WD(self.wd)  # Recreate the Analysis Object
    
    def specific_dates(self):
        raise NotImplementedError("Implement this!")
        
    
    def monthly_rain(self):
        self.set_status_text("Loading the Data...")
        date = self.get_month()
        self.v_wd.visualize_rain_month(date_month=date, gui=self)
        self.set_status_text("Waiting")
        print("Here!!")
        
    def monthly_sun(self):
        self.set_status_text("Loading the Data...")
        date = self.get_month()
        self.v_wd.visualize_solar_month(date_month=date, gui=self) 
        self.set_status_text("Waiting")
        
    def maxminmonth(self):
        self.set_status_text("Loading the Data...")
        date = self.get_month()
        dtype = self.get_data_type()
        self.v_wd.visualize_max_min_month(date, column=dtype, gui=self)
        self.set_status_text("Waiting")
        
    def meanpermonth(self):
        self.set_status_text("Loading the Data...")
        date = self.get_month()
        dtype = get_data_type()
        self.v_wd.visualize_mean_month(date_month=date, column=dtype)   
        self.set_status_text("Waiting...")
        
    def daytemp(self):
        date = self.get_day()  # Get the Date (via Input)
        self.v_wd.visualize_day_data(date, column="temp", gui=self)
        
    def records(self):
        self.set_status_text("Loading the Data...")
        date = self.get_month()
        minimum = self.ask_minimum()
        dtype = self.get_data_type()
        
        #minimum = int(input("Value? \n(0) Maximum \n(1) Minimum\n"))
        #print(minimum)
        
        self.v_wd.visualize_records(date_month=date, date_year=0, minimum=minimum,
          column=dtype, gui=self)
        self.set_status_text("Waiting...")
    
    def set_status_text(self, text):
        '''Method to set the Status Text'''
        self.status_text.set(text)
        self.update_idletasks()
        
        
    ####################
    def get_month(self):
        '''Input for year/month'''
        texts = ["Year", "Month"]
        popup = PopupWindow(self, texts=texts)
        self.wait_window(popup.top)  # Wait until TopLevel of Widget is destroyed
        vals = popup.values
        return datetime.date(year=int(vals[0]), month=int(vals[1]), day=1)
    
    def get_day(self):
        '''Run Window for Day Input'''
        texts = ["Year", "Month", "Day"]
        popup = PopupWindow(self, texts=texts)
        self.wait_window(popup.top)  # Wait until TopLevel of Widget is destroyed
        vals = popup.values
        return datetime.date(year=int(vals[0]), month=int(vals[1]), day=int(vals[2]))
        
    ###################
    
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
        
        if val =="Minimum":
            minimum = 1
        elif val == "Maximum":
            minimum = 0
        
        return minimum
        
        
    ###################
    
        
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
        for i in xrange(self.k):
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
            self.rb = tk.Radiobutton(self.top, text=s, variable=self.val, value=s)
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
    
    
    
    
