import logging
from typing import Dict, Any, Optional, List
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
import re
from .lang import lang_queries, weather_labels, locale_configs, weather_conditions, unit_preferences

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
        
        # Cache para browsers/contexts
        self._browser: Optional[Browser] = None
        self._contexts: Dict[str, BrowserContext] = {}
        
    def clean_location(self, location: str) -> str:
        """Cleans location string from various suffixes and formats"""
        if not location:
            return ''
        
        # Remove common prefixes/suffixes
        location = re.sub(r'^(?:weather|tiempo|clima|météo|wetter)\s+(?:in|en|para|à|in)\s+', '', location, flags=re.IGNORECASE)
        location = re.sub(r'\s*-\s*(?:google search|buscar con google).*$', '', location, flags=re.IGNORECASE)
        location = re.sub(r'\s*\|\s*[^|]+$', '', location)
        location = re.sub(r'(?:weather|tiempo|clima)$', '', location, flags=re.IGNORECASE)
        
        # Remove country/region information
        location = re.sub(r',\s*(?:Argentina|NY|France|Deutschland|[A-Z]{2}|[^,]+)$', '', location)
        
        # Remove forecast related terms
        location = re.sub(r'\s*(?:Hourly|Forecast|Pronóstico|7 Day|14 Day).*$', '', location, flags=re.IGNORECASE)
        
        # Clean up any remaining whitespace and special characters
        location = location.strip()
        location = re.sub(r'\s+', ' ', location)
        
        return location

    async def _get_context(self, lang: str) -> BrowserContext:
        """Obtiene o crea un contexto de navegador para el idioma especificado"""
        if lang not in self._contexts:
            if not self._browser:
                self._browser = await self._launch_browser()
            
            # Obtener configuración regional
            lang_config = locale_configs.get(lang, locale_configs['en'])
            
            context = await self._browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                locale=lang_config['locale'],
                timezone_id=lang_config['timezone'],
                permissions=['geolocation'],
                java_script_enabled=True
            )
            
            # Agregar scripts de evasión
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
            self._contexts[lang] = context
            
        return self._contexts[lang]
    
    async def _launch_browser(self) -> Browser:
        """Lanza el navegador con configuraciones optimizadas"""
        playwright = await async_playwright().start()
        return await playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-site-isolation-trials'
            ]
        )
    
    async def _extract_location(self, page: Page, lang: str) -> str:
        """Extrae la ubicación del widget del clima"""
        try:
            # Esperar y obtener el elemento de ubicación usando el selector más genérico
            location_element = await page.wait_for_selector(".BBwThe", timeout=5000)
            
            if location_element:
                full_text = await location_element.text_content()
                if self.debug:
                    logger.debug(f"Texto completo encontrado: {full_text}")
                
                # Eliminar textos de prefijo comunes en diferentes idiomas
                prefixes = ['Resultados para ', 'Results for ', 'Résultats pour ', 'Ergebnisse für ']
                for prefix in prefixes:
                    if full_text.startswith(prefix):
                        full_text = full_text.replace(prefix, '').strip()
                
                # Limpiar y devolver la ubicación
                location = full_text.strip()
                if self.debug:
                    logger.debug(f"Ubicación final: {location}")
                return location
                
            raise ValueError("No se encontró el elemento de ubicación")
            
        except Exception as e:
            if self.debug:
                logger.error(f"Error extrayendo ubicación: {str(e)}")
                await page.screenshot(path=str(self.debug_dir / f"location_error_{lang}.png"))
                content = await page.content()
                logger.debug(f"HTML de la página: {content}")
            raise

    async def _perform_search(self, page: Page, city: str, lang: str) -> None:
        """Realiza la búsqueda del clima"""
        try:
            # Construir y navegar a la URL de búsqueda
            search_query = lang_queries.get(lang, lang_queries['en']).format(city=city.replace(' ', '+'))
            url = f'https://www.google.com/search?q={search_query}&hl={lang}'
            
            if self.debug:
                logger.debug(f"URL de búsqueda: {url}")
            
            await page.goto(url)
            
            # Esperar a que el widget se cargue
            try:
                await page.wait_for_selector('#wob_wc', state='visible')
                
                if self.debug:
                    # Verificar si el widget está realmente presente
                    widget = await page.query_selector('#wob_wc')
                    if widget:
                        html = await page.evaluate('element => element.outerHTML', widget)
                        logger.debug(f"Widget encontrado: {html}")
                    else:
                        logger.debug("Widget no encontrado después de esperar")
                    
                    # Verificar elementos críticos
                    for selector in ['#wob_loc', '#wob_tm', '#wob_dc', '#wob_hm', '#wob_ws']:
                        elem = await page.query_selector(selector)
                        if elem:
                            text = await elem.text_content()
                            logger.debug(f"Elemento {selector} encontrado con texto: {text}")
                        else:
                            logger.debug(f"Elemento {selector} no encontrado")
                
            except Exception as e:
                if self.debug:
                    logger.error(f"Error esperando al widget: {str(e)}")
                    content = await page.content()
                    save_debug_html(content, f"widget_error_{lang}")
                raise Exception("Error getting weather: Widget not found")
            
        except Exception as e:
            if self.debug:
                logger.error(f"Error en búsqueda: {str(e)}")
                await page.screenshot(path=str(self.debug_dir / f"search_error_{lang}.png"))
            raise

    async def get_weather(
        self, 
        city: str, 
        lang: str = 'en',
        temp_unit: str = None,
        wind_unit: str = None,
        retries: int = 2
    ) -> Dict[str, Any]:
        """Obtiene el clima actual usando múltiples estrategias de recuperación"""
        
        # Obtener configuración regional
        lang_config = locale_configs.get(lang, locale_configs['en'])
        locale = lang_config['locale']
        
        # Determinar unidades basadas en la configuración regional si no se especifican
        if temp_unit is None or wind_unit is None:
            unit_prefs = unit_preferences.get(locale, unit_preferences['default'])
            temp_unit = temp_unit or unit_prefs['temp']
            wind_unit = wind_unit or unit_prefs['wind']
        
        context = await self._get_context(lang)
        page = await context.new_page()
        
        try:
            # Realizar búsqueda directamente
            await self._perform_search(page, city, lang)
            
            # Extraer datos
            data = {}
            
            # Ubicación
            data['location'] = await self._extract_location(page, lang)
            
            # Temperatura
            temp_elem = await page.query_selector('#wob_tm')
            if temp_elem:
                temp = float(await temp_elem.text_content())
                if temp_unit == 'F':
                    temp = (temp * 9/5) + 32
                elif temp_unit == 'K':
                    temp = temp + 273.15
                data['temperature'] = f"{round(temp, 1)}°{temp_unit}"
            
            # Condición
            condition_elem = await page.query_selector('#wob_dc')
            if condition_elem:
                condition = await condition_elem.text_content()
                # Intentar traducir la condición si existe en el mapeo
                conditions_map = weather_conditions.get(lang, weather_conditions['en'])
                for key, value in conditions_map.items():
                    if value.lower() in condition.lower():
                        condition = value
                        break
                data['condition'] = condition
            
            # Humedad
            humidity_elem = await page.query_selector('#wob_hm')
            if humidity_elem:
                data['humidity'] = await humidity_elem.text_content()
            
            # Viento
            wind_elem = await page.query_selector('#wob_ws')
            if wind_elem:
                wind_text = await wind_elem.text_content()
                try:
                    wind_value = float(re.search(r'[\d.]+', wind_text).group())
                    
                    # Convertir solo si es necesario
                    if wind_unit == 'mph' and 'km/h' in wind_text.lower():
                        wind_value = wind_value * 0.621371
                    
                    unit_text = 'mph' if wind_unit == 'mph' else 'km/h'
                    data['wind'] = f"{round(wind_value, 1)} {unit_text}"
                except (AttributeError, ValueError):
                    data['wind'] = wind_text
            
            # Validar datos requeridos
            required_fields = ['temperature', 'condition', 'humidity', 'wind', 'location']
            missing = [k for k in required_fields if k not in data]
            if missing:
                raise Exception(f"Faltan datos del clima: {', '.join(missing)}")
            
            return data
            
        except Exception as e:
            if self.debug:
                await page.screenshot(path=str(self.debug_dir / f"error_{lang}.png"))
                logger.error(f"Error obteniendo clima: {str(e)}")
            raise
        
        finally:
            await page.close()

    async def close(self):
        """Cierra todos los recursos del navegador"""
        for context in self._contexts.values():
            await context.close()
        if self._browser:
            await self._browser.close()

# Crear una función helper para uso síncrono
def get_weather_sync(city: str, lang: str = 'en', temp_unit: str = 'C', wind_unit: str = 'kmh') -> Dict[str, Any]:
    """Versión síncrona del scraper para compatibilidad"""
    import asyncio
    scraper = WeatherScraper()
    return asyncio.run(scraper.get_weather(city, lang, temp_unit, wind_unit))