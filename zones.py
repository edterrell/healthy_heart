import requests
import pandas as pd
import time


def get_zones_for_id(activity_id, access_token):
    print(f"Fetching zones for activity: {activity_id}")
    url = f'https://www.strava.com/api/v3/activities/{activity_id}/zones'
    # Set up Authorization header and make request
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        zones = response.json()
    else:
        print(f"Error fetching zones: {response.status_code}")
        print(response.text)
    # create time_in_zones series
    zone_series  = pd.DataFrame(zones[0]).iloc[:,1]
    
    time_in_zones = zone_series.apply(lambda z: z['time']/60)
    time_in_zones.index = ['Zone1', 'Zone2', 'Zone3', 'Zone4', 'Zone5']
    time.sleep(.6)
    return (time_in_zones)

def build_week_summary (strava_zone_df):
    """
    Build a weekly summary DataFrame with max values per week for
    intense effort, moderate effort, and suffer score.

    Parameters:
        strava_zone_df (pd.DataFrame): DataFrame with columns including:
            - 'week_start' (datetime)
            - 'weekly_intense', 'weekly_moderate', 'weekly_suffer_score'

    Returns:
        pd.DataFrame: Summary with one row per week, columns:
            'week_start', 'weekly_intense', 'weekly_moderate', 
            'weekly_suffer_score', and 'week' (formatted string label)
    """
    week_summary = (strava_zone_df
        .groupby('week_start')[['weekly_intense','weekly_moderate','weekly_suffer_score','weekly_HR-value']]
        .max()
        .reset_index()
    )
    # Format weeks as strings (e.g. 'Jul 01', 'Jul 08') for plotting    
    week_summary["week"] = week_summary["week_start"].dt.strftime('%b %d')
    #week_summary[['weekly_intense','weekly_moderate']].head(3)
    return week_summary

    