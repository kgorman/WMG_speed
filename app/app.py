#!/usr/bin/env python

from flask import Flask
from flask import render_template
import pandas as pd
import numpy as np
import datetime as datetime

app = Flask(__name__)

if not app.debug:
    import logging
    file_handler = logging.FileHandler('error.log')
    file_handler.setLevel(logging.WARNING)
    app.logger.addHandler(file_handler)


def int_to_dow(dayno):
    """ convert an integer into a day of week string """
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday',
            'Sunday']
    return days[int(dayno)]


def create_graph_strings(input_list):
    return None


def get_raw_data():
    file_name = "static/files/all_data.csv"
    dataframe = pd.read_csv(file_name, header=0)
    dataframe['date'] = pd.to_datetime(dataframe['date'])
    return dataframe


def get_max_speed(df):
    return float(max(df['peak_speed']))


def get_vehicle_count(df):
    return float(sum(df['vehicle_count']))


def get_violator_count(df):
    return float(sum(df['violator_count']))


def get_avg_speed(df):
    theavg = np.mean(df['peak_speed'])
    return round(theavg, 2)

def get_over_limit(df):
    theavg = get_avg_speed(df)
    return (30-theavg)*-1


def get_timeseries_by_year(df):
    ''' group by keys, then return strings suitable for graphing '''
    df['year'] = df.date.map(lambda x: '{year}'.format(year=x.year))
    grouped = df.sort(['year'], ascending=1).groupby(['year'])
    vehicle_count_by_month = grouped.aggregate(np.sum)['vehicle_count']
    violator_count_by_month = grouped.aggregate(np.sum)['violator_count']
    keys = vehicle_count_by_month.index.get_values()

    # convert to specially formatted strings
    vehicle_count_by_month_l = [str(i) for i in list(vehicle_count_by_month.get_values())]
    violator_count_by_month_l = [str(i) for i in list(violator_count_by_month.get_values())]
    keys_l = [str(i) for i in list(keys)]

    vehicle_count_by_month_str = ','.join(vehicle_count_by_month_l)
    violator_count_by_month_str = ','.join(violator_count_by_month_l)
    keys_str = ",".join(keys_l)

    return [keys_str, vehicle_count_by_month_str, violator_count_by_month_str]


def get_speed_by_hour(df):
    grouped = df.sort(['hour_of_day'], ascending=1).groupby(['hour_of_day'])
    mean_speed = grouped.aggregate(np.mean)['peak_speed']
    max_speed = grouped.aggregate(np.max)['peak_speed']
    keys = mean_speed.index.get_values()

    mean_speed_l = [str(i) for i in list(mean_speed.get_values())]
    max_speed_l = [str(i) for i in list(max_speed.get_values())]

    keys_l = [str(i) for i in list(keys)]

    mean_speed_str = ','.join(mean_speed_l)
    max_speed_str = ','.join(max_speed_l)
    keys_str = ",".join(keys_l)

    return [keys_str, mean_speed_str, max_speed_str]


def get_speed_by_day(df):
    grouped = df.sort(['weekday'], ascending=0).groupby(['weekday'])
    mean_speed = grouped.aggregate(np.mean)['peak_speed']
    max_speed = grouped.aggregate(np.max)['peak_speed']
    keys = mean_speed.index.get_values()

    mean_dow_l = [str(i) for i in list(mean_speed.get_values())]
    max_dow_l = [str(i) for i in list(max_speed.get_values())]

    dow_keys_l = [int_to_dow(i) for i in list(keys)]

    mean_speed_str = ','.join(mean_dow_l)
    max_speed_str = ','.join(max_dow_l)
    keys_str = "','".join(dow_keys_l)
    keys_str = "'"+keys_str+"'"

    return [keys_str, mean_speed_str, max_speed_str]

def car_count_by_hour(df):
    grouped = df.sort(['date'], ascending=0).groupby(['hour_of_day'])
    car_count = grouped.aggregate(np.mean)['vehicle_count']
    violator_count = grouped.aggregate(np.max)['violator_count']
    keys = car_count.index.get_values()

    car_count_l = [str(i) for i in list(car_count.get_values())]
    violator_count_l = [str(i) for i in list(violator_count.get_values())]

    keys_l = [str(i) for i in list(keys)]

    car_count_str = ','.join(car_count_l)
    violator_count_str = ','.join(violator_count_l)
    keys_str = ",".join(keys_l)

    return [keys_str, car_count_str, violator_count_str]


@app.route("/")
def dashboard():
    df = get_raw_data()
    violator_pct = round((get_violator_count(df)/get_vehicle_count(df)*100), 2)
    violator_graph = get_timeseries_by_year(df)
    speed_graph = get_speed_by_hour(df)
    dow_graph = get_speed_by_day(df)
    car_count_graph = car_count_by_hour(df)

    return render_template('index.html',
                    car_count=get_vehicle_count(df),
                    violator_count=get_violator_count(df),
                    violator_pct=violator_pct,
                    max_speed=get_max_speed(df),
                    avg_speed=get_avg_speed(df),
                    over_limit=get_over_limit(df),
                    ts_labels=violator_graph[0],
                    ts_vehicle=violator_graph[1],
                    ts_violator=violator_graph[2],
                    ts_speed_labels=speed_graph[0],
                    ts_mean_speed_data=speed_graph[1],
                    ts_max_speed_data=speed_graph[2],
                    ts_dow_labels=dow_graph[0],
                    ts_dow_mean=dow_graph[1],
                    ts_dow_max=dow_graph[2],
                    ts_car_count_labels=car_count_graph[0],
                    ts_car_count_count=car_count_graph[1],
                    ts_car_count_violators=car_count_graph[2]
                    )


@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/contact")
def contact():
    return render_template('contact.html')


if __name__ == "__main__":
    app.run(host=0.0.0.0)
