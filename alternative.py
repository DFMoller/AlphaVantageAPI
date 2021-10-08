from matplotlib import colors
import requests
import json
import matplotlib
import pandas as pd
import numpy as np
import scipy
import seaborn as sns
import datetime
import time
from datetime import timedelta
import matplotlib.pyplot as plt
from matplotlib import dates as mpl_dates
import collections
from matplotlib.animation import FuncAnimation

API_KEY = "AVDG281ETZSFEMEB"
demo_api_key = "demo"
dt_format = "%Y-%m-%d %H:%M:%S"
symbols_5min = ["AAPL", "TSLA", "GOOGL", "MSFT", "FB"]
demo_symbols = ["AAPL"]
# font1 = {'family': 'serif', 'size': 20, 'color': "#ffffff"}
# font2 = {'family': 'serif', 'size': 14}
current_date_format = "%Y-%m-%d"

def get_API_json(symbol):
    url = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=" + \
        symbol + "&interval=5min&apikey=" + API_KEY
    print(symbol, "Data: ", url)
    return requests.get(url).json()

def get_sorted_df(raw_data):
    useful_data = raw_data["Time Series (5min)"]
    last_refreshed = raw_data["Meta Data"]["3. Last Refreshed"]
    # Find Earliest Opening Value
    earliest_dt = None
    earliest_val = None
    for count, key in enumerate(useful_data):
        dt_obj = datetime.datetime.strptime(key, dt_format)
        if count == 0:
            earliest_dt = dt_obj
            earliest_val = float(useful_data[key]["1. open"])
        elif count > 0:
            if dt_obj < earliest_dt:
                earliest_dt = dt_obj
                earliest_val = float(useful_data[key]["1. open"])
    # print("Starting Value: ", str(earliest_val))
    package = {"dt": [], "value": []}
    prev_open = None
    for count, key in enumerate(useful_data):
        dt_obj = datetime.datetime.strptime(key, dt_format)
        if count == 0:
            # This is the first element
            package["dt"].append(dt_obj)
            element_percentage = (
                float(useful_data[key]["4. close"]) - earliest_val)*100.0/earliest_val
            package["value"].append(element_percentage)
        elif count+1 == len(useful_data):
            # This is the last element
            package["dt"].append(dt_obj)
            average_value = ((float(
                useful_data[key]["4. close"]) - earliest_val)*100.0/earliest_val + prev_open) / 2
            package["value"].append(average_value)
            # Now add the last (earliest) reading to the package
            package["dt"].append(dt_obj - timedelta(minutes=5))
            package["value"].append(
                (float(useful_data[key]["1. open"]) - earliest_val)*100.0/earliest_val)
        elif count > 0:
            # All other elements
            package["dt"].append(dt_obj)
            average_value = ((float(
                useful_data[key]["4. close"]) - earliest_val)*100.0/earliest_val + prev_open) / 2
            package["value"].append(average_value)
        prev_open = (
            float(useful_data[key]["1. open"]) - earliest_val)*100.0/earliest_val
    df = pd.DataFrame.from_dict(package)
    sorted_df = df.sort_values(["dt"])
    return sorted_df

def clean_data(sorted_df, current_date):
    cleaned_df = sorted_df
    for index, row in sorted_df.iterrows():
        # print(row["dt"])
        datapoint_date = row["dt"].strftime(current_date_format)
        if datapoint_date != current_date:
            cleaned_df = cleaned_df.drop(index)
            print("Data Point removed due to date mismatch: ", datapoint_date, " || ", current_date)
    return cleaned_df

def get_plotting_info(raw_json):
    for count, key in enumerate(raw_json["Time Series (5min)"]):
        if count == 0:
            dt_obj = datetime.datetime.strptime(key, dt_format)
            title_date = dt_obj.strftime("%A, %d %b %Y")
            current_date = dt_obj.strftime(current_date_format)
    return title_date, current_date

def draw_lines():

    # clear existing lines
    ax.cla()

    max_val = min_val = 0

    for count, symbol in enumerate(symbols_5min):

        # fetch updated data
        raw_json = get_API_json(symbol) # Unsorted

        # sort data and catch exception
        sorted_values = get_sorted_df(raw_json) # Sorted

        # get date and time for title
        if count == 0:
            title_date, current_date = get_plotting_info(raw_json)
            my_title = "Some stocks from the NYSE on " + title_date

        # clean data by dropping datapoints that do not match current_date
        cleaned_df = clean_data(sorted_values, current_date)

        # plot new data
        ax.plot(cleaned_df["dt"], cleaned_df["value"], linestyle="solid", marker=None, linewidth=3)
        plt.gca().xaxis.set_major_formatter(date_format)
        ax.title.set_text(my_title)
        ax.title.set_color("#ffffff")
        ax.set_ylabel("Percentage Change (%)")
        ax.set_xlabel("Time")
        ax.spines['bottom'].set_color('#ffffff')
        ax.spines['top'].set_color('#2C4051') 
        ax.spines['right'].set_color('#2C4051')
        ax.spines['left'].set_color('#ffffff')
        ax.tick_params(axis='x', colors="#ffffff")
        ax.tick_params(axis='y', colors='#ffffff')
        ax.yaxis.label.set_color("#ffffff")
        ax.xaxis.label.set_color("#ffffff")
        plt.legend(symbols_5min, loc="best", facecolor='#2C4051', edgecolor="#2C4051", labelcolor="#ffffff")

def try_plotting(i):
    try:
        draw_lines()
    except KeyError as e:
        if str(e) == "'Time Series (5min)'":
            print("Cannot make more than 5 api calls per minute! ", "-> KeyError: ", e)
            print("Waiting for 1 min...")
            time.sleep(60)
            draw_lines()
        else:
            raise


# define and adjust figure
fig = plt.figure(figsize=(12, 6), facecolor='#2C4051', clear=True)
ax = plt.subplot()
ax.set_facecolor('#2C4051')
date_format = mpl_dates.DateFormatter("%H:%M")


try_plotting(0)

# ani = FuncAnimation(fig, try_plotting, interval=(60000))
plt.show()