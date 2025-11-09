from flask import Flask, render_template, request
from geopy.geocoders import Nominatim
from datetime import datetime
import requests
import pandas as pd

app=Flask(__name__)

weather_options = {
    "Temperature Range": ["temperature_2m_max", "temperature_2m_min"],
    "Precipitation Sum": ["precipitation_sum"],
    "Rain Sum": ["rain_sum"],
    "Snowfall Sum": ["snowfall_sum"],
    "Showers Sum": ["showers_sum"],
    "Current Temperature": ["temperature_2m"]
}

def fetch_coordinates(city):
    geolocator = Nominatim(user_agent="City Weather Identifier")
    location = geolocator.geocode(city)
    if not location:
        return None, None
    
    loc_class=location.raw.get('class', '').lower()
    loc_type=location.raw.get('type', '').lower()

    if loc_class== "place" and loc_type in ["city", "capital", "metropolis"] \
        or loc_class=="boundary" and loc_type=="administrative":
        return location.latitude, location.longitude
    return None, None


def fetch_weather_data(lat, lon, variables):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": variables,
        "timezone": "auto"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()['daily']
    else:
        return None


def fetch_current_temperature(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m",
        "timezone": "auto"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        hourly_data = response.json()['hourly']
        times = hourly_data['time']
        temps = hourly_data['temperature_2m']
        now = datetime.now().strftime('%Y-%m-%dT%H:00')
        if now in times:
            index = times.index(now)
            return temps[index]
    return None


@app.route('/', methods=["POST","GET"])

def index():
    table_html=None
    error=None
    name=None
    if request.method =="POST":
        city=request.form.get("city").strip()
        option=request.form.get("Weather-Details")

        if not city:
            error="Please enter city name"
        else:
            lat, lon = fetch_coordinates(city)
            if lat is None or lon is None:
                error = f"Could not find location for '{city}'."
            else:
                name=city.title()
                if option == "Current Temperature":
                    temp = fetch_current_temperature(lat, lon)
                    if temp is not None:
                        table_html = f"<p>Current Temperature in {city.title()}: {temp}°C</p>"
                    else:
                        error = "Current temperature not available."
                else:
                    variables = weather_options[option]
                    data = fetch_weather_data(lat, lon, variables)
                    if data:
                        df = pd.DataFrame(data)
                        rename = {
                            "temperature_2m_max": "Maximum Temperature (°C)",
                            "temperature_2m_min": "Minimum Temperature (°C)",
                            "precipitation_sum": "Precipitation (mm)",
                            "rain_sum": "Rainfall (mm)",
                            "snowfall_sum": "Snowfall (mm)",
                            "showers_sum": "Showers (mm)",
                            "temperature_2m": "Temperature (°C)",
                            "time": "Date"
                            }
                        df.rename(columns=rename, inplace=True)
                        table_html = df.to_html(table_id="table", classes="table table-striped table-bordered", index=False)
                    else:
                        error = "Failed to retrieve weather data."
    return render_template("index.html", options=weather_options.keys(), table_html=table_html, error=error, name=name)


    
if __name__ == "__main__":
    app.run(debug=True)
