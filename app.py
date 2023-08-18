from flask import Flask, render_template, request, jsonify
import requests
from collections import defaultdict
from datetime import datetime


app = Flask(__name__)

# Your OpenWeatherMap API Key (register on their website to get this)
API_KEY = '908f6a1b206d0baf8c3bed93c4138fe1'
BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"
FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast?"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_weather', methods=['POST'])
def get_weather():
    city = request.form['city']
    complete_url = BASE_URL + "q=" + city + "&appid=" + API_KEY
    response = requests.get(complete_url)
    data = response.json()

    if data.get("cod") != 404:
        main = data.get("main", {})
        coord = data.get("coord", {})
        weather = data["weather"][0] if data.get("weather") else {}
        return jsonify({
            'city': data.get('name'),
            'temperature': main.get("temp"),
            'description': weather.get("description"),
            'icon': weather.get("icon"),
            'lon': coord.get("lon"),
            'lat': coord.get("lat")
        })
    else:
        return jsonify({'error': 'Unknown error occured'})
    
def get_weather_data(city):
    complete_url = BASE_URL + "q=" + city + "&appid=" + API_KEY
    response = requests.get(complete_url)
    data = response.json()
    
    if data.get("cod") != 404:
        main = data.get("main", {})
        coord = data.get("coord", {})
        weather = data["weather"][0] if data.get("weather") else {}
        return jsonify({
            'city': data.get('name'),
            'temperature': main.get("temp"),
            'description': weather.get("description"),
            'icon': weather.get("icon"),
            'lon': coord.get("lon"),
            'lat': coord.get("lat")
        }).get_json()
    else:
        return jsonify({'error': 'Unknown error occured'})

@app.route('/get_multiple_weather', methods=['POST'])
def get_multiple_weather():
    cities = request.json.get('cities', [])
    weather_data = []
    for city in cities:
        data = get_weather_data(city)  # Assuming you have a function called get_weather_data
        weather_data.append(data)
    return jsonify(weather_data)

@app.route('/forecast', methods=['POST'])
def get_forecast():
    city = request.form['city']
    response = requests.get(FORECAST_URL + "q=" + city + "&appid=" + API_KEY)

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch forecast data for " + city})
    
    data = response.json()
    daily_max_temps = defaultdict(float)

    for forecast in data['list']:
        # Convert the timestamp to a date string (without time)
        date_str = datetime.utcfromtimestamp(forecast['dt']).strftime('%Y-%m-%d')
        
        # Get the temperature for the current 3-hourly forecast (assuming it's in Kelvin)
        temp = forecast['main']['temp'] - 273.15  # Convert Kelvin to Celsius
        
        # Update the maximum temperature for the day if the current temperature is higher
        daily_max_temps[date_str] = max(daily_max_temps[date_str], temp)

    return jsonify(dict(daily_max_temps))


if __name__ == '__main__':
    app.run(debug=True)
