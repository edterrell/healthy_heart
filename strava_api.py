import requests
import json
import time
import os
from pprint import pprint
import pandas as pd
pd.set_option('display.precision', 1)

from IPython.core.display import HTML
css = open('style-table.css').read() + open('style-notebook.css').read()
HTML('<style>{}</style>'.format(css))

#import sys
#sys.executable

from token_manager import get_valid_access_token
import requests

access_token = get_valid_access_token()
print("Using access token:", access_token)

# Make an authenticated API call
response = requests.get(
    'https://www.strava.com/api/v3/athlete',
    headers={'Authorization': f'Bearer {access_token}'}
)
#print(response.json())

# Get recent activities
response = requests.get(
    'https://www.strava.com/api/v3/athlete/activities',
    headers={'Authorization': f'Bearer {access_token}'}
)
activities = response.json()
response.status_code

# Build out strava_df with only the necessary columns
strava_df = pd.DataFrame(activities)
cols_needed = ['id','name', 'distance', 'moving_time','total_elevation_gain', 'sport_type',
          'average_speed', 'average_heartrate','max_heartrate', 'suffer_score','start_date']
strava_df = strava_df.loc[:,cols_needed]

def cleanup (strava_df):
    """
    Clean and transform Strava activity DataFrame:
    - Convert start_date to datetime and extract date
    - Convert distance from meters to miles
    - Convert moving_time to minutes and add formatted time (hh:mm)
    - Convert elevation gain from meters to feet
    """
    # Change to datetime and create new date column
    strava_df.start_date = pd.to_datetime(strava_df.start_date) 
    strava_df['date'] = strava_df.start_date.dt.date
    # Change distance to miles
    strava_df['distance'] = strava_df['distance'] / 1609.34
    # Change moving time to minutes in new col: time
    strava_df['time'] = strava_df.moving_time/60
    # Convert to timedelta
    strava_df.moving_time = pd.to_timedelta(strava_df['moving_time'], unit='s')
    # Change to hours/minutes
    strava_df['moving_time'] = strava_df['moving_time'].apply(lambda td: f"{int(td.total_seconds() // 3600)}:{int((td.total_seconds() % 3600) // 60):02}")
    # Change to feet
    strava_df.total_elevation_gain = strava_df.total_elevation_gain*3.28084
    
    return strava_df

def convert_speed(row):
    if row['sport_type'] == 'Ride':
        return row['average_speed'] * 2.23694  # m/s to mph
    elif row['sport_type'] == 'Run':
        if row['average_speed'] > 0:
            pace_sec_per_mile = 1609.34 / row['average_speed']
            minutes = int(pace_sec_per_mile // 60)
            seconds = int(pace_sec_per_mile % 60)
            return f"{minutes}:{seconds:02d}"
        else:
            return "N/A"
    else:
        return None  # for other sports
    
# process data
cleanup (strava_df)

# add column: converted_speed -mph (ride) and -min/mile (run)
strava_df['converted_speed'] = strava_df.apply(convert_speed, axis=1)

# Reorder columns
new_order = ['id', 'name','date','sport_type',  'distance','moving_time', 'converted_speed', 
       'total_elevation_gain', 'average_heartrate', 'max_heartrate',
       'suffer_score', 'time','average_speed','start_date' ]

strava_df = strava_df[new_order]

# modify column names
strava_df.columns = ['id', 'name', 'date', 'sport', 'distance', 'time',
       'speed', 'elev_gain',
       'avg_HR', 'max_HR', 'suffer_score', 'time-minutes','average_speed',
       'start_date']

print (strava_df.head())

### Gather activity data and build activity_df
# activity ID to inspect
activity_id = 15048399185

# endpoint URL
url = f'https://www.strava.com/api/v3/activities/{activity_id}/zones'
# Set up Authorization header and make request
headers = {'Authorization': f'Bearer {access_token}'}
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    zones = response.json()
else:
    print(f"Error: {response.status_code}")
    print(response.text)

# Build activity_df
activity_df = strava_df.loc[strava_df.id == activity_id, ['name','date']]
# add suffer score and total minutes to activity_df
activity_df['suffer_score'] = pd.DataFrame(zones[0]).iloc[0,0]

# create time_in_zones series
zone_series  = pd.DataFrame(zones[0]).iloc[:,1]
time_in_zones = zone_series.apply(lambda z: z['time']/60)

# Create column names for all zones
column_names = [f'Zone{i+1}' for i in range(len(time_in_zones))]
# Convert to single-row DataFrame
zone_df = pd.DataFrame([time_in_zones.values], columns=column_names)

# set index of zond.df to match activity index before merge
zone_df.index = activity_df.index
activity_df = pd.merge(activity_df, zone_df,left_index=True, right_index=True)

# create moderate and intense summary columns
activity_df['moderate'] = activity_df.Zone1 + activity_df.Zone2
activity_df['intense']= activity_df.Zone3 + activity_df.Zone4 + activity_df.Zone5

print (activity_df)