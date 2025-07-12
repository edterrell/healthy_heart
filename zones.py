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
    time.sleep(1.5)
    return (time_in_zones)