import logging
from typing import Dict, Any
from pathlib import Path
from playwright.sync_api import sync_playwright
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
            
    def get_weather(self, city: str, lang: str = 'en', temp_unit: str = 'C', wind_unit: str = 'kmh') -> Dict[str, Any]:
        """Gets current weather for a city using Playwright"""
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(
                headless=self.headless,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            # Create context
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1280, 'height': 720},
                locale=lang
            )
            
            page = context.new_page()
            
            try:
                # Visit Google and search for weather
                page.goto('https://www.google.com')
                if self.debug:
                    page.screenshot(path=str(self.debug_dir / "1_homepage.png"))
                
                # Handle consent dialog if present
                try:
                    consent_button = page.get_by_role(
                        "button", 
                        name=re.compile("Accept|Aceptar", re.IGNORECASE)
                    )
                    if consent_button.is_visible(timeout=5000):
                        consent_button.click()
                except Exception as e:
                    logger.debug(f"No consent dialog or error: {str(e)}")
                
                # Search for weather
                search_box = page.locator('textarea[name="q"]')
                search_box.fill(f'weather {city}')
                search_box.press('Enter')
                page.wait_for_load_state('networkidle')
                
                if self.debug:
                    page.screenshot(path=str(self.debug_dir / "2_search.png"))
                
                # Wait for weather widget
                page.wait_for_selector('div[data-wob-di]', timeout=5000)
                
                # Extract weather data using more specific selectors
                selectors = {
                    'temperature': '#wob_tm',
                    'condition': '#wob_dc',
                    'humidity': '#wob_hm',
                    'wind': '#wob_ws',
                    'wind_mph': '#wob_tws',
                    'location': [
                        'div.wob_loc',
                        '#wob_loc',
                        'span.BBwThe'
                    ]
                }
                
                # Mostrar HTML de los elementos del clima
                if self.debug:
                    logger.debug("\nHTML de los elementos del clima:")
                    temp_html = page.locator('#wob_tm').first.evaluate('el => el.outerHTML')
                    condition_html = page.locator('#wob_dc').first.evaluate('el => el.outerHTML')
                    humidity_html = page.locator('#wob_hm').first.evaluate('el => el.parentElement.outerHTML')
                    wind_html = page.locator('#wob_ws').first.evaluate('el => el.parentElement.outerHTML')
                    
                    logger.debug(f"Temperatura HTML: {temp_html}")
                    logger.debug(f"Condición HTML: {condition_html}")
                    logger.debug(f"Humedad HTML: {humidity_html}")
                    logger.debug(f"Viento HTML: {wind_html}")
                
                data = {}
                for field, selector in selectors.items():
                    if isinstance(selector, list):
                        # Try multiple selectors for this field
                        for sel in selector:
                            try:
                                elem = page.locator(sel).first
                                if elem and elem.is_visible():
                                    text = elem.text_content().strip()
                                    if field == 'location' and city.lower() in text.lower():
                                        data[field] = text
                                        break
                            except Exception as e:
                                logger.debug(f"Error with selector {sel}: {str(e)}")
                    else:
                        try:
                            elem = page.locator(selector).first
                            if elem and elem.is_visible():
                                data[field] = elem.text_content().strip()
                        except Exception as e:
                            logger.debug(f"Error with selector {selector}: {str(e)}")
                
                # Use city name if location not found
                if 'location' not in data:
                    data['location'] = city
                
                # Convert temperature if needed
                if 'temperature' in data:
                    temp_value = float(data['temperature'])
                    if temp_unit == 'F':
                        temp_value = (temp_value * 9/5) + 32
                    elif temp_unit == 'K':
                        temp_value = temp_value + 273.15
                    data['temperature'] = f"{temp_value}°{temp_unit}"
                
                # Get wind speed in desired unit
                if wind_unit == 'mph':
                    wind_elem = page.locator('#wob_tws').first
                else:
                    wind_elem = page.locator('#wob_ws').first
                
                if wind_elem and wind_elem.is_visible():
                    wind_speed = wind_elem.text_content().strip()
                else:
                    # Fallback to default wind speed and convert if needed
                    wind_elem = page.locator('#wob_ws').first
                    if wind_elem and wind_elem.is_visible():
                        wind_text = wind_elem.text_content().strip()
                        if wind_unit == 'mph' and 'km/h' in wind_text:
                            # Convert from km/h to mph
                            speed = float(wind_text.replace('km/h', '').strip())
                            wind_speed = f"{round(speed * 0.621371)} mph"
                        else:
                            wind_speed = wind_text
                    else:
                        wind_speed = "N/A"
                
                if not all(k in data for k in ['temperature', 'condition', 'humidity', 'wind']):
                    missing = [k for k in ['temperature', 'condition', 'humidity', 'wind'] if k not in data]
                    raise Exception(f"Missing weather data: {', '.join(missing)}")
                
                if self.debug:
                    page.screenshot(path=str(self.debug_dir / "3_weather.png"))
                    logger.debug("Weather data found:")
                    for k, v in data.items():
                        logger.debug(f"  {k}: {v}")
                
                return {
                    "temperature": data['temperature'],
                    "condition": data['condition'],
                    "humidity": data['humidity'],
                    "wind": wind_speed,
                    "location": data['location']
                }
                
            except Exception as e:
                if self.debug:
                    page.screenshot(path=str(self.debug_dir / "error.png"))
                    logger.error(f"Failed to get weather data: {str(e)}")
                    logger.error(f"Current URL: {page.url}")
                    try:
                        content = page.content()
                        error_file = self.debug_dir / "error.html"
                        error_file.write_text(content, encoding='utf-8')
                        logger.error(f"Page content saved to: {error_file}")
                    except Exception as save_error:
                        logger.error(f"Failed to save error page: {str(save_error)}")
                raise Exception(f"Error getting weather: {str(e)}")
            
            finally:
                context.close()
                browser.close()

# Alias para mantener compatibilidad con código existente
get_current_weather = WeatherScraper().get_weather