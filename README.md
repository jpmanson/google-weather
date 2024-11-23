# pygoogleweather

`pygoogleweather` is a Python library to get weather information from Google Search. No API keys required.

## Features

- Fetch current weather information for any city.
- Supports multiple languages.
- Convert temperature units between Celsius, Fahrenheit, and Kelvin.
- Get wind speed in km/h or mph.

## Installation

You can install the library using pip:

```bash
pip install pygoogleweather
```

## Usage
```python
from google_weather.weather import get_current_weather

result = get_current_weather('Buenos Aires')
print(result)
# {'temperature': '24.0°C', 'humidity': '72%', 'wind': '34 kmh', 'condition': 'Mayormente soleado', 'location': 'Buenos Aires, Cdad. Autónoma de Buenos Aires'}
```

You can also specify the language, temperature unit, and wind unit:

```python
print(get_current_weather('Buenos Aires', lang='it', temp_unit='F', wind_unit='mph'))
# {'temperature': '75.2°F', 'humidity': '72%', 'wind': '21 mph', 'condition': 'Per lo più soleggiato', 'location': 'Buenos Aires, Città Autonoma di Buenos Aires'}

print(get_current_weather('New York', lang='en'))
# {'temperature': '37.4°F', 'humidity': '40%', 'wind': '11 mph', 'condition': 'Mostly Cloudy', 'location': 'New York, NY'}
```

