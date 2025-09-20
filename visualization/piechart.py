import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, Any, List

def create_air_quality_pie_chart(components: Dict[str, float], city: str) -> Dict[str, Any]:
    """
    Create a pie chart for air quality components
    """
    # Normalize component names and values
    pollutants = ['PM2.5', 'PM10', 'NO2', 'O3', 'SO2', 'CO']
    values = [
        components.get('pm2_5', 0),
        components.get('pm10', 0),
        components.get('no2', 0),
        components.get('o3', 0),
        components.get('so2', 0),
        components.get('co', 0) / 1000  # Convert CO from μg/m³ to mg/m³
    ]
    
    # Define colors for each pollutant
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
    
    fig = go.Figure(data=[go.Pie(
        labels=pollutants,
        values=values,
        hole=0.3,
        marker_colors=colors,
        textinfo='label+percent',
        textfont_size=12,
        hovertemplate='<b>%{label}</b><br>Value: %{value:.2f}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title={
            'text': f'Air Quality Composition - {city}',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16}
        },
        template='plotly_white',
        height=400,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02
        )
    )
    
    return {
        "chart_type": "air_quality_pie",
        "data": fig.to_dict(),
        "layout": fig.layout.to_dict()
    }

def create_weather_distribution_pie_chart(weather_data: List[Dict[str, Any]], city: str) -> Dict[str, Any]:
    """
    Create a pie chart for weather condition distribution
    """
    # Count weather conditions
    weather_counts = {}
    for item in weather_data:
        condition = item.get('weather', 'Unknown')
        weather_counts[condition] = weather_counts.get(condition, 0) + 1
    
    # Create pie chart
    conditions = list(weather_counts.keys())
    counts = list(weather_counts.values())
    
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#FFB6C1', '#98FB98']
    
    fig = go.Figure(data=[go.Pie(
        labels=conditions,
        values=counts,
        hole=0.3,
        marker_colors=colors[:len(conditions)],
        textinfo='label+percent',
        textfont_size=12,
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title={
            'text': f'Weather Conditions Distribution - {city}',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16}
        },
        template='plotly_white',
        height=400,
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02
        )
    )
    
    return {
        "chart_type": "weather_distribution_pie",
        "data": fig.to_dict(),
        "layout": fig.layout.to_dict()
    }

def create_temperature_humidity_pie_chart(temperature_data: List[float], humidity_data: List[float], city: str) -> Dict[str, Any]:
    """
    Create a pie chart showing temperature and humidity ranges
    """
    # Categorize temperature ranges
    temp_ranges = ['Cold (<10°C)', 'Cool (10-20°C)', 'Warm (20-30°C)', 'Hot (>30°C)']
    temp_counts = [0, 0, 0, 0]
    
    for temp in temperature_data:
        if temp < 10:
            temp_counts[0] += 1
        elif temp < 20:
            temp_counts[1] += 1
        elif temp < 30:
            temp_counts[2] += 1
        else:
            temp_counts[3] += 1
    
    # Categorize humidity ranges
    humidity_ranges = ['Low (<40%)', 'Moderate (40-60%)', 'High (60-80%)', 'Very High (>80%)']
    humidity_counts = [0, 0, 0, 0]
    
    for humidity in humidity_data:
        if humidity < 40:
            humidity_counts[0] += 1
        elif humidity < 60:
            humidity_counts[1] += 1
        elif humidity < 80:
            humidity_counts[2] += 1
        else:
            humidity_counts[3] += 1
    
    # Create subplot with two pie charts
    from plotly.subplots import make_subplots
    
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "pie"}, {"type": "pie"}]],
        subplot_titles=("Temperature Ranges", "Humidity Ranges")
    )
    
    # Temperature pie chart
    fig.add_trace(go.Pie(
        labels=temp_ranges,
        values=temp_counts,
        hole=0.3,
        marker_colors=['#87CEEB', '#4ECDC4', '#FFB347', '#FF6B6B'],
        name="Temperature"
    ), row=1, col=1)
    
    # Humidity pie chart
    fig.add_trace(go.Pie(
        labels=humidity_ranges,
        values=humidity_counts,
        hole=0.3,
        marker_colors=['#E6E6FA', '#B0E0E6', '#87CEEB', '#4682B4'],
        name="Humidity"
    ), row=1, col=2)
    
    fig.update_layout(
        title={
            'text': f'Temperature & Humidity Distribution - {city}',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16}
        },
        template='plotly_white',
        height=400,
        showlegend=False
    )
    
    return {
        "chart_type": "temperature_humidity_pie",
        "data": fig.to_dict(),
        "layout": fig.layout.to_dict()
    }
