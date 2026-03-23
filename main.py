from flask import Flask, render_template, request, send_from_directory, Response, session
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta
import requests
import pandas as pd
from timezonefinder import TimezoneFinder
from zoneinfo import ZoneInfo
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

if not app.secret_key:
    raise ValueError("Set a secret key in a .env file and keep the .env file in .gitignore (format: SECRET_KEY=abc123)\nWARNING: replace abc123 with a real randomly generated secret key and make it long")

class hourly:
    def __init__(self, lat, lon, variables):
        self.lat = lat
        self.lon = lon
        self.variables = variables

    def get_data(self):
        return fetch_hourly_data(self.lat, self.lon, self.variables)

    def format(self, data):
        if not data:
            return None

        df = pd.DataFrame(data)
        df['time'] = df['time'].str.replace('T', ' ')
        df['time'] = pd.to_datetime(df['time']).dt.strftime('%Y-%m-%d %H:%M')
        df = df.set_index('time').T

        rename = {
            "temperature_2m": "Temperature (°C)",
            "precipitation": "Precipitation (mm)",
            "rain": "Rain (mm)",
            "snowfall": "Snowfall (mm)",
            "showers": "Showers (mm)",
            "windspeed_10m": "Wind Speed (km/h)"
        }

        df.columns.name = "Time"
        df.index = [rename.get(i, i) for i in df.index]

        return df.to_html(table_id = "table", classes = "table table-striped table-bordered")
    
class daily:
    def __init__(self, lat, lon, variables):
        self.lat = lat
        self.lon = lon
        self.variables = variables

    def get_data(self):
        return fetch_daily_data(self.lat, self.lon, self.variables)

    def format(self, data):
        if not data:
            return None

        df = pd.DataFrame(data)

        rename = {
            "temperature_2m_max": "Maximum Temperature (°C)",
            "temperature_2m_min": "Minimum Temperature (°C)",
            "rain_sum": "Total Rain (mm)",
            "windspeed_10m_max": "Maximum Wind Speed (km/h)",
            "windspeed_10m_min": "Minimum Wind Speed (km/h)",
            "snowfall_sum": "Total Snowfall (mm)",
            "precipitation_sum": "Total Precipitation (mm)",
            "showers_sum": "Total Showers (mm)",
            "time": "Date"
        }

        df.rename(columns = rename, inplace = True)

        return df.to_html(table_id = "table", classes = "table table-striped table-bordered", index = False)
    
class current:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    def get_data(self):
        return fetch_current_temperature(self.lat, self.lon)

    def format(self, data, city_name):
        if not data:
            return None

        temp, apparent = data

        return (
            f"<div class='alert alert-info' style='text-align: center; border-radius: 15px;'>"
            f"<h4>Current weather in {city_name}:</h4>"
            f"<p style='font-size: 1.5rem; margin-bottom: 0;'><strong>{temp}°C</strong></p>"
            f"<p style='font-size: 1rem; color: #555;'>Feels like: <strong>{apparent}°C</strong></p>"
            f"</div>"
        )

weather_options = {
    "Current Temperature": ["temperature_2m", "apparent_temperature"],
    "Temperature (Across week)": ["temperature_2m_max", "temperature_2m_min"],
    "Rain (Hourly)": ["rain"],
    "Rain (Across Week)": ["rain_sum"],
    "Wind Speed (Hourly)": ["windspeed_10m"],
    "Wind Speed (Across Week)": ["windspeed_10m_max", "windspeed_10m_min"],
    "Snowfall (Hourly)": ["snowfall"],
    "Snowfall (Across Week)": ["snowfall_sum"],
    "Precipitation (Hourly)": ["precipitation"],
    "Precipitation (Across Week)": ["precipitation_sum"],
    "Showers (Hourly)": ["showers"],
    "Showers (Across Week)": ["showers_sum"],
}

