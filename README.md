# wunderground

Program to analyze weather station data

@ All rights reserved, Harald Ringbauer


The main App with Gui can be started with
python3 app.py

It has fields for
Dowloading data (wd)
Processing data (sd)
Visualizing data (v_wd)


The general stream of data:
Data is downloaded until current day, from saved Day
(into Data/YYYY/M.csv)

Data is process unitl current month, from saved Day (Month)
(into Data/Summary/yyyy.csv)
