#!/bin/python

#
# script to pre-process sign data into normalized form
# very specific to the file format the sign generates
# 2015 kg
#

import os
import csv
import datetime
import sys

dir = sys.argv[1]
csv_output_filename = "all_data.csv"
csv_write_file = open(csv_output_filename, 'ab')

def dow(date):
    days=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    dayNumber=date.weekday()
    return days[dayNumber]

def makedate(file_name, time_stamp):
    ''' makes a date string out of the filename based on convention '''
    if ':' in time_stamp:
        date_string = file_name.split('.')[0].split('DS')[1]+' '+time_stamp
        date_object = datetime.datetime.strptime(date_string, '%y%m%d %H:%M')
        return date_object
    else:
        return None

for root, dirs, files in os.walk(dir):
    for file in files:
        if file.endswith(".csv"):

            f = open(os.path.join(root, file), 'r')

            csv_file = csv.reader(f, delimiter=',', quotechar='|')
            csv_output_file = csv.writer(csv_write_file, delimiter=',', quotechar='|')

            for row in csv_file:

                thedate = makedate(file, row[0])

                # lets make a new csv with the correct stuff
                if thedate:
                    newrow = []
                    newrow.append(str(thedate))
                    newrow.append(str(thedate.weekday()))
                    newrow.append(str(dow(thedate)))
                    newrow.append(str(thedate.strftime("%H")))
                    newrow.append(str(dir))
                    for i in range(1,5):
                        newrow.append(row[i])
                    csv_output_file.writerow(newrow)

            f.close()
