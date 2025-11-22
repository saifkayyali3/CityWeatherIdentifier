from flask import Flask, render_template, request
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta, timezone
import requests
import pandas as pd
from timezonefinder import TimezoneFinder
from zoneinfo import ZoneInfo

app = Flask(__name__)

weather_options = {
    "Current Temperature": ["temperature_2m"],
    "Temperature (Across week)": ["temperature_2m_max", "temperature_2m_min"],
    "Rain (Hourly)": ["rain"],
    "Wind Speed (Hourly)": ["windspeed_10m"],
    "Snowfall (Hourly)": ["snowfall"],
    "Precipitation (Hourly)": ["precipitation"],
    "Showers (Hourly)": ["showers"]
}

abv_map = {
    "usa": "United States",
    "us": "United States",
    "uk": "United Kingdom",
    "u.k.": "United Kingdom",
    "uae": "United Arab Emirates",
    "ksa": "Saudi Arabia",
    "saudi": "Saudi Arabia",
    "prc": "China",
    "cn": "China",
    "nz": "New Zealand",
    "drc": "Democratic Republic of the Congo"
}

def normalize_input(city_input):
    city_input = city_input.strip()
    city_input_lower = city_input.lower()
    for abv, full in abv_map.items():
        if city_input_lower.endswith(" " + abv) or city_input_lower.endswith("," + abv) or city_input_lower == abv:
            start_index = city_input_lower.rfind(abv)
            city_input = city_input[:start_index] + full
            city_input_lower = city_input.lower()
    return city_input

def fetch_coordinates(city):
    city = normalize_input(city)
    geolocator = Nominatim(user_agent="City Weather Identifier")
    location = geolocator.geocode(city, exactly_one=True, addressdetails=True, extratags=True)
    if not location:
        return None, None
    
    raw = location.raw
    loc_class = raw.get('class', '').lower()
    loc_type = raw.get('type', '').lower()
    extratags = raw.get('extratags') or {}
    importance = float(raw.get('importance', 0))
    population = extratags.get('population')
    
    try:
        population = int(population) if population else 0
    except ValueError:
        population = 0
    
    if ((loc_class == "place" and loc_type in ["city", "capital", "metropolis"]) or
        (loc_class == "boundary" and loc_type == "administrative")):
        if len(city) >= 3 and (population >= 20000 or importance >= 0.3):
            return location.latitude, location.longitude
    return None, None

def fetch_daily_data(lat, lon, variables):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": ",".join(variables),
        "timezone": "auto"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()['daily']
    return None

def fetch_hourly_data(lat, lon, variables, hours=24):
    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lat=lat, lng=lon)
    if not tz_name:
        tz_name = "UTC"
    tz = ZoneInfo(tz_name)
    now_local = datetime.now(tz).replace(minute=0, second=0, microsecond=0)

    if now_local.minute >= 30:
        now_local = (now_local + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    else:
        now_local = now_local.replace(minute=0, second=0, microsecond=0)
    
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join(variables),
        "timezone": "auto",
        "start_hour": now_local.strftime("%Y-%m-%dT%H:%M"),
        "end_hour": (now_local + timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M")
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json().get("hourly")
    return None

def fetch_current_temperature(lat, lon):
    data = fetch_hourly_data(lat, lon, ["temperature_2m"], hours=1)
    if data and "temperature_2m" in data:
        return data["temperature_2m"][0]
    return None

@app.route('/', methods=["POST", "GET"])
def index():
    table_html = None
    error = None
    name = None
    if request.method == "POST":
        city = request.form.get("city").strip()
        option = request.form.get("Weather-Details")
        
        if not city:
            error = "Please enter city name"
        else:
            lat, lon = fetch_coordinates(city)
            if lat is None or lon is None:
                error = f"Could not find '{city}', make sure you entered a valid city name or check your spelling"
            else:
                name = city.title()
                if option == "Current Temperature":
                    temp = fetch_current_temperature(lat, lon)
                    if temp is not None:
                        table_html = f"<p>Current Temperature in {name}: {temp}°C</p>"
                    else:
                        error = "Current temperature not available."
                elif "Hourly" in option:
                    variables = weather_options[option]
                    data = fetch_hourly_data(lat, lon, variables, hours=24)
                    if data:
                        df = pd.DataFrame(data)
                        df['time'] = df['time'].str.replace('T', ' ')
                        df['time'] = pd.to_datetime(df['time']).dt.strftime('%Y-%m-%d %H:%M')
                        
                        rename = {
                            "temperature_2m": "Temperature (°C)",
                            "precipitation": "Precipitation (mm)",
                            "rain": "Rain (mm)",
                            "snowfall": "Snowfall (mm)",
                            "showers": "Showers (mm)",
                            "windspeed_10m": "Wind Speed (km/h)",
                            "time": "Date & Time"
                        }
                        
                        df = df.set_index('time').T
                        df.index = [rename.get(v, v) for v in df.index]
                        table_html = df.to_html(table_id="table", classes="table table-striped table-bordered")
                    else:
                        error = "Failed to retrieve hourly weather data."
                else:
                    variables = weather_options[option]
                    data = fetch_daily_data(lat, lon, variables)
                    if data:
                        df = pd.DataFrame(data)
                        rename = {
                            "temperature_2m_max": "Maximum Temperature (°C)",
                            "temperature_2m_min": "Minimum Temperature (°C)",
                            "time": "Date"
                        }
                        df.rename(columns=rename, inplace=True)
                        table_html = df.to_html(table_id="table", classes="table table-striped table-bordered", index=False)
                    else:
                        error = "Failed to retrieve weather data."
    return render_template("index.html", options=weather_options.keys(), table_html=table_html, error=error, name=name)

if __name__ == "__main__":
    app.run(debug=True)

