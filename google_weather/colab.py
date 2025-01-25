import asyncio
import tracemalloc
import nest_asyncio
from typing import Dict, Any
from .weather import WeatherScraper

class ColabWeatherClient:
    """Cliente especial para Google Colab que maneja automáticamente la configuración async"""
    
    def __init__(self, debug: bool = False):
        # Configurar el entorno de Colab
        if not tracemalloc.is_running():
            tracemalloc.start()
        nest_asyncio.apply()
        
        # Crear el scraper
        self.scraper = WeatherScraper(debug=debug)
    
    def get_weather(self, city: str, lang: str = 'en', temp_unit: str = 'C', wind_unit: str = 'kmh') -> Dict[str, Any]:
        """
        Obtiene el clima para una ciudad de forma síncrona (para uso fácil en Colab)
        
        Args:
            city: Nombre de la ciudad
            lang: Código de idioma ('en', 'es', 'fr', etc.)
            temp_unit: Unidad de temperatura ('C', 'F', 'K')
            wind_unit: Unidad de viento ('kmh', 'mph')
            
        Returns:
            Dict con información del clima
        """
        async def _get_weather():
            return await self.scraper.get_weather(city, lang, temp_unit, wind_unit)
        
        return asyncio.get_event_loop().run_until_complete(_get_weather()) 