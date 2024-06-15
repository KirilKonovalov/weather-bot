import os
import requests
import openmeteo_requests
from dotenv import load_dotenv

import requests_cache
import pandas as pd
from retry_requests import retry

load_dotenv()

def get_weather():
    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 52.52,
        "longitude": 13.41,
        "hourly": "temperature_2m",
        "forecast_days": 1
    }
    responses = openmeteo.weather_api(url, params=params)

    response = responses[0]
    print(f"Coordinates {response.Latitude()}°N {response.Longitude()}°E")
    print(f"Elevation {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()}")
    print(f"Timezone difference to GMT+0 {response.UtcOffsetSeconds()} s")

    hourly = response.Hourly()
    hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()

    hourly_data = {"date": pd.date_range(
        start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
        end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
        freq=pd.Timedelta(seconds=hourly.Interval()),
        inclusive="left"
    )}
    hourly_data["temperature_2m"] = hourly_temperature_2m

    hourly_dataframe = pd.DataFrame(data=hourly_data)
    return hourly_dataframe.to_markdown(index=None)
    
def send_message(message):
    
    # TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_TOKEN')
    # TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID')
    
    TELEGRAM_BOT_TOKEN = '7183169130:AAFRwwQc5wjP5750nfpaD4thR0nBYScTBAw'
    TELEGRAM_CHANNEL_ID = '-1002240857940'

    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'

    params = {
        'chat_id': TELEGRAM_CHANNEL_ID,
        'text': f'{message}'
    }
 
    res = requests.post(url, params=params)
    res.raise_for_status()

    return res.json()


if __name__ == '__main__':
    weather = get_weather()
    send_message(weather)