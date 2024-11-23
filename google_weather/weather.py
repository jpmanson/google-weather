import requests
from bs4 import BeautifulSoup
from typing import Dict, Any
from google_weather.lang import lang_queries


def get_current_weather(city: str, lang: str = 'es', temp_unit: str = 'C', wind_unit: str = 'kmh') -> Dict[str, Any]:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    query = lang_queries[lang].format(city=city.replace(' ', '+'))
    url = f"https://www.google.com/search?hl={lang}&lr=lang_en&q={query}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Error getting weather: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract weather elements
    temp = soup.select_one("#wob_tm")
    humidity = soup.select_one("#wob_hm")
    wind = soup.select_one("#wob_ws")
    condition = soup.select_one("#wob_dc")
    location = (
        soup.find("span", class_="BBwThe") or
        soup.find("div", class_="wob_loc") or
        soup.select_one("#wob_loc")
    )

    if not all([temp, humidity, wind, condition, location]):
        missing = []
        if not temp: missing.append("temperature")
        if not humidity: missing.append("humidity")
        if not wind: missing.append("wind")
        if not condition: missing.append("condition")
        if not location: missing.append("location")

        raise Exception(f"Missing data: {', '.join(missing)}")

    # Primero detectar la unidad que está usando Google
    temp_unit_span = soup.select_one('div.vk_bk.wob-unit span[aria-disabled="true"][style="display:inline"]')
    if not temp_unit_span:
        raise Exception("Cannot find temperature unit")
    
    source_unit = temp_unit_span.text.strip().replace('°', '').upper()
    temp_value = float(temp.text)

    # Primero convertir a Celsius si es necesario
    if source_unit == 'F':
        temp_value = (temp_value - 32) * 5/9
    elif source_unit == 'K':
        temp_value = temp_value - 273.15

    # Ahora convertir de Celsius a la unidad deseada
    if temp_unit == 'F':
        temp_value = round((temp_value * 9/5) + 32, 1)
    elif temp_unit == 'K':
        temp_value = round(temp_value + 273.15, 1)
    else:  # Celsius
        temp_value = round(temp_value, 1)

    # Get wind speed in desired unit
    wind_kmh = soup.select_one('span#wob_ws')
    wind_mph = soup.select_one('span#wob_tws')

    if wind_kmh and wind_mph:
        if wind_unit == 'kmh':
            wind_speed = wind_kmh.text.strip().replace('km/h', 'kmh')
        else:  # mph
            wind_speed = wind_mph.text.strip().replace('mph', 'mph')
    else:
        wind_speed = "N/A"

    weather_data = {
        "temperature": f"{temp_value}°{temp_unit}",
        "humidity": humidity.text,
        "wind": wind_speed,
        "condition": condition.text,
        "location": location.text
    }

    return weather_data