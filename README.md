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

In Google Colab, you need to handle event loops differently. Here's how to use the library in Colab:

1. First, install the required dependencies:
```python
!pip install pygoogleweather nest-asyncio
!playwright install chromium
```

2. Import and configure:
```python
import asyncio
import nest_asyncio
from google_weather.weather import WeatherScraper

# Enable nested event loops (required for Colab)
nest_asyncio.apply()

# Create scraper
scraper = WeatherScraper()

# Function to run async code in Colab
def run_async(coroutine):
    return asyncio.get_event_loop().run_until_complete(coroutine)
```

3. Get weather data:
```python
# Get weather for New York
result = run_async(scraper.get_weather('New York'))
print(result)

# Get weather with custom options
result = run_async(scraper.get_weather(
    'Paris',
    lang='fr',
    temp_unit='C',
    wind_unit='kmh'
))
print(result)
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

