import os
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import requests
import json
import random
import datetime
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
load_dotenv()
# Chart generation is now handled in the frontend

router = APIRouter()

# Request/Response models
class DashboardDataResponse(BaseModel):
    city: str
    current_weather: Dict[str, Any]
    summary_stats: Dict[str, str]
    chart_data: Dict[str, Any]  # Raw data for charts
    air_quality: Dict[str, Any]
    forecast: List[Dict[str, Any]]

# ChartData model removed - charts are now generated in frontend

# OpenWeatherMap API configuration
WEATHER_API_KEY =os.getenv("api_key")
WEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5"

def get_weather_data(city: str) -> Dict[str, Any]:
    """Fetch current weather data from OpenWeatherMap API"""
    try:
        url = f"{WEATHER_BASE_URL}/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error fetching weather for {city}: {str(e)}")

def get_forecast_data(city: str, days: int = 5) -> Dict[str, Any]:
    """Fetch weather forecast data from OpenWeatherMap API"""
    try:
        url = f"{WEATHER_BASE_URL}/forecast?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error fetching forecast for {city}: {str(e)}")

def get_air_quality_data(city: str) -> Dict[str, Any]:
    """Fetch air quality data from OpenWeatherMap API"""
    try:
        # First get coordinates
        weather_data = get_weather_data(city)
        lat = weather_data['coord']['lat']
        lon = weather_data['coord']['lon']
        
        # Get air quality data
        url = f"{WEATHER_BASE_URL}/air_pollution?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        # Return mock data if API fails
        return {
            "list": [{
                "main": {"aqi": random.randint(20, 150)},
                "components": {
                    "co": random.uniform(200, 1000),
                    "no": random.uniform(0, 50),
                    "no2": random.uniform(10, 60),
                    "o3": random.uniform(50, 120),
                    "so2": random.uniform(5, 30),
                    "pm2_5": random.uniform(10, 50),
                    "pm10": random.uniform(20, 80),
                    "nh3": random.uniform(0, 20)
                }
            }]
        }

def get_temperature_data(city: str, days: int = 7) -> Dict[str, Any]:
    """Extract temperature and humidity data for charting"""
    try:
        forecast_data = get_forecast_data(city, days)
        
        # Extract temperature data
        dates = []
        temps = []
        humidity = []
        
        for item in forecast_data['list'][:days * 8]:  # 8 forecasts per day
            dates.append(item['dt_txt'])
            temps.append(item['main']['temp'])
            humidity.append(item['main']['humidity'])
        
        return {
            "dates": dates,
            "temperatures": temps,
            "humidity": humidity,
            "city": city
        }
    except Exception as e:
        # Return mock data if API fails
        dates = []
        temps = []
        humidity = []
        
        for i in range(7):
            date = datetime.datetime.now() + datetime.timedelta(days=i)
            dates.append(date.strftime('%Y-%m-%d %H:%M:%S'))
            temps.append(round(random.uniform(15, 30), 1))
            humidity.append(round(random.uniform(40, 80), 1))
        
        return {
            "dates": dates,
            "temperatures": temps,
            "humidity": humidity,
            "city": city,
            "mock": True
        }

def get_air_quality_chart_data(city: str) -> Dict[str, Any]:
    """Extract air quality data for charting"""
    try:
        air_quality_data = get_air_quality_data(city)
        components = air_quality_data['list'][0]['components']
        
        # Prepare data for pie chart
        pollutants = ['PM2.5', 'PM10', 'NO2', 'O3', 'SO2', 'CO']
        values = [
            round(components['pm2_5'], 1),
            round(components['pm10'], 1),
            round(components['no2'], 1),
            round(components['o3'], 1),
            round(components['so2'], 1),
            round(components['co'] / 1000, 1)  # Convert CO from μg/m³ to mg/m³
        ]
        
        return {
            "pollutants": pollutants,
            "values": values,
            "city": city
        }
    except Exception as e:
        # Return mock data if API fails
        pollutants = ['PM2.5', 'PM10', 'NO2', 'O3', 'SO2', 'CO']
        values = [round(random.uniform(10, 50), 1) for _ in pollutants]
        
        return {
            "pollutants": pollutants,
            "values": values,
            "city": city,
            "mock": True
        }

