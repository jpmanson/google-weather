from http.cookiejar import debug

import pytest
from google_weather.weather import WeatherScraper
from typing import Dict, Any
from google_weather.lang import weather_conditions
import re

# Configurar pytest-asyncio como el backend por defecto
pytest_plugins = ('pytest_asyncio',)

@pytest.fixture
async def scraper():
    """Create a WeatherScraper instance"""
    scraper = WeatherScraper(headless=True, debug=True)
    yield scraper
    await scraper.close()  # Asegurar que se cierren los recursos

@pytest.mark.asyncio
class TestWeatherScraper:
    async def test_get_weather_buenos_aires(self, scraper):
        """Test getting weather for Buenos Aires in Spanish"""
        result = await scraper.get_weather('Buenos Aires', lang='es')
        
        # Verificar que las unidades por defecto son correctas para es-ES
        assert result['temperature'].endswith('°C')  # Correcto, es el default
        assert result['humidity'].endswith('%')
        assert any(unit in result['wind'] for unit in ['km/h', 'kmh'])  # Correcto para es-ES
        assert result['condition'].strip()
        assert 'buenos aires' in result['location'].lower()

    async def test_get_weather_custom_units(self, scraper):
        """Test getting weather with custom units"""
        # Modificar para probar unidades por defecto de en-US
        result_default = await scraper.get_weather(
            'New York',
            lang='en'
        )
        # Debería usar las unidades por defecto de en-US
        assert result_default['temperature'].endswith('°F')
        assert 'mph' in result_default['wind'].lower()
        
        # Probar override de unidades
        result_custom = await scraper.get_weather(
            'New York',
            lang='en',
            temp_unit='C',
            wind_unit='kmh'
        )
        assert result_custom['temperature'].endswith('°C')
        assert 'km/h' in result_custom['wind'].lower()

    async def test_get_weather_multiple_languages(self, scraper):
        """Test getting weather in different languages"""
        # Test in English
        result_en = await scraper.get_weather('Paris', lang='en')
        assert 'paris' in result_en['location'].lower()
        
        # Test in French
        result_fr = await scraper.get_weather('Paris', lang='fr')
        assert 'paris' in result_fr['location'].lower()

    async def test_get_weather_invalid_city(self, scraper):
        """Test getting weather for an invalid city"""
        with pytest.raises(Exception) as exc_info:
            await scraper.get_weather('ThisCityDoesNotExist12345')
        assert 'Error getting weather' in str(exc_info.value)

    async def test_temperature_range_validation(self, scraper):
        """Test that temperatures are within reasonable ranges"""
        cities = ['Buenos Aires', 'New York', 'Moscow', 'Dubai']
        
        for city in cities:
            result = await scraper.get_weather(city)
            # Extraer valor numérico y unidad
            match = re.match(r'([\d.]+)°([CF])', result['temperature'])
            assert match, f"Formato de temperatura inválido: {result['temperature']}"
            
            temp = float(match.group(1))
            unit = match.group(2)
            
            # Convertir a Celsius si está en Fahrenheit
            if unit == 'F':
                temp = (temp - 32) * 5/9
            
            # Verificar rango razonable en Celsius
            assert -50 <= temp <= 50, f"Temperatura fuera de rango: {temp}°C"

    async def test_location_name_cleaning(self, scraper):
        """Test that location names are properly cleaned"""
        test_cases = [
            ('Buenos Aires', 'es', ['hourly', 'forecast', 'clima', 'weather', '|']),
            ('New York', 'en', ['hourly', 'forecast', 'weather', '|', 'day']),
            ('Paris', 'fr', ['météo', 'hourly', 'forecast', '|']),
            ('Tokyo', 'en', ['weather', 'forecast', 'hourly', '|'])
        ]
        
        for city, lang, forbidden_terms in test_cases:
            result = await scraper.get_weather(city, lang=lang)
            location = result['location'].lower()
            
            # Verify no unwanted patterns
            for term in forbidden_terms:
                assert term.lower() not in location, f"Found '{term}' in location: {result['location']}"
            
            # Verify city name is present
            assert city.lower() in location, f"City name not found in location: {result['location']}"
            
            # Basic validation
            assert 2 <= len(result['location']) <= 50, f"Location name length suspicious: {result['location']}"
            
            # Verify basic structure
            assert result['location'].strip() == result['location'], f"Location has leading/trailing spaces: '{result['location']}'"
            assert '  ' not in result['location'], f"Location has multiple spaces: '{result['location']}'"

    async def test_location_name_variations(self, scraper):
        """Test location name cleaning with various input formats"""
        test_cases = [
            ('New York', 'Weather in New York Hourly'),
            ('Paris', 'Météo à Paris | 7 Day Forecast'),
            ('Tokyo', 'Tokyo Weather - 14 Day Forecast'),
            ('Buenos Aires', 'Clima en Buenos Aires | Pronóstico')
        ]
        
        for expected_city, input_location in test_cases:
            # Use the public method name
            cleaned = scraper.clean_location(input_location)
            assert cleaned == expected_city

    async def test_weather_conditions_translation(self, scraper):
        """Test weather condition translations"""
        # Probar cada idioma soportado
        test_cities = {
            'es': 'Madrid',
            'en': 'London',
            'fr': 'Paris',
            'de': 'Berlin'
        }
        
        for lang, city in test_cities.items():
            result = await scraper.get_weather(city, lang=lang)
            condition = result['condition'].lower()
            
            # Verificar que la condición está en el idioma correcto
            lang_conditions = weather_conditions.get(lang, weather_conditions['en'])
            assert any(
                value.lower() in condition 
                for value in lang_conditions.values()
            ), f"Condition '{condition}' not found in {lang} translations"

    async def test_locale_configurations(self, scraper):
        """Test locale-specific configurations"""
        from google_weather.lang import locale_configs
        
        test_cases = [
            ('New York', 'en', 'en-US', 'F', 'mph'),
            ('London', 'en-GB', 'en-GB', 'C', 'mph'),
            ('Paris', 'fr', 'fr-FR', 'C', 'kmh'),
            ('Madrid', 'es', 'es-ES', 'C', 'kmh')
        ]
        
        for city, lang, expected_locale, expected_temp_unit, expected_wind_unit in test_cases:
            result = await scraper.get_weather(city, lang=lang)
            
            # Verificar unidades según la configuración regional
            assert result['temperature'].endswith(f'°{expected_temp_unit}')
            assert expected_wind_unit in result['wind'].lower()

    async def test_error_handling(self, scraper):
        """Test error handling scenarios"""
        # Probar ciudad inválida
        with pytest.raises(Exception) as exc_info:
            await scraper.get_weather('ThisCityDoesNotExist12345')
        assert any(msg in str(exc_info.value) for msg in [
            'Error getting weather',
            'No se pudo extraer una ubicación válida',
            'Widget del clima no encontrado'
        ])
        
        # Probar idioma no soportado
        result = await scraper.get_weather('Paris', lang='xx')
        # Debería usar el idioma por defecto (en)
        assert any(unit in result['temperature'] for unit in ['°F', '°C'])
        
        # Probar unidades inválidas
        with pytest.raises(ValueError):
            await scraper.get_weather('Paris', temp_unit='X')

    async def test_location_cleaning_extended(self, scraper):
        """Test extended location name cleaning"""
        test_cases = [
            ('Buenos Aires, Argentina', 'Buenos Aires'),
            ('Weather in New York, NY', 'New York'),
            ('Météo à Paris, France', 'Paris'),
            ('Wetter in Berlin - Deutschland', 'Berlin')
        ]
        
        for input_location, expected in test_cases:
            cleaned = scraper.clean_location(input_location)
            assert cleaned == expected, f"Failed cleaning '{input_location}'"

@pytest.mark.asyncio
async def test_get_weather_playwright(scraper):
    """Test using Playwright directly"""
    def validate_weather_data(result: Dict[str, Any], city: str):
        # Verify structure
        assert isinstance(result, dict)
        assert set(result.keys()) == {'temperature', 'humidity', 'wind', 'condition', 'location'}
        
        # Verify temperature format and range
        assert result['temperature'].endswith('°C')
        temp = float(result['temperature'].rstrip('°C'))
        assert -50 <= temp <= 50
        
        # Verify humidity format and range
        assert result['humidity'].endswith('%')
        humidity = int(result['humidity'].rstrip('%'))
        assert 0 <= humidity <= 100
        
        # Verify wind format
        assert any(unit in result['wind'] for unit in ['km/h', 'kmh', 'mph'])
        
        # Verify condition and location
        assert result['condition'].strip()
        assert city.lower() in result['location'].lower()
        
        return True
    
    # Test in Spanish
    result_es = await scraper.get_weather('Buenos Aires', lang='es')
    assert validate_weather_data(result_es, 'Buenos Aires')
    
    # Test in English
    result_en = await scraper.get_weather('Buenos Aires', lang='en')
    assert validate_weather_data(result_en, 'Buenos Aires')