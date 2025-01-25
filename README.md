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

### Basic Usage (Regular Python Environment)

```python
import asyncio
from google_weather.weather import WeatherScraper

async def main():
    # Create a scraper instance
    scraper = WeatherScraper()

    # Get weather for a city
    result = await scraper.get_weather('Buenos Aires')
    print(result)
    # {'temperature': '24.0°C', 'humidity': '72%', 'wind': '34 kmh', 'condition': 'Mayormente soleado', 'location': 'Buenos Aires, Argentina'}

# Run the async function
asyncio.run(main())
```

### Custom Options

```python
async def main():
    scraper = WeatherScraper()
    
    # Get weather in Italian with Fahrenheit and mph
    result = await scraper.get_weather(
        'Buenos Aires', 
        lang='it',
        temp_unit='F',
        wind_unit='mph'
    )
    print(result)
    # {'temperature': '75.2°F', 'humidity': '72%', 'wind': '21 mph', 'condition': 'Per lo più soleggiato', 'location': 'Buenos Aires, Argentina'}

asyncio.run(main())
```

### Using in Google Colab

The library provides a special client for Google Colab that handles all the async complexity for you:

```python
# Install
!pip install pygoogleweather
!playwright install chromium

# Import and use
from google_weather.colab import ColabWeatherClient

# Create client
weather = ColabWeatherClient()

# Get weather data
result = weather.get_weather('New York', lang='en')
print(result)
# {'location': 'New York', 'temperature': '19.4°F', 'condition': 'Sunny', 'humidity': '57%', 'wind': '2 mph'}

# With custom units
result = weather.get_weather(
    'Paris',
    lang='fr',
    temp_unit='C',
    wind_unit='kmh'
)
print(result)
# {'location': 'Paris', 'temperature': '9.0°C', 'condition': 'Nuageux', 'humidity': '85%', 'wind': '6 km/h'}
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

