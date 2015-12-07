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

    # convert to specially formatted strings
    mean_speed_l = [str(i) for i in list(mean_speed.get_values())]
    max_speed_l = [str(i) for i in list(max_speed.get_values())]

    keys_l = [str(i) for i in list(keys)]

    mean_speed_str = ','.join(mean_speed_l)
    max_speed_str = ','.join(max_speed_l)
    keys_str = ",".join(keys_l)

    return [keys_str, mean_speed_str, max_speed_str]


@app.route("/")
def dashboard():
    df = get_raw_data()
    violator_pct = round((get_violator_count(df)/get_vehicle_count(df)*100), 2)
    violator_graph = get_timeseries_by_year(df)
    speed_graph = get_speed_by_hour(df)

    return render_template('index.html',
                    car_count=get_vehicle_count(df),
                    violator_count=get_violator_count(df),
                    violator_pct=violator_pct,
                    max_speed=get_max_speed(df),
                    avg_speed=get_avg_speed(df),
                    ts_labels=violator_graph[0],
                    ts_vehicle=violator_graph[1],
                    ts_violator=violator_graph[2],
                    ts_speed_labels=speed_graph[0],
                    ts_mean_speed_data=speed_graph[1],
                    ts_max_speed_data=speed_graph[2]
                    )

if __name__ == "__main__":
    app.run()
