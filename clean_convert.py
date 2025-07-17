import time
import os
from datetime import datetime
import pandas as pd
pd.set_option('display.precision', 1)
__all__ = ['cleanup', 'convert_speed', 'order_columns', 'process_new_data', 'save_data']



def cleanup (strava_df):
    """
    Clean and transform Strava activity DataFrame:
    - Convert start_date to datetime and extract date
    - Convert distance from meters to miles
    - Convert moving_time to minutes and add formatted time (hh:mm)
    - Convert elevation gain from meters to feet
    """
    # drop activities where no heartrate data was collected
    strava_df = strava_df.dropna(subset=['average_heartrate']).copy()
    
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
    
def order_columns (df):
    # Reorder columns
    new_order = ['id', 'name','date','sport_type',  'distance','moving_time', 'converted_speed', 
           'total_elevation_gain', 'average_heartrate', 'max_heartrate',
           'suffer_score', 'time','average_speed','start_date' ]
    
    df = df[new_order]
    
    # modify column names
    df.columns = ['id', 'name', 'date', 'sport', 'distance', 'time',
           'speed', 'elev_gain',
           'avg_HR', 'max_HR', 'suffer_score', 'time-minutes','average_speed',
           'start_date']
    return df

def process_new_data (new_activities_df, strava_df):
    if new_activities_df.empty:
        print("No new activities to process.")
        return strava_df

    # proceed with combining or processing
    new_activities_df = cleanup (new_activities_df)
    new_activities_df['converted_speed'] = new_activities_df.apply(convert_speed, axis=1)
    new_activities_df = order_columns(new_activities_df)

    strava_df = pd.concat ([new_activities_df, strava_df])
    #strava_df.head()
    return strava_df


def save_data (strava_df, strava_zone_df, year):
    # Create directory with today's date, e.g., "2025-07-17"
    today_dir = datetime.today().strftime("%Y-%m-%d")
    dir_path = os.path.join("data", today_dir)
    os.makedirs(dir_path, exist_ok=True)
    
    # Build file paths inside that folder
    strava_path = os.path.join(dir_path, f"strava_data_{year}.pkl")
    zone_path = os.path.join(dir_path, f"strava_zone_data_{year}.pkl")
    
    # Save the pickles
    strava_df.to_pickle(strava_path)
    strava_zone_df.to_pickle(zone_path)
    
    print(f"Data saved in folder: {dir_path}")

# Example usage:
# save_strava_data_daily(strava_df, strava_zone_df, 2025)

