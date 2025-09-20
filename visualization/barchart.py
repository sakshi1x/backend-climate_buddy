import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime, timedelta

def create_temperature_bar_chart(temperature_data: List[float], dates: List[str], city: str) -> Dict[str, Any]:
    """
    Create a bar chart for temperature trends
    """
    fig = go.Figure()
    
    # Create color gradient based on temperature values
    colors = []
    for temp in temperature_data:
        if temp < 0:
            colors.append('#0000FF')  # Blue for very cold
        elif temp < 10:
            colors.append('#87CEEB')  # Light blue for cold
        elif temp < 20:
            colors.append('#4ECDC4')  # Teal for cool
        elif temp < 30:
            colors.append('#FFB347')  # Orange for warm
        else:
            colors.append('#FF6B6B')  # Red for hot
    
    fig.add_trace(go.Bar(
        x=dates,
        y=temperature_data,
        marker_color=colors,
        text=[f'{temp:.1f}°C' for temp in temperature_data],
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>Temperature: %{y:.1f}°C<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': f'Daily Temperature Trends - {city}',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16}
        },
        xaxis_title='Date',
        yaxis_title='Temperature (°C)',
        template='plotly_white',
        height=400,
        xaxis=dict(tickangle=45)
    )
    
    return {
        "chart_type": "temperature_bar",
        "data": fig.to_dict(),
        "layout": fig.layout.to_dict()
    }

def create_air_quality_bar_chart(air_quality_data: List[Dict[str, Any]], city: str) -> Dict[str, Any]:
    """
    Create a bar chart for air quality components
    """
    # Extract components data
    components = ['PM2.5', 'PM10', 'NO2', 'O3', 'SO2', 'CO']
    values = []
    
    for component in ['pm2_5', 'pm10', 'no2', 'o3', 'so2', 'co']:
        if air_quality_data and component in air_quality_data[0]:
            val = air_quality_data[0][component]
            if component == 'co':
                val = val / 1000  # Convert CO from μg/m³ to mg/m³
            values.append(val)
        else:
            values.append(0)
    
    # Define colors for each component
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=components,
        y=values,
        marker_color=colors,
        text=[f'{val:.2f}' for val in values],
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>Value: %{y:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': f'Air Quality Components - {city}',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16}
        },
        xaxis_title='Air Quality Component',
        yaxis_title='Concentration',
        template='plotly_white',
        height=400
    )
    
    return {
        "chart_type": "air_quality_bar",
        "data": fig.to_dict(),
        "layout": fig.layout.to_dict()
    }

def create_weather_conditions_bar_chart(weather_data: List[Dict[str, Any]], city: str) -> Dict[str, Any]:
    """
    Create a bar chart for weather conditions frequency
    """
    # Count weather conditions
    weather_counts = {}
    for item in weather_data:
        condition = item.get('weather', 'Unknown')
        weather_counts[condition] = weather_counts.get(condition, 0) + 1
    
    # Sort by frequency
    sorted_conditions = sorted(weather_counts.items(), key=lambda x: x[1], reverse=True)
    conditions = [item[0] for item in sorted_conditions]
    counts = [item[1] for item in sorted_conditions]
    
    # Define colors
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#FFB6C1', '#98FB98']
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=conditions,
        y=counts,
        marker_color=colors[:len(conditions)],
        text=counts,
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>Frequency: %{y}<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': f'Weather Conditions Frequency - {city}',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16}
        },
        xaxis_title='Weather Condition',
        yaxis_title='Frequency',
        template='plotly_white',
        height=400,
        xaxis=dict(tickangle=45)
    )
    
    return {
        "chart_type": "weather_conditions_bar",
        "data": fig.to_dict(),
        "layout": fig.layout.to_dict()
    }

def create_hourly_temperature_bar_chart(hourly_data: List[Dict[str, Any]], city: str) -> Dict[str, Any]:
    """
    Create a bar chart for hourly temperature variations
    """
    hours = []
    temperatures = []
    
    for item in hourly_data:
        # Extract hour from datetime
        dt = datetime.strptime(item['datetime'], '%Y-%m-%d %H:%M:%S')
        hours.append(dt.strftime('%H:%M'))
        temperatures.append(item['temperature'])
    
    # Create color gradient based on temperature
    colors = []
    for temp in temperatures:
        if temp < 0:
            colors.append('#0000FF')
        elif temp < 10:
            colors.append('#87CEEB')
        elif temp < 20:
            colors.append('#4ECDC4')
        elif temp < 30:
            colors.append('#FFB347')
        else:
            colors.append('#FF6B6B')
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=hours,
        y=temperatures,
        marker_color=colors,
        text=[f'{temp:.1f}°C' for temp in temperatures],
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>Temperature: %{y:.1f}°C<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': f'Hourly Temperature Variations - {city}',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16}
        },
        xaxis_title='Time',
        yaxis_title='Temperature (°C)',
        template='plotly_white',
        height=400,
        xaxis=dict(tickangle=45)
    )
    
    return {
        "chart_type": "hourly_temperature_bar",
        "data": fig.to_dict(),
        "layout": fig.layout.to_dict()
    }

def create_wind_speed_bar_chart(wind_data: List[Dict[str, Any]], city: str) -> Dict[str, Any]:
    """
    Create a bar chart for wind speed variations
    """
    dates = []
    wind_speeds = []
    
    for item in wind_data:
        dates.append(item['datetime'])
        wind_speeds.append(item['wind_speed'])
    
    # Create color gradient based on wind speed
    colors = []
    for speed in wind_speeds:
        if speed < 2:
            colors.append('#90EE90')  # Light green for calm
        elif speed < 5:
            colors.append('#FFEAA7')  # Yellow for light breeze
        elif speed < 10:
            colors.append('#FFB347')  # Orange for moderate breeze
        else:
            colors.append('#FF6B6B')  # Red for strong wind
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=dates,
        y=wind_speeds,
        marker_color=colors,
        text=[f'{speed:.1f} m/s' for speed in wind_speeds],
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>Wind Speed: %{y:.1f} m/s<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': f'Wind Speed Variations - {city}',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16}
        },
        xaxis_title='Date',
        yaxis_title='Wind Speed (m/s)',
        template='plotly_white',
        height=400,
        xaxis=dict(tickangle=45)
    )
    
    return {
        "chart_type": "wind_speed_bar",
        "data": fig.to_dict(),
        "layout": fig.layout.to_dict()
    }
