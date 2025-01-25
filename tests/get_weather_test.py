import pytest
from google_weather.weather import WeatherScraper
from typing import Dict, Any

# Configurar pytest-asyncio como el backend por defecto
pytest_plugins = ('pytest_asyncio',)

@pytest.fixture(scope="function")
async def scraper():
    """Fixture para crear una instancia de WeatherScraper para cada test"""
    _scraper = WeatherScraper(debug=True)
    yield _scraper

@pytest.mark.asyncio
class TestWeatherScraper:
    async def test_get_weather_buenos_aires(self, scraper):
        """Test getting weather for Buenos Aires in Spanish"""
        result = await scraper.get_weather('Buenos Aires', lang='es')
        
        # Verify structure
        assert isinstance(result, dict)
        assert set(result.keys()) == {'temperature', 'humidity', 'wind', 'condition', 'location'}
        
        # Verify data types and formats
        assert result['temperature'].endswith('°C')
        assert result['humidity'].endswith('%')
        assert any(unit in result['wind'] for unit in ['km/h', 'kmh'])
        assert result['condition'].strip()
        assert 'buenos aires' in result['location'].lower()

    async def test_get_weather_custom_units(self, scraper):
        """Test getting weather with custom units"""
        result = await scraper.get_weather(
            'New York',
            lang='en',
            temp_unit='F',
            wind_unit='mph'
        )
        
        # Verify units
        assert result['temperature'].endswith('°F')
        assert 'mph' in result['wind'].lower()
        assert 'new york' in result['location'].lower()

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