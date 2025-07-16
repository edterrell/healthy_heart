import time
import pandas as pd
pd.set_option('display.precision', 1)

def display_detail_week(start, strava_df, strava_zone_df):
    select_start = pd.Timestamp(start, tz='UTC') 
    select_end = select_start + pd.Timedelta(days=7)
    mask = (strava_df['start_date'] >= select_start) & (strava_df['start_date'] < select_end)
    week_df = strava_df[mask]
    week_df
    
    zone_mask = (strava_zone_df['start_date'] >= select_start) & (strava_zone_df['start_date'] < select_end)
    zone_week_df = strava_zone_df[zone_mask]
    zone_week_df
    return week_df, zone_week_df
