# pygoogleweather

`pygoogleweather` is a Python library to get weather information from Google Search. No API keys required.

## Features

- Fetch current weather information for any city
- Supports multiple languages
- Convert temperature units between Celsius, Fahrenheit, and Kelvin
- Get wind speed in km/h or mph
- Reliable web scraping using Playwright

## Installation

1. Install the library using pip:

```bash
pip install pygoogleweather
```

2. Install Playwright's browser (required):

```bash
playwright install chromium
```

## Usage

### Basic Usage

```python
from google_weather.weather import get_weather_sync

# Get weather for a city (returns a dictionary with weather information)
result = get_weather_sync('Buenos Aires')
print(result)
# Output:
# {
#     'temperature': '24.0°C',
#     'humidity': '72%',
#     'wind': '34 km/h',
#     'condition': 'Mostly sunny',
#     'location': 'Buenos Aires, Argentina'
# }
```

### Advanced Usage (with async)

```python
import asyncio
from google_weather.weather import WeatherScraper

async def main():
    # Create a scraper instance with custom options
    scraper = WeatherScraper(headless=True, debug=False)
    
    try:
        # Get weather with custom language and units
        result = await scraper.get_weather(
            city='Paris',
            lang='fr',          # French language
            temp_unit='F',      # Fahrenheit
            wind_unit='mph'     # Miles per hour
        )
        print(result)
    finally:
        # Always close the scraper to free resources
        await scraper.close()

# Run the async function
asyncio.run(main())
```

### Using in Google Colab

The library provides a special client for Google Colab that handles all the async complexity for you:

```python
# Install
!pip install pygoogleweather
!playwright install chromium

from google_weather.colab import ColabWeatherClient

# Crear cliente
weather = ColabWeatherClient()

# Buenos Aires
result = weather.get_weather('Buenos Aires', lang='es')
print("\nBuenos Aires (ES):")
print(result)
# Buenos Aires (ES):
# {'location': 'Buenos Aires, Cdad. Autónoma de Buenos Aires, Argentina', 'temperature': '26.7°C', 'condition': 'Parcialmente nublado', 'humidity': '53%', 'wind': '12.0 km/h'}


# New York
result = weather.get_weather('New York', lang='en', temp_unit='F', wind_unit='mph')
print("\nNew York (EN, °F, mph):")
print(result)
# New York (EN, °F, mph):
# {'location': 'New York, NY', 'temperature': '30.0°F', 'condition': 'Partly cloudy', 'humidity': '45%', 'wind': '6.0 mph'}

# Paris
result = weather.get_weather('Paris', lang='fr', temp_unit='C', wind_unit='kmh')
print("\nParis (FR, °C, kmh):")
print(result)
# Paris (FR, °C, kmh):
# {'location': 'Paris, France', 'temperature': '3.9°C', 'condition': 'Nuageux', 'humidity': '93%', 'wind': '12.0 km/h'}
```

### Debug Mode

You can enable debug mode to save screenshots during scraping:

```python
scraper = WeatherScraper(debug=True)  # Screenshots will be saved in 'debug_screenshots' directory
```

### Options

The `WeatherScraper` class accepts these parameters:
- `headless` (bool): Run browser in headless mode (default: True)
- `debug` (bool): Enable debug mode with screenshots (default: False)

The `get_weather` method accepts:
- `city` (str): City name
- `lang` (str): Language code (default: 'en')
- `temp_unit` (str): Temperature unit ('C', 'F', or 'K', default: 'C')
- `wind_unit` (str): Wind speed unit ('kmh' or 'mph', default: 'kmh')

## Requirements

- Python 3.9+
- Playwright
- Chromium browser (installed via `playwright install`)
- nest-asyncio (for Google Colab usage)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

