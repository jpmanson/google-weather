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

Basic usage:
```python
from google_weather.weather import WeatherScraper

# Create a scraper instance
scraper = WeatherScraper()

# Get weather for a city
result = scraper.get_weather('Buenos Aires')
print(result)
# {'temperature': '24.0°C', 'humidity': '72%', 'wind': '34 kmh', 'condition': 'Mayormente soleado', 'location': 'Buenos Aires, Cdad. Autónoma de Buenos Aires'}
```

You can also specify the language, temperature unit, and wind unit:

```python
# Get weather in Italian with Fahrenheit and mph
result = scraper.get_weather(
    'Buenos Aires', 
    lang='it',
    temp_unit='F',
    wind_unit='mph'
)
print(result)
# {'temperature': '75.2°F', 'humidity': '72%', 'wind': '21 mph', 'condition': 'Per lo più soleggiato', 'location': 'Buenos Aires, Città Autonoma di Buenos Aires'}

# Get weather in English
result = scraper.get_weather('New York', lang='en')
print(result)
# {'temperature': '37.4°F', 'humidity': '40%', 'wind': '11 mph', 'condition': 'Mostly Cloudy', 'location': 'New York, NY'}
```

### Debug Mode

You can enable debug mode to save screenshots and HTML content during scraping:

```python
scraper = WeatherScraper(debug=True)
result = scraper.get_weather('Tokyo')
```

This will save screenshots and HTML files in a `debug_screenshots` directory.

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

## License

This project is licensed under the MIT License - see the LICENSE file for details.

