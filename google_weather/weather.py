import logging
from typing import Dict, Any
from pathlib import Path
from playwright.async_api import async_playwright
import re
from bs4 import BeautifulSoup
from datetime import datetime
import brotli
import html
from google_weather.lang import lang_queries
import os
import requests
import brotli
import html
from pathlib import Path
from playwright.sync_api import sync_playwright
import re

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('weather_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def save_debug_html(content: str, prefix: str = 'debug') -> str:
    """Guarda el HTML de forma legible y devuelve el nombre del archivo"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    debug_dir = Path('debug_responses')
    debug_dir.mkdir(exist_ok=True)
    
    try:
        # Formatear HTML para mejor legibilidad
        soup = BeautifulSoup(content, 'html.parser')
        formatted_html = soup.prettify()
        
        debug_file = debug_dir / f"{prefix}_{timestamp}.html"
        debug_file.write_text(formatted_html, encoding='utf-8')
        logger.debug(f"HTML guardado en {debug_file}")
        return str(debug_file)
    except Exception as e:
        logger.error(f"Error guardando HTML: {str(e)}")
        return "No se pudo guardar el HTML"

class WeatherScraper:
    def __init__(self, headless: bool = True, debug: bool = False):
        self.headless = headless
        self.debug = debug
        self.debug_dir = Path("debug_screenshots") if debug else None
        if self.debug_dir:
            self.debug_dir.mkdir(exist_ok=True)
            
    async def get_weather(self, city: str, lang: str = 'en', temp_unit: str = 'C', wind_unit: str = 'kmh') -> Dict[str, Any]:
        """Gets current weather for a city using Playwright"""
        async with async_playwright() as p:
            # Launch browser with stealth mode
            browser = await p.chromium.launch(
                headless=self.headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--disable-site-isolation-trials'
                ]
            )
            
            # Create context with specific options
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                locale=lang,
                timezone_id='Europe/London',
                permissions=['geolocation'],
                java_script_enabled=True
            )
            
            # Add stealth scripts
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
            page = await context.new_page()
            
            try:
                # First visit Google homepage
                await page.goto('https://www.google.com')
                
                # Handle consent dialog if present
                try:
                    consent_button = page.get_by_role("button", name=re.compile("Accept|Aceptar", re.IGNORECASE))
                    if await consent_button.is_visible(timeout=5000):
                        await consent_button.click()
                except Exception:
                    pass  # No consent dialog or error handling it
                
                # Search for weather
                search_box = await page.wait_for_selector('textarea[name="q"]')
                await search_box.fill(f'weather {city}')
                await search_box.press('Enter')
                
                # Wait for navigation and weather widget
                await page.wait_for_load_state('networkidle')
                await page.wait_for_selector('#wob_wc', timeout=10000)
                
                if self.debug:
                    await page.screenshot(path=str(self.debug_dir / "weather_widget.png"))
                
                # Extract weather data
                data = {}
                
                # Location - usando múltiples selectores y estrategias
                location_selectors = [
                    'div.wob_loc',  # Selector original
                    '#wob_loc',     # Selector alternativo
                    'div[class*="q8U8x"] >> text=Clima en',  # Nuevo formato español
                    f'text=Weather in {city}',  # Formato inglés
                    f'text=Clima en {city}',    # Formato español
                    f'text=Météo à {city}',     # Formato francés
                ]
                
                location = None
                for selector in location_selectors:
                    try:
                        location_elem = await page.query_selector(selector)
                        if location_elem:
                            location_text = await location_elem.text_content()
                            # Limpiar el texto de la ubicación
                            location_text = (
                                location_text.replace('Weather in ', '')
                                .replace('Clima en ', '')
                                .replace('Météo à ', '')
                                .replace('Weather for ', '')
                                .replace('Clima para ', '')
                                .strip()
                            )
                            if city.lower() in location_text.lower():
                                location = location_text
                                break
                    except Exception:
                        continue
                
                # Si no encontramos la ubicación en los selectores, usar la ciudad original
                if not location:
                    location = city
                
                data['location'] = location
                
                # Temperature
                temp_elem = await page.query_selector('#wob_tm')
                if temp_elem:
                    temp = await temp_elem.text_content()
                    temp_value = float(temp)
                    
                    # Convert temperature if needed
                    if temp_unit == 'F':
                        temp_value = (temp_value * 9/5) + 32
                    elif temp_unit == 'K':
                        temp_value = temp_value + 273.15
                    
                    data['temperature'] = f"{round(temp_value, 1)}°{temp_unit}"
                
                # Condition
                condition_elem = await page.query_selector('#wob_dc')
                if condition_elem:
                    data['condition'] = await condition_elem.text_content()
                
                # Humidity
                humidity_elem = await page.query_selector('#wob_hm')
                if humidity_elem:
                    data['humidity'] = await humidity_elem.text_content()
                
                # Wind
                wind_selector = '#wob_tws' if wind_unit == 'mph' else '#wob_ws'
                wind_elem = await page.query_selector(wind_selector)
                if wind_elem:
                    data['wind'] = await wind_elem.text_content()
                
                if not all(k in data for k in ['temperature', 'condition', 'humidity', 'wind', 'location']):
                    missing = [k for k in ['temperature', 'condition', 'humidity', 'wind', 'location'] if k not in data]
                    raise Exception(f"Missing weather data: {', '.join(missing)}")
                
                return data
                
            except Exception as e:
                if self.debug:
                    await page.screenshot(path=str(self.debug_dir / "error.png"))
                    logger.error(f"Failed to get weather data: {str(e)}")
                raise Exception(f"Error getting weather: {str(e)}")
            
            finally:
                await context.close()
                await browser.close()

# Crear una función helper para uso síncrono
def get_weather_sync(city: str, lang: str = 'en', temp_unit: str = 'C', wind_unit: str = 'kmh') -> Dict[str, Any]:
    """Versión síncrona del scraper para compatibilidad"""
    import asyncio
    scraper = WeatherScraper()
    return asyncio.run(scraper.get_weather(city, lang, temp_unit, wind_unit))