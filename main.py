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

API_KEY = "AVDG281ETZSFEMEB"
demo_api_key = "demo"
dt_format = "%Y-%m-%d %H:%M:%S"
symbols_5min = ["AAPL", "TSLA", "AMZN", "MSFT", "FB"]
demo_symbol = ["AAPL"]
font1 = {'family':'serif','size':20}
font2 = {'family':'serif','size':14}

def get_5min_json(symbol):
  url = "https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=" + symbol + "&interval=5min&apikey=" + API_KEY
  print(symbol, "Data: ", url)
  return requests.get(url).json()

def extract_5min_values(raw_data): # Not currently used, but keep for reference
  package = {
      "dt": [],
      "value": []
  }
  useful_data = raw_data["Time Series (5min)"]
  prev_open = None
  for count, key in enumerate(useful_data):
    dt_obj = datetime.datetime.strptime(key, dt_format)
    if count == 0:
      # This is the first element
      package["dt"].append(dt_obj)
      package["value"].append(float(useful_data[key]["4. close"]))
    elif count+1 == len(useful_data):
      # This is the last element
      package["dt"].append(dt_obj)
      average_value = (float(useful_data[key]["4. close"]) + prev_open) / 2
      package["value"].append(average_value)
      # Now add the last (earliest) reading to the package
      package["dt"].append(dt_obj - timedelta(minutes=5))
      package["value"].append(float(useful_data[key]["1. open"]))
    elif count > 0:
      # All other elements
      package["dt"].append(dt_obj)
      average_value = (float(useful_data[key]["4. close"]) + prev_open) / 2
      package["value"].append(average_value)
    prev_open = float(useful_data[key]["1. open"])
  df = pd.DataFrame.from_dict(package)
  sorted_df = df.sort_values(["dt"])
  return sorted_df

def extract_5min_relative_values(raw_data):
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
      element_percentage = (float(useful_data[key]["4. close"]) - earliest_val)*100.0/earliest_val
      package["value"].append(element_percentage)
    elif count+1 == len(useful_data):
      # This is the last element
      package["dt"].append(dt_obj)
      average_value = ((float(useful_data[key]["4. close"]) - earliest_val)*100.0/earliest_val + prev_open) / 2
      package["value"].append(average_value)
      # Now add the last (earliest) reading to the package
      package["dt"].append(dt_obj - timedelta(minutes=5))
      package["value"].append((float(useful_data[key]["1. open"]) - earliest_val)*100.0/earliest_val)
    elif count > 0:
      # All other elements
      package["dt"].append(dt_obj)
      average_value = ((float(useful_data[key]["4. close"]) - earliest_val)*100.0/earliest_val + prev_open) / 2
      package["value"].append(average_value)
    prev_open = (float(useful_data[key]["1. open"]) - earliest_val)*100.0/earliest_val
  df = pd.DataFrame.from_dict(package)
  sorted_df = df.sort_values(["dt"])
  return sorted_df

def init_obj_plot():
  fig, ax = plt.subplots(figsize=(40, 15))
  return fig, ax

def update_obj_plot(fig, ax, sorted_values):
  ax.plot_date(sorted_values["dt"], sorted_values["value"], linestyle="solid", marker=None)
  # plt.ion()
  # plt.show()
  # plt.gcf().autofmt_xdate()

def get_title(raw_json):
  for count, key in enumerate(raw_json["Time Series (5min)"]):
    if count == 0:
      dt_obj = datetime.datetime.strptime(key, dt_format)
      title = dt_obj.strftime("%a, %-d %b %Y")
  return title

def format_obj_plot(title):
  date_format = mpl_dates.DateFormatter("%H:%M")
  plt.gca().xaxis.set_major_formatter(date_format)
  plt.title(title, fontdict=font1)
  plt.xlabel("Time", fontdict=font2)
  plt.ylabel("Percentage Change (%)", fontdict=font2)
  plt.legend(symbols_5min, loc="best")


fig, ax = init_obj_plot()
for count, symbol in enumerate(symbols_5min):
    raw_5min_json = get_5min_json(symbol) # Unsorted
    sorted_values = extract_5min_relative_values(raw_5min_json) # Sorted
    update_obj_plot(fig, ax, sorted_values)
    # if count == 0:
        # title = get_title(raw_5min_json) # Latest data point is taken for date
    format_obj_plot("Title")
# plt.show()
print(sorted_values)
  