abrvMap = {
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

def normalize_input(cityInput):
    cityInput = cityInput.strip()
    cityInput_lower = cityInput.lower()
    for abv, full in abrvMap.items():
        if cityInput_lower.endswith(" " + abv) or cityInput_lower.endswith("," + abv) or cityInput_lower == abv:
            start_index = cityInput_lower.rfind(abv)
            cityInput = cityInput[:start_index] + full
            cityInput_lower = cityInput.lower()
    return cityInput

def fetch_coordinates(city):
    city = normalize_input(city)
    geolocator = Nominatim(user_agent="City Weather Identifier")
    location = geolocator.geocode(city, exactly_one=True, addressdetails=True, extratags=True)
    if not location:
        return None, None
    
    raw = location.raw
    locClass = raw.get('class', '').lower()
    locType = raw.get('type', '').lower()
    extratags = raw.get('extratags') or {}
    importance = float(raw.get('importance', 0))
    population = extratags.get('population')
    
    try:
        population = int(population) if population else 0
    except ValueError:
        population = 0
    
    if ((locClass == "place" and locType in ["city", "capital", "metropolis"]) or
        (locClass == "boundary" and locType == "administrative")):
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

def fetch_hourly_data(lat, lon, variables):
    tzf = TimezoneFinder()
    tzName = tzf.timezone_at(lat=lat, lng=lon)
    if not tzName:
        tzName = "UTC"
    tz = ZoneInfo(tzName)
    nowLocal = datetime.now(tz)

    if nowLocal.minute >= 30:
        nowLocal = (nowLocal + timedelta(hours=1)).replace(minute = 0, second = 0, microsecond = 0)
    else:
        nowLocal = nowLocal.replace(minute = 0, second = 0, microsecond = 0)
    
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join(variables),
        "timezone": "auto",
        "start_hour": nowLocal.strftime("%Y-%m-%dT%H:%M"),
        "end_hour": (nowLocal + timedelta(hours = 24)).strftime("%Y-%m-%dT%H:%M")
    }
    response = requests.get(url, params = params)
    if response.status_code == 200:
        return response.json().get("hourly")
    return None

def fetch_current_temperature(lat, lon):
    data = fetch_hourly_data(lat, lon, ["temperature_2m", "apparent_temperature"])
    if data and "temperature_2m" in data and "apparent_temperature" in data:
        return data["temperature_2m"][0], data["apparent_temperature"][0]
    return None

@app.route('/', methods=["POST", "GET"])
def index():
    htmlTable = None
    error = None
    name = None
    if request.method == "POST":
        city = (request.form.get("city") or request.form.get("recentCity") or "").strip() 
        option = request.form.get("Weather-Details")
        
        if not city:
            error = "Please enter a city name"
        else:
            lat, lon = fetch_coordinates(city)
            if lat is None or lon is None:
                error = f"Could not find '{city}', make sure you entered a valid city name or check your spelling"
            else:
                name = city.title()

                if "recent_cities" not in session:
                    session["recent_cities"] = []
                
                cities = session["recent_cities"]

                if name in cities:
                    cities.remove(name)

                cities.insert(0, name)
                session["recent_cities"] = cities[:5]
                if option == "Current Temperature":
                    weather = current(lat, lon)
                    data = weather.get_data()
                    htmlTable = weather.format(data, name)

                elif "Hourly" in option:
                    weather = hourly(lat, lon, weather_options[option])
                    data = weather.get_data()
                    htmlTable = weather.format(data)

                else:
                    weather = daily(lat, lon, weather_options[option])
                    data = weather.get_data()
                    htmlTable = weather.format(data)

                if htmlTable is None:
                    error = "Failed to retrieve weather data."
    return render_template("index.html", options = weather_options.keys(), htmlTable = htmlTable, error = error, name = name, recent_cities = session.get("recent_cities", []))

@app.context_processor
def inject_year():
    return {"current_year": datetime.now().year}

@app.route('/robots.txt')
def robotsTxt():
    return send_from_directory(os.getcwd(), 'robots.txt')

@app.route('/sitemap.xml')
def sitemap():
    urls = [{'loc': 'https://city-weather-identifier.vercel.app/', 'lastmod': datetime.now().date()}]
    return Response(render_template('sitemap.xml', urls=urls), mimetype='application/xml')

if __name__ == "__main__":
    app.run(debug = True)