from google_weather.weather import get_current_weather

print(get_current_weather('Buenos Aires'))
print(get_current_weather('Buenos Aires', wind_unit='mph', lang='it', temp_unit='F'))
print(get_current_weather('New York', lang='en'))