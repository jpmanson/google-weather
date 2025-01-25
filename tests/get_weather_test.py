import unittest
from google_weather.weather import WeatherScraper
import pytest
from typing import Dict, Any
import time

class TestWeatherScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = WeatherScraper(debug=True)

    def test_get_weather_buenos_aires(self):
        """Test getting weather for Buenos Aires in Spanish"""
        result = self.scraper.get_weather('Buenos Aires', lang='es')
        
        # Verify structure
        self.assertIsInstance(result, dict)
        self.assertEqual(
            set(result.keys()), 
            {'temperature', 'humidity', 'wind', 'condition', 'location'}
        )
        
        # Verify data types and formats
        self.assertTrue(result['temperature'].endswith('°C'))
        self.assertTrue(result['humidity'].endswith('%'))
        self.assertTrue(any(unit in result['wind'] for unit in ['km/h', 'kmh']))
        self.assertTrue(result['condition'].strip())
        self.assertTrue('buenos aires' in result['location'].lower())

    def test_get_weather_custom_units(self):
        """Test getting weather with custom units"""
        result = self.scraper.get_weather(
            'New York', 
            lang='en',
            temp_unit='F',
            wind_unit='mph'
        )
        
        # Verify units
        self.assertTrue(result['temperature'].endswith('°F'))
        self.assertTrue('mph' in result['wind'].lower())
        self.assertTrue('new york' in result['location'].lower())

    def test_get_weather_multiple_languages(self):
        """Test getting weather in different languages"""
        # Test in English
        result_en = self.scraper.get_weather('Paris', lang='en')
        self.assertTrue('paris' in result_en['location'].lower())
        
        # Test in French
        result_fr = self.scraper.get_weather('Paris', lang='fr')
        self.assertTrue('paris' in result_fr['location'].lower())

    def test_get_weather_invalid_city(self):
        """Test getting weather for an invalid city"""
        with self.assertRaises(Exception) as context:
            self.scraper.get_weather('ThisCityDoesNotExist12345')
        self.assertTrue('Error getting weather' in str(context.exception))

def test_get_weather_playwright():
    """Test using Playwright directly"""
    scraper = WeatherScraper(debug=True)
    
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
    result_es = scraper.get_weather('Buenos Aires', lang='es')
    assert validate_weather_data(result_es, 'Buenos Aires')
    
    # Test in English
    result_en = scraper.get_weather('Buenos Aires', lang='en')
    assert validate_weather_data(result_en, 'Buenos Aires')

if __name__ == '__main__':
    unittest.main()