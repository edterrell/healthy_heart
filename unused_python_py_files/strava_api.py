import requests
import json
import time
import os
from pprint import pprint
import pandas as pd
pd.set_option('display.precision', 1)
from clean_convert import cleanup, convert_speed

#import sys
#sys.executable

from token_manager import get_valid_access_token

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

# Drop any rows with NaN
strava_df = strava_df.dropna(subset=['average_heartrate'])
 
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

# Get acivitity['id'] for all activities
# for id_tags in strava_df.id:
    #print(f"ID: {id_tags}")

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

# set index of zone_df to match activity index before merge
zone_df.index = activity_df.index
activity_df = pd.merge(activity_df, zone_df,left_index=True, right_index=True)

# create moderate and intense summary columns
activity_df['moderate'] = activity_df.Zone1 + activity_df.Zone2
activity_df['intense']= activity_df.Zone3 + activity_df.Zone4 + activity_df.Zone5

print (activity_df)