# weather_agent.py

import os
import requests
from typing import Annotated
from langchain_core.tools import tool
from dotenv import load_dotenv
load_dotenv()

def fetch_weather(city: str) -> dict:
    """Fetch weather information for a given city."""
    api_key = os.getenv("api_key")
    city = city.strip().strip('"').strip("'")
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return {"status": "success",
        "data": {
            "weather": data['weather'][0]['description'].title(),
            "temperature": f"{data['main']['temp']}°C",
            "humidity": f"{data['main']['humidity']}%",
            "wind_speed": f"{data['wind']['speed']} m/s",
        }
    }
        
    except requests.RequestException as e:
        return {"error": f"Error fetching weather for {city}: {str(e)}"}
    except KeyError as e:
        return {"error": f"Error parsing weather data for {city}: {str(e)}"}