def get_weather_distribution_data(city: str, days: int = 30) -> Dict[str, Any]:
    """Extract weather condition distribution data for charting"""
    try:
        forecast_data = get_forecast_data(city, days)
        
        # Count weather conditions
        weather_counts = {}
        for item in forecast_data['list']:
            condition = item['weather'][0]['main']
            weather_counts[condition] = weather_counts.get(condition, 0) + 1
        
        return {
            "conditions": list(weather_counts.keys()),
            "counts": list(weather_counts.values()),
            "city": city
        }
    except Exception as e:
        # Return mock data if API fails
        conditions = ['Clear', 'Clouds', 'Rain', 'Snow', 'Thunderstorm']
        counts = [random.randint(5, 15) for _ in conditions]
        
        return {
            "conditions": conditions,
            "counts": counts,
            "city": city,
            "mock": True
        }

@router.get("/data", response_model=DashboardDataResponse)
async def get_dashboard_data(
    city: str = Query(..., description="City name"),
    days: int = Query(7, description="Number of days for forecast"),
    data_type: str = Query("all", description="Type of data to fetch")
):
    """
    Get comprehensive dashboard data including weather, charts, and statistics
    """
    try:
        # Get current weather
        weather_data = get_weather_data(city)
        current_weather = {
            "city": weather_data['name'],
            "country": weather_data['sys']['country'],
            "temperature": f"{weather_data['main']['temp']}°C",
            "feels_like": f"{weather_data['main']['feels_like']}°C",
            "humidity": f"{weather_data['main']['humidity']}%",
            "pressure": f"{weather_data['main']['pressure']} hPa",
            "wind_speed": f"{weather_data['wind']['speed']} m/s",
            "wind_direction": f"{weather_data['wind'].get('deg', 0)}°",
            "visibility": f"{weather_data.get('visibility', 0) / 1000:.1f} km",
            "weather": weather_data['weather'][0]['description'].title(),
            "weather_icon": weather_data['weather'][0]['icon'],
            "uv_index": weather_data.get('uvi', 0)
        }
        
        # Get air quality
        air_quality_data = get_air_quality_data(city)
        aqi = air_quality_data['list'][0]['main']['aqi']
        components = air_quality_data['list'][0]['components']
        
        air_quality = {
            "aqi": aqi,
            "category": get_aqi_category(aqi),
            "health_impact": get_aqi_health_impact(aqi),
            "components": {
                "pm2_5": round(components['pm2_5'], 1),
                "pm10": round(components['pm10'], 1),
                "no2": round(components['no2'], 1),
                "o3": round(components['o3'], 1),
                "so2": round(components['so2'], 1),
                "co": round(components['co'], 1)
            }
        }
        
        # Get forecast
        forecast_data = get_forecast_data(city, days)
        forecast = []
        for item in forecast_data['list'][:days * 8]:
            forecast.append({
                "datetime": item['dt_txt'],
                "temperature": f"{item['main']['temp']}°C",
                "feels_like": f"{item['main']['feels_like']}°C",
                "humidity": f"{item['main']['humidity']}%",
                "weather": item['weather'][0]['description'].title(),
                "weather_icon": item['weather'][0]['icon'],
                "wind_speed": f"{item['wind']['speed']} m/s",
                "pressure": f"{item['main']['pressure']} hPa"
            })
        
        # Get chart data
        chart_data = {}
        if data_type in ["all", "charts"]:
            chart_data = {
                "temperature": get_temperature_data(city, days),
                "air_quality": get_air_quality_chart_data(city),
                "weather_distribution": get_weather_distribution_data(city, days)
            }
        
        # Calculate summary statistics
        summary_stats = {
            "avg_temperature": f"{weather_data['main']['temp']}°C",
            "humidity": f"{weather_data['main']['humidity']}%",
            "air_quality": get_aqi_category(aqi),
            "wind_speed": f"{weather_data['wind']['speed']} m/s",
            "pressure": f"{weather_data['main']['pressure']} hPa",
            "visibility": f"{weather_data.get('visibility', 0) / 1000:.1f} km"
        }
        
        return DashboardDataResponse(
            city=city,
            current_weather=current_weather,
            summary_stats=summary_stats,
            chart_data=chart_data,
            air_quality=air_quality,
            forecast=forecast
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating dashboard data: {str(e)}")

def get_aqi_category(aqi: int) -> str:
    """Convert AQI number to category"""
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Moderate"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups"
    elif aqi <= 200:
        return "Unhealthy"
    elif aqi <= 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"

def get_aqi_health_impact(aqi: int) -> str:
    """Get health impact description based on AQI"""
    if aqi <= 50:
        return "Air quality is satisfactory, and air pollution poses little or no risk."
    elif aqi <= 100:
        return "Air quality is acceptable. However, there may be a risk for some people, particularly those who are unusually sensitive to air pollution."
    elif aqi <= 150:
        return "Members of sensitive groups may experience health effects. The general public is less likely to be affected."
    elif aqi <= 200:
        return "Some members of the general public may experience health effects; members of sensitive groups may experience more serious health effects."
    elif aqi <= 300:
        return "Health alert: The risk of health effects is increased for everyone."
    else:
        return "Health warning of emergency conditions: everyone is more likely to be affected."

@router.get("/cities/search")
async def search_cities(query: str = Query("", description="Search query"), limit: int = Query(10, description="Maximum number of results")):
    """
    Search for cities with autocomplete functionality
    """
    # Default popular cities when no query is provided
    default_cities = [
        {"name": "London", "country": "GB", "state": "England", "lat": 51.5074, "lon": -0.1278},
        {"name": "New York", "country": "US", "state": "NY", "lat": 40.7128, "lon": -74.0060},
        {"name": "Tokyo", "country": "JP", "state": "Tokyo", "lat": 35.6762, "lon": 139.6503},
        {"name": "Paris", "country": "FR", "state": "Île-de-France", "lat": 48.8566, "lon": 2.3522},
        {"name": "Sydney", "country": "AU", "state": "NSW", "lat": -33.8688, "lon": 151.2093},
        {"name": "Mumbai", "country": "IN", "state": "Maharashtra", "lat": 19.0760, "lon": 72.8777},
        {"name": "São Paulo", "country": "BR", "state": "São Paulo", "lat": -23.5505, "lon": -46.6333},
        {"name": "Cairo", "country": "EG", "state": "Cairo", "lat": 30.0444, "lon": 31.2357},
        {"name": "Berlin", "country": "DE", "state": "Berlin", "lat": 52.5200, "lon": 13.4050},
        {"name": "Beijing", "country": "CN", "state": "Beijing", "lat": 39.9042, "lon": 116.4074}
    ]
    
    # If no query provided, return default cities
    if not query or query.strip() == "":
        return {"cities": default_cities[:limit]}
    
    try:
        # Use OpenWeatherMap's geocoding API for real city search
        url = f"http://api.openweathermap.org/geo/1.0/direct?q={query}&limit={limit}&appid={WEATHER_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        cities = []
        for city in data:
            cities.append({
                "name": city['name'],
                "country": city['country'],
                "state": city.get('state', ''),
                "lat": city['lat'],
                "lon": city['lon']
            })
        
        # If no results from API, fall back to filtering default cities
        if not cities:
            filtered_cities = [
                city for city in default_cities 
                if query.lower() in city["name"].lower()
            ][:limit]
            return {"cities": filtered_cities}
        
        return {"cities": cities}
        
    except requests.RequestException as e:
        # Fallback to sample cities if API fails
        filtered_cities = [
            city for city in default_cities 
            if query.lower() in city["name"].lower()
        ][:limit]
        
        return {"cities": filtered_cities}

@router.get("/chart-data/{chart_type}")
async def get_chart_data(
    chart_type: str,
    city: str = Query(..., description="City name"),
    days: int = Query(7, description="Number of days")
):
    """
    Get specific chart data (raw data for frontend charting)
    """
    try:
        if chart_type == "temperature":
            return get_temperature_data(city, days)
        elif chart_type == "air_quality":
            return get_air_quality_chart_data(city)
        elif chart_type == "weather_distribution":
            return get_weather_distribution_data(city, days)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown chart type: {chart_type}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting chart data: {str(e)}")
