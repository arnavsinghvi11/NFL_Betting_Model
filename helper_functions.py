from bs4 import BeautifulSoup
import datetime
from datetime import datetime
from datetime import timedelta
import os
import pickle
import pytz
from pytz import timezone
import requests

def abbrv(col):
    if ' ' in col:
        col = col.split(' ')[0][0] + '.' + col.split(' ')[1]
    return col

def load_files(directory, suffixes, prefix):
    data = {}
    for suffix in suffixes:
        with open(f'{directory}{prefix}{suffix}.pkl', 'rb') as f:
            data[suffix] = pickle.load(f)
    return data

def create_folders(directory, month, date_counter):
    month_folder = os.path.join(directory, str(month))
    if not os.path.exists(month_folder):
        os.makedirs(month_folder)
    day_folder = os.path.join(month_folder, str(date_counter))
    if not os.path.exists(day_folder):
        os.makedirs(day_folder)
    return month_folder, day_folder

def calculate_payout(row):
    odds = row['Odds']
    units = row['Units']
    if int(odds) > 0:
        multiplier = (int(odds) / 100) + 1
    else:
        multiplier = (-100 / int(odds)) + 1
    return float(float(multiplier) * float(units))

def site_scrape(url):
    headers = requests.utils.default_headers()
    headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
    })
    page = requests.get(url, headers = headers)
    soup = BeautifulSoup(page.content, "html.parser")
    return soup