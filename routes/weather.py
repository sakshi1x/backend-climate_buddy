from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests
import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
load_dotenv()

router = APIRouter()

# Request/Response models
class WeatherRequest(BaseModel):
    city: str
    country_code: Optional[str] = None

class WeatherResponse(BaseModel):
    city: str
    country: str
    weather: str
    temperature: str
    humidity: str
    wind_speed: str
    pressure: str
    visibility: str
    uv_index: Optional[str] = None
    air_quality: Optional[Dict[str, Any]] = None

class ClimateDataResponse(BaseModel):
    city: str
    temperature_trend: list[float]
    humidity_trend: list[float]
    precipitation_trend: list[float]
    air_quality_trend: list[float]

# OpenWeatherMap API configuration
WEATHER_API_KEY =os.getenv("api_key")
WEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5"

@router.get("/current/{city}", response_model=WeatherResponse)
async def get_current_weather(city: str, country_code: Optional[str] = None):
    """
    Get current weather information for a specific city
    """
    try:
        # Clean city name and handle common issues
        city = city.strip().strip('"').strip("'").strip()
        
        # Validate city name
        if not city or len(city) < 2:
            raise HTTPException(status_code=400, detail="City name must be at least 2 characters long")
        
        # Build API URL
        if country_code:
            location = f"{city},{country_code}"
        else:
            location = city
            
        url = f"{WEATHER_BASE_URL}/weather?q={location}&appid={WEATHER_API_KEY}&units=metric"
        
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Extract weather information
        weather_info = WeatherResponse(
            city=data['name'],
            country=data['sys']['country'],
            weather=data['weather'][0]['description'].title(),
            temperature=f"{data['main']['temp']}°C",
            humidity=f"{data['main']['humidity']}%",
            wind_speed=f"{data['wind']['speed']} m/s",
            pressure=f"{data['main']['pressure']} hPa",
            visibility=f"{data.get('visibility', 0) / 1000:.1f} km"
        )
        
        # Add UV index if available
        if 'uvi' in data:
            weather_info.uv_index = f"{data['uvi']}"
        
        return weather_info
        
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error fetching weather for {city}: {str(e)}")
    except KeyError as e:
        raise HTTPException(status_code=500, detail=f"Error parsing weather data: {str(e)}")

@router.get("/forecast/{city}")
async def get_weather_forecast(city: str, days: int = 5):
    """
    Get weather forecast for a specific city
    """
    try:
        city = city.strip().strip('"').strip("'")
        url = f"{WEATHER_BASE_URL}/forecast?q={city}&appid={WEATHER_API_KEY}&units=metric"
        
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Process forecast data
        forecast = []
        for item in data['list'][:days * 8]:  # 8 forecasts per day (3-hour intervals)
            forecast.append({
                "datetime": item['dt_txt'],
                "temperature": f"{item['main']['temp']}°C",
                "weather": item['weather'][0]['description'].title(),
                "humidity": f"{item['main']['humidity']}%",
                "wind_speed": f"{item['wind']['speed']} m/s"
            })
        
        return {
            "city": data['city']['name'],
            "country": data['city']['country'],
            "forecast": forecast
        }
        
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error fetching forecast for {city}: {str(e)}")
    except KeyError as e:
        raise HTTPException(status_code=500, detail=f"Error parsing forecast data: {str(e)}")

@router.get("/climate-data/{city}")
async def get_climate_data(city: str):
    """
    Get historical climate data and trends for a city
    Note: This is a simplified version. In production, you'd use a climate data API
    """
    try:
        # For demo purposes, we'll generate sample climate trend data
        # In a real application, you'd fetch this from a climate data service
        
        import random
        import datetime
        
        # Generate sample trend data (last 30 days)
        base_temp = 20.0  # Base temperature
        base_humidity = 60.0  # Base humidity
        base_precipitation = 2.0  # Base precipitation
        base_air_quality = 50.0  # Base air quality index
        
        temperature_trend = [base_temp + random.uniform(-5, 5) for _ in range(30)]
        humidity_trend = [base_humidity + random.uniform(-10, 10) for _ in range(30)]
        precipitation_trend = [max(0, base_precipitation + random.uniform(-1, 3)) for _ in range(30)]
        air_quality_trend = [max(0, base_air_quality + random.uniform(-20, 20)) for _ in range(30)]
        
        return ClimateDataResponse(
            city=city,
            temperature_trend=temperature_trend,
            humidity_trend=humidity_trend,
            precipitation_trend=precipitation_trend,
            air_quality_trend=air_quality_trend
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating climate data: {str(e)}")

@router.get("/air-quality/{city}")
async def get_air_quality(city: str):
    """
    Get air quality information for a city
    """
    try:
        # This would typically use an air quality API like OpenWeatherMap's air pollution API
        # For demo purposes, we'll return sample data
        
        import random
        
        aqi = random.randint(20, 150)
        
        # Determine air quality category
        if aqi <= 50:
            category = "Good"
            health_impact = "Air quality is satisfactory"
        elif aqi <= 100:
            category = "Moderate"
            health_impact = "Sensitive people may experience minor breathing discomfort"
        elif aqi <= 150:
            category = "Unhealthy for Sensitive Groups"
            health_impact = "Children and people with respiratory diseases should limit outdoor activities"
        else:
            category = "Unhealthy"
            health_impact = "Everyone may experience health effects"
        
        return {
            "city": city,
            "aqi": aqi,
            "category": category,
            "health_impact": health_impact,
            "pollutants": {
                "pm2_5": round(random.uniform(10, 50), 1),
                "pm10": round(random.uniform(20, 80), 1),
                "o3": round(random.uniform(50, 120), 1),
                "no2": round(random.uniform(20, 60), 1)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching air quality data: {str(e)}")

@router.get("/cities/search")
async def search_cities(query: str, limit: int = 10):
    """
    Search for cities by name
    """
    # Sample cities for demo - in production, you'd use a geocoding API
    sample_cities = [
        {"name": "London", "country": "GB", "state": "England"},
        {"name": "New York", "country": "US", "state": "NY"},
        {"name": "Tokyo", "country": "JP", "state": "Tokyo"},
        {"name": "Paris", "country": "FR", "state": "Île-de-France"},
        {"name": "Sydney", "country": "AU", "state": "NSW"},
        {"name": "Mumbai", "country": "IN", "state": "Maharashtra"},
        {"name": "São Paulo", "country": "BR", "state": "São Paulo"},
        {"name": "Cairo", "country": "EG", "state": "Cairo"},
        {"name": "Lagos", "country": "NG", "state": "Lagos"},
        {"name": "Bangkok", "country": "TH", "state": "Bangkok"}
    ]
    
    # Filter cities based on query
    filtered_cities = [
        city for city in sample_cities 
        if query.lower() in city["name"].lower()
    ][:limit]
    
    return {"cities": filtered_cities}
