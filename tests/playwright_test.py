import asyncio
from playwright.async_api import async_playwright
import logging
from pathlib import Path
import re
from google_weather.lang import lang_queries  # Importamos lang_queries

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Definir casos de prueba
test_cases = [
    ('es', 'C', 'Soleado', 'Humedad:', 'Viento:'),
    ('en', 'F', 'Sunny', 'Humidity:', 'Wind:'),
    ('fr', 'C', 'Ensoleillé', 'Humidité:', 'Vent:'),
    ('de', 'C', 'Sonnig', 'Luftfeuchtigkeit:', 'Wind:')
]

async def get_temperature(page) -> float:
    try:
        temp_element = page.locator("#wob_tm")
        temp_raw = await temp_element.inner_text()
        logger.info(f"Temperatura encontrada (raw): {temp_raw}")
        
        temp_value = float(temp_raw)
        logger.info(f"Temperatura procesada: {temp_value}°C")
        return temp_value
    except Exception as e:
        logger.error(f"Error procesando temperatura: {str(e)}")
        raise ValueError(f"La temperatura debe ser un número válido: {temp_raw}")

async def get_location(page) -> str:
    try:
        # Buscar el elemento de ubicación por su estructura en lugar de texto específico
        location_element = await page.wait_for_selector(".BBwThe", timeout=5000)
        
        if location_element:
            full_text = await location_element.text_content()
            logger.info(f"Texto completo encontrado: {full_text}")
            
            # Eliminar textos de prefijo comunes en diferentes idiomas
            prefixes = ['Resultados para ', 'Results for ', 'Résultats pour ', 'Ergebnisse für ']
            for prefix in prefixes:
                if full_text.startswith(prefix):
                    full_text = full_text.replace(prefix, '').strip()
            
            # Devolver la ubicación completa
            location = full_text.strip()
            logger.info(f"Ubicación final: {location}")
            return location
            
    except Exception as e:
        logger.error(f"Error buscando ubicación: {str(e)}")
        raise ValueError("No se pudo encontrar la ubicación")

async def test_weather(language, unit, city, humidity_label, wind_label):
    # Crear directorio para screenshots si no existe
    screenshots_dir = Path("debug_screenshots")
    screenshots_dir.mkdir(exist_ok=True)
    
    # Mapeo de idiomas a configuraciones
    language_configs = {
        'es': {'locale': 'es-ES'},
        'en': {'locale': 'en-US'},
        'fr': {'locale': 'fr-FR'},
        'de': {'locale': 'de-DE'}
    }
    
    # Obtener configuración del idioma seleccionado
    lang_config = language_configs.get(language, language_configs['en'])
    
    # Usar lang_queries para construir el término de búsqueda
    search_term = lang_queries[language].format(city=city.replace(' ', '+'))
    logger.info(f"Search term for {language}: {search_term}")
    
    async with async_playwright() as p:
        # Configurar el navegador para que parezca más humano
        browser = await p.chromium.launch(
            headless=False,  # Mostrar el navegador
            args=[
                '--disable-blink-features=AutomationControlled',
                '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
        )
        
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale=language,
            timezone_id='America/Argentina/Buenos_Aires',
        )
        
        page = await context.new_page()
        
        logger.info("Visiting Google homepage...")
        await page.goto(f"https://www.google.com?hl={language}", wait_until="networkidle")
        
        # Esperar un poco antes de buscar
        await page.wait_for_timeout(2000)
        
        logger.info(f"Searching for weather in {language}...")
        search_input = await page.wait_for_selector("[name='q']")
        await search_input.click()
        await search_input.fill(search_term)  # Usar el nuevo search_term
        await page.wait_for_timeout(1000)
        await search_input.press("Enter")
        
        # Esperar a que la página se cargue completamente
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(2000)  # Esperar un poco más
        
        search_url = page.url
        search_content = await page.content()
        logger.info(f"Search URL: {search_url}")
        logger.info(f"Search results HTML:\n{search_content[:1000]}...")
        
        logger.info("Waiting for weather widget...")
        try:
            weather_widget = await page.wait_for_selector("#wob_wc", timeout=30000)
            logger.info("Weather widget found!")
            
            # Tomar screenshot cuando encontramos el widget
            await page.screenshot(path=f'success-{language}.png')
            
            # Debug: Mostrar todo el HTML del widget del clima
            logger.info("Obteniendo HTML del widget completo...")
            weather_widget_html = await weather_widget.inner_html()
            logger.debug(f"Weather widget HTML completo:\n{weather_widget_html}")
            
            # Debug: Mostrar elementos individuales
            logger.info("Buscando elementos individuales del clima...")
            
            elements = {
                "temperatura": "#wob_tm",
                "condición": "#wob_dc",
                "ubicación": "#wob_loc",
                "precipitación": "#wob_pp",
                "humedad": "#wob_hm",
                "viento": "#wob_ws"
            }
            
            for name, selector in elements.items():
                element = page.locator(selector)
                html = await element.inner_html()
                text = await element.inner_text()
                logger.debug(f"{name.capitalize()} HTML: {html}")
                logger.debug(f"{name.capitalize()} texto: {text}")

            city = await get_location(page)

            # Get weather data using the correct selectors
            logger.info("Obteniendo datos del clima...")
            
            # Mapeo de etiquetas según idioma
            weather_labels = {
                'es': {'humidity': 'Humedad:', 'wind': 'Viento:'},
                'en': {'humidity': 'Humidity:', 'wind': 'Wind:'},
                'fr': {'humidity': 'Humidité:', 'wind': 'Vent:'},
                'de': {'humidity': 'Luftfeuchtigkeit:', 'wind': 'Wind:'}
            }
            
            current_labels = weather_labels.get(language, weather_labels['en'])
            
            try:
                # Temperatura
                logger.info("Obteniendo temperatura...")
                temp = await get_temperature(page)
                
                # Condición climática
                condition_element = page.locator("#wob_dc")
                condition_html = await condition_element.inner_html()
                logger.debug(f"Condición HTML: {condition_html}")
                current_condition = await condition_element.inner_text()
                logger.info(f"Condición encontrada: {current_condition}")
                
                # Obtener humedad
                humidity_element = page.locator("#wob_hm")
                humidity_html = await humidity_element.inner_html()
                logger.debug(f"Humedad HTML: {humidity_html}")
                
                humidity = await humidity_element.inner_text()
                logger.info(f"Humedad encontrada: {humidity}")
                
                # Obtener viento
                try:
                    wind_element = page.locator("#wob_ws")
                    wind_html = await wind_element.inner_html()
                    logger.debug(f"Viento HTML: {wind_html}")
                    wind = await wind_element.inner_text()
                    
                    # Convertir viento a mph para inglés
                    if language == 'en':
                        # Extraer el número y convertir
                        wind_speed = float(wind.split()[0])  # Obtiene el número
                        wind_speed_mph = round(wind_speed * 0.621371, 1)  # Convierte km/h a mph
                        wind = f"{wind_speed_mph} mph"
                        logger.info(f"Viento convertido a mph: {wind}")
                    
                    logger.info(f"Viento encontrado: {wind}")
                except Exception as e:
                    logger.error(f"Error obteniendo viento: {e}")
                    wind = "N/A"
                
                # Log the raw data
                logger.info("\nHTML de los elementos del clima:")
                logger.info(f"Temperatura HTML: {temp}")
                logger.info(f"Condición HTML: {condition_html}")
                logger.info(f"Humedad HTML: {humidity_html}")
                logger.info(f"Viento HTML: {wind_html}")
                
                # Log the processed data
                logger.info("\nWeather data found:")
                logger.info(f"Location: {city}")
                logger.info(f"Temperature: {temp}")
                logger.info(f"Condition: {current_condition}")
                logger.info(f"Humidity: {humidity}")
                logger.info(f"Wind: {wind}")
                
                # Convertir temperatura si es necesario
                if unit == 'F':
                    temp = (temp * 9/5) + 32
                    logger.info(f"Temperatura convertida a Fahrenheit: {temp}°F")

                # Mostrar resultados individuales con la temperatura ya convertida
                print(f"""
                    Resultados para {language.upper()} ({unit}):
                    Ubicación: {city}
                    Temperatura: {temp}
                    Condición: {current_condition}
                    Humedad: {humidity}
                    Viento: {wind}
                """)

                return {
                    "language": language,
                    "location": city,
                    "temperature": temp,  # Ya está convertida si era necesario
                    "condition": current_condition,
                    "humidity": humidity,
                    "wind": wind,
                    "unit": unit
                }

            except Exception as e:
                logger.error(f"Error obteniendo datos del clima: {str(e)}")
                await page.screenshot(path=str(screenshots_dir / "error_getting_weather.png"))
                raise

            # Take final screenshot
            await page.screenshot(path=str(screenshots_dir / "4_weather_widget.png"))
            
            # Basic assertions
            assert temp.strip(), "Temperature should not be empty"
            assert current_condition.strip(), "Condition should not be empty"
            assert city.strip(), "Location should not be empty"
            assert 'buenos aires' in city.lower(), "Location should contain Buenos Aires"
            
        except Exception as e:
            logger.error(f"Error extracting weather data: {str(e)}")
            await page.screenshot(path=str(screenshots_dir / "error_state.png"))
            raise
            
        finally:
            await context.close()
            await browser.close()

async def main():
    # Casos de prueba con diferentes ciudades
    test_cases = [
        ("es", "C", "Madrid", "Humedad:", "Viento:"),
        ("en", "F", "Tokyo", "Humidity:", "Wind:"),
        ("fr", "C", "Paris", "Humidité:", "Vent:"),
        ("de", "C", "Berlin", "Luftfeuchtigkeit:", "Wind:"),
    ]
    
    results = []
    for language, unit, city, humidity_label, wind_label in test_cases:
        print(f"\n{'='*80}")
        print(f"Ejecutando prueba para idioma: {language} - Ciudad: {city}")
        print(f"{'='*80}")
        try:
            result = await test_weather(language, unit, city, humidity_label, wind_label)
            results.append(result)
        except Exception as e:
            print(f"Error en prueba {language} - {city}: {str(e)}")
    
    # Print summary of all results
    if results:
        print("\nResumen de resultados:")
        for result in results:
            unit_symbol = '°F' if result.get('unit') == 'F' else '°C'
            print(f"\nIdioma: {result['language'].upper()}")
            print(f"Ubicación: {result['location']}")
            print(f"Temperatura: {result['temperature']}{unit_symbol}")
            print(f"Condición: {result['condition']}")
            print(f"Humedad: {result['humidity']}")
            print(f"Viento: {result['wind']}")

    # Print any failed languages
    failed_languages = [lang for lang, _, _, _, _ in test_cases if not any(r['language'] == lang for r in results)]
    if failed_languages:
        print("\nPruebas fallidas para los siguientes idiomas:")
        for lang in failed_languages:
            print(f"- {lang.upper()}")

if __name__ == "__main__":
    asyncio.run(main())


"""
Output:
(.venv) D:\Development\google-weather git:[main]
python tests/playwright_test.py

================================================================================
Ejecutando prueba para idioma: es - Ciudad: Madrid
================================================================================
INFO:__main__:Search term for es: clima+en+Madrid
INFO:__main__:Visiting Google homepage...
INFO:__main__:Searching for weather in es...
INFO:__main__:Search URL: https://www.google.com/search?q=clima%2Ben%2BMadrid&sca_esv=e7c48c294f52a5cb&hl=es&source=hp&ei=tnGVZ8jJHZPL1sQP7tza2Ao&iflsig=ACkRmUkAAAAAZ5V_xpbIY3I4KbkF-jV7x98G1PJRLRe9&ved=0ahUKEwjI_PqygZKLAxWTpZUCHW6uFqsQ4dUDCA4&uact=5&oq=clima%2Ben%2BMadrid&gs_lp=Egdnd3Mtd2l6Ig9jbGltYStlbitNYWRyaWQyBBAAGB4yBBAAGB4yBBAAGB4yBBAAGB4yBBAAGB4yBBAAGB4yBBAAGB4yBBAAGB4yBBAAGB4yBBAAGB5IvghQNFg0cAF4AJABAJgBVaABVaoBATG4AQPIAQD4AQGYAgKgAmOoAgrCAgoQABgDGOoCGI8BwgIKEC4YAxjqAhiPAZgDCPEFWP10QwNGbPmSBwEyoAfUBQ&sclient=gws-wiz&sei=vHGVZ-e-Hp7T1sQPrurIgQk
INFO:__main__:Search results HTML:
<!DOCTYPE html><html itemscope="" itemtype="http://schema.org/SearchResultsPage" lang="es-AR"><head><meta charset="UTF-8"><meta content="origin" name="referrer"><meta content="/images/branding/googleg/1x/googleg_standard_color_128dp.png" itemprop="image"><title>clima+en+Madrid - Buscar con Google</title><script nonce="">window._hst=Date.now();</script><script nonce="">(function(){var b=window.addEventListener;window.addEventListener=function(a,c,d){a!=="unload"&&b(a,c,d)};}).call(this);(function(){var _g={kEI:'vHGVZ4v5K7Hb1sQ
PqrnNwAc',kEXPI:'31',kBL:'HhQf',kOPI:89978449};(function(){var a;((a=window.google)==null?0:a.stvsc)?google.kEI=_g.kEI:window.google=_g;}).call(this);})();(function(){google.sn='web';google.kHL='es-AR';})();(function(){
var g=this||self;function k(){return window.google&&window.google.kOPI||null};var l,m=[];function n(a){for(var b;a&&(!a.getAttribute||!(b=a.getAttribute("eid")));)a=a.parentNode;return b||l}function p(a){for(var b=null;a&&(!a.getAttribute||!(b=a.get...
INFO:__main__:Waiting for weather widget...
INFO:__main__:Weather widget found!
INFO:__main__:Obteniendo HTML del widget completo...
INFO:__main__:Buscando elementos individuales del clima...
INFO:__main__:Texto completo encontrado: Madrid, España
INFO:__main__:Ubicación final: Madrid, España
INFO:__main__:Obteniendo datos del clima...
INFO:__main__:Obteniendo temperatura...
INFO:__main__:Temperatura encontrada (raw): 8
INFO:__main__:Temperatura procesada: 8.0°C
INFO:__main__:Condición encontrada: Despejado con intervalos nubosos
INFO:__main__:Humedad encontrada: 87%
INFO:__main__:Viento encontrado: 10 km/h
INFO:__main__:
HTML de los elementos del clima:
INFO:__main__:Temperatura HTML: 8.0
INFO:__main__:Condición HTML: Despejado con intervalos nubosos
INFO:__main__:Humedad HTML: 87%
INFO:__main__:Viento HTML: 10 km/h
INFO:__main__:
Weather data found:
INFO:__main__:Location: Madrid, España
INFO:__main__:Temperature: 8.0
INFO:__main__:Condition: Despejado con intervalos nubosos
INFO:__main__:Humidity: 87%
INFO:__main__:Wind: 10 km/h

                    Resultados para ES (C):
                    Ubicación: Madrid, España
                    Temperatura: 8.0
                    Condición: Despejado con intervalos nubosos
                    Humedad: 87%
                    Viento: 10 km/h


================================================================================
Ejecutando prueba para idioma: en - Ciudad: Tokyo
================================================================================
INFO:__main__:Search term for en: weather+in+Tokyo
INFO:__main__:Visiting Google homepage...
INFO:__main__:Searching for weather in en...
INFO:__main__:Search URL: https://www.google.com/search?q=weather%2Bin%2BTokyo&sca_esv=e7c48c294f52a5cb&hl=en&source=hp&ei=x3GVZ8iWC4zd1sQP1eCamQg&iflsig=ACkRmUkAAAAAZ5V_13ATTKR
LrZrPE1OCtBl0x6LPKVdy&ved=0ahUKEwiIlva6gZKLAxWMrpUCHVWwJoMQ4dUDCA4&uact=5&oq=weather%2Bin%2BTokyo&gs_lp=Egdnd3Mtd2l6IhB3ZWF0aGVyK2luK1Rva3lvMgQQABgeMgQQABgeMgQQABgeMgQQABgeMgQQABgeMgQQABgeMgQQABgeMgQQABgeMgQQABgeMgQQABgeSK0IUBdYF3ABeACQAQCYAVSgAVSqAQExuAEDyAEA-AEBmAIBoAJbqAIAmAMB8QVIhVsosBQrHJIHATGgB8kF&sclient=gws-wiz&sei=zHGVZ9-DAu7e1sQP4tmg6Qk      
INFO:__main__:Search results HTML:
<!DOCTYPE html><html itemscope="" itemtype="http://schema.org/SearchResultsPage" lang="en-AR"><head><meta charset="UTF-8"><meta content="origin" name="referrer"><meta content="/
images/branding/googleg/1x/googleg_standard_color_128dp.png" itemprop="image"><title>weather+in+Tokyo - Google Search</title><script nonce="">window._hst=Date.now();</script><sc
ript nonce="">(function(){var b=window.addEventListener;window.addEventListener=function(a,c,d){a!=="unload"&&b(a,c,d)};}).call(this);(function(){var _g={kEI:'zHGVZ8CBENjX1sQPsf
GguAg',kEXPI:'31',kBL:'HhQf',kOPI:89978449};(function(){var a;((a=window.google)==null?0:a.stvsc)?google.kEI=_g.kEI:window.google=_g;}).call(this);})();(function(){google.sn='web';google.kHL='en-AR';})();(function(){
var g=this||self;function k(){return window.google&&window.google.kOPI||null};var l,m=[];function n(a){for(var b;a&&(!a.getAttribute||!(b=a.getAttribute("eid")));)a=a.parentNode;return b||l}function p(a){for(var b=null;a&&(!a.getAttribute||!(b=a.getAtt...
INFO:__main__:Waiting for weather widget...
INFO:__main__:Weather widget found!
INFO:__main__:Obteniendo HTML del widget completo...
INFO:__main__:Buscando elementos individuales del clima...
INFO:__main__:Texto completo encontrado: Tokyo, Japan
INFO:__main__:Ubicación final: Tokyo, Japan
INFO:__main__:Obteniendo datos del clima...
INFO:__main__:Obteniendo temperatura...
INFO:__main__:Temperatura encontrada (raw): 6
INFO:__main__:Temperatura procesada: 6.0°C
INFO:__main__:Condición encontrada: Clear
INFO:__main__:Humedad encontrada: 49%
INFO:__main__:Viento convertido a mph: 8.1 mph
INFO:__main__:Viento encontrado: 8.1 mph
INFO:__main__:
HTML de los elementos del clima:
INFO:__main__:Temperatura HTML: 6.0
INFO:__main__:Condición HTML: Clear
INFO:__main__:Humedad HTML: 49%
INFO:__main__:Viento HTML: 13 km/h
INFO:__main__:
Weather data found:
INFO:__main__:Location: Tokyo, Japan
INFO:__main__:Temperature: 6.0
INFO:__main__:Condition: Clear
INFO:__main__:Humidity: 49%
INFO:__main__:Wind: 8.1 mph
INFO:__main__:Temperatura convertida a Fahrenheit: 42.8°F

                    Resultados para EN (F):
                    Ubicación: Tokyo, Japan
                    Temperatura: 42.8
                    Condición: Clear
                    Humedad: 49%
                    Viento: 8.1 mph


================================================================================
Ejecutando prueba para idioma: fr - Ciudad: Paris
================================================================================
INFO:__main__:Search term for fr: météo+à+Paris
INFO:__main__:Visiting Google homepage...
INFO:__main__:Searching for weather in fr...
INFO:__main__:Search URL: https://www.google.com/search?q=m%C3%A9t%C3%A9o%2B%C3%A0%2BParis&sca_esv=e7c48c294f52a5cb&hl=fr&source=hp&ei=1nGVZ8mJNorW1sQPnLG22Ao&iflsig=ACkRmUkAAAA
AZ5V_5h-TK-DdeXIy5XC6iKu3IBMkD9Mt&ved=0ahUKEwjJzLTCgZKLAxUKq5UCHZyYDasQ4dUDCA4&uact=5&oq=m%C3%A9t%C3%A9o%2B%C3%A0%2BParis&gs_lp=Egdnd3Mtd2l6IhBtw6l0w6lvK8OgK1BhcmlzMgQQABgeMgQQA
BgeMgQQABgeMgQQABgeMgQQABgeMgQQABgeMgQQABgeMgQQABgeMgQQABgeMgQQABgeSKMIUBRYFHABeACQAQCYAUqgAUqqAQExuAEDyAEA-AEBmAIBoAJUqAIAmAMB8QXSWjE7QVCHQJIHATGgB_sF&sclient=gws-wiz&sei=23GVZ_m1MP3S1sQPmLrWwAw
INFO:__main__:Search results HTML:
<!DOCTYPE html><html itemscope="" itemtype="http://schema.org/SearchResultsPage" lang="fr-AR"><head><meta charset="UTF-8"><meta content="origin" name="referrer"><meta content="/
images/branding/googleg/1x/googleg_standard_color_128dp.png" itemprop="image"><title>météo+à+Paris - Recherche Google</title><script nonce="">window._hst=Date.now();</script><sc
ript nonce="">(function(){var b=window.addEventListener;window.addEventListener=function(a,c,d){a!=="unload"&&b(a,c,d)};}).call(this);(function(){var _g={kEI:'3HGVZ6SeAfLQ1sQPuK
_10Ak',kEXPI:'31',kBL:'HhQf',kOPI:89978449};(function(){var a;((a=window.google)==null?0:a.stvsc)?google.kEI=_g.kEI:window.google=_g;}).call(this);})();(function(){google.sn='web';google.kHL='fr-AR';})();(function(){
var g=this||self;function k(){return window.google&&window.google.kOPI||null};var l,m=[];function n(a){for(var b;a&&(!a.getAttribute||!(b=a.getAttribute("eid")));)a=a.parentNode;return b||l}function p(a){for(var b=null;a&&(!a.getAttribute||!(b=a.getAtt...
INFO:__main__:Waiting for weather widget...
INFO:__main__:Weather widget found!
INFO:__main__:Obteniendo HTML del widget completo...
INFO:__main__:Buscando elementos individuales del clima...
INFO:__main__:Texto completo encontrado: Paris, France
INFO:__main__:Ubicación final: Paris, France
INFO:__main__:Obteniendo datos del clima...
INFO:__main__:Obteniendo temperatura...
INFO:__main__:Temperatura encontrada (raw): 5
INFO:__main__:Temperatura procesada: 5.0°C
INFO:__main__:Condición encontrada: Nuageux
INFO:__main__:Humedad encontrada: 93%
INFO:__main__:Viento encontrado: 19 km/h
INFO:__main__:
HTML de los elementos del clima:
INFO:__main__:Temperatura HTML: 5.0
INFO:__main__:Condición HTML: Nuageux
INFO:__main__:Humedad HTML: 93%
INFO:__main__:Viento HTML: 19 km/h
INFO:__main__:
Weather data found:
INFO:__main__:Location: Paris, France
INFO:__main__:Temperature: 5.0
INFO:__main__:Condition: Nuageux
INFO:__main__:Humidity: 93%
INFO:__main__:Wind: 19 km/h

                    Resultados para FR (C):
                    Ubicación: Paris, France
                    Temperatura: 5.0
                    Condición: Nuageux
                    Humedad: 93%
                    Viento: 19 km/h


================================================================================
Ejecutando prueba para idioma: de - Ciudad: Berlin
================================================================================
INFO:__main__:Search term for de: wetter+in+Berlin
INFO:__main__:Visiting Google homepage...
INFO:__main__:Searching for weather in de...
INFO:__main__:Search URL: https://www.google.com/search?q=wetter%2Bin%2BBerlin&sca_esv=e7c48c294f52a5cb&hl=de&source=hp&ei=5nGVZ-miFdbK1sQPiLDG4A4&iflsig=ACkRmUkAAAAAZ5V_9kntZpv
EMsEOUqanvsdKpVdL-mvR&ved=0ahUKEwjpreTJgZKLAxVWpZUCHQiYEewQ4dUDCA4&uact=5&oq=wetter%2Bin%2BBerlin&gs_lp=Egdnd3Mtd2l6IhB3ZXR0ZXIraW4rQmVybGluMgQQABgeMgQQABgeMgQQABgeMgQQABgeMgQQABgeMgQQABgeMgQQABgeMgQQABgeMgQQABgeMgQQABgeSLcIUCNYI3ABeACQAQCYAVegAVeqAQExuAEDyAEA-AEBmAIBoAJfqAIAmAMC8QVGH9v83oG8KJIHATGgB8QF&sclient=gws-wiz&sei=7HGVZ9G3A-SP4dUPw5iX0QU      
INFO:__main__:Search results HTML:
<!DOCTYPE html><html itemscope="" itemtype="http://schema.org/SearchResultsPage" lang="de-AR"><head><meta charset="UTF-8"><meta content="origin" name="referrer"><meta content="/
images/branding/googleg/1x/googleg_standard_color_128dp.png" itemprop="image"><title>wetter+in+Berlin - Google Suche</title><script nonce="">window._hst=Date.now();</script><scr
ipt nonce="">(function(){var b=window.addEventListener;window.addEventListener=function(a,c,d){a!=="unload"&&b(a,c,d)};}).call(this);(function(){var _g={kEI:'7HGVZ8WVErve1sQPpJL
8CA',kEXPI:'31',kBL:'HhQf',kOPI:89978449};(function(){var a;((a=window.google)==null?0:a.stvsc)?google.kEI=_g.kEI:window.google=_g;}).call(this);})();(function(){google.sn='web';google.kHL='de-AR';})();(function(){
var g=this||self;function k(){return window.google&&window.google.kOPI||null};var l,m=[];function n(a){for(var b;a&&(!a.getAttribute||!(b=a.getAttribute("eid")));)a=a.parentNode;return b||l}function p(a){for(var b=null;a&&(!a.getAttribute||!(b=a.getAttri...
INFO:__main__:Waiting for weather widget...
INFO:__main__:Weather widget found!
INFO:__main__:Obteniendo HTML del widget completo...
INFO:__main__:Buscando elementos individuales del clima...
INFO:__main__:Texto completo encontrado: Berlin, Deutschland
INFO:__main__:Ubicación final: Berlin, Deutschland
INFO:__main__:Obteniendo datos del clima...
INFO:__main__:Obteniendo temperatura...
INFO:__main__:Temperatura encontrada (raw): 8
INFO:__main__:Temperatura procesada: 8.0°C
INFO:__main__:Condición encontrada: Stark bewölkt
INFO:__main__:Humedad encontrada: 82%
INFO:__main__:Viento encontrado: 5 km/h
INFO:__main__:
HTML de los elementos del clima:
INFO:__main__:Temperatura HTML: 8.0
INFO:__main__:Condición HTML: Stark bewölkt
INFO:__main__:Humedad HTML: 82%
INFO:__main__:Viento HTML: 5 km/h
INFO:__main__:
Weather data found:
INFO:__main__:Location: Berlin, Deutschland
INFO:__main__:Temperature: 8.0
INFO:__main__:Condition: Stark bewölkt
INFO:__main__:Humidity: 82%
INFO:__main__:Wind: 5 km/h

                    Resultados para DE (C):
                    Ubicación: Berlin, Deutschland
                    Temperatura: 8.0
                    Condición: Stark bewölkt
                    Humedad: 82%
                    Viento: 5 km/h


Resumen de resultados:

Idioma: ES
Ubicación: Madrid, España
Temperatura: 8.0°C
Condición: Despejado con intervalos nubosos
Humedad: 87%
Viento: 10 km/h

Idioma: EN
Ubicación: Tokyo, Japan
Temperatura: 42.8°F
Condición: Clear
Humedad: 49%
Viento: 8.1 mph

Idioma: FR
Ubicación: Paris, France
Temperatura: 5.0°C
Condición: Nuageux
Humedad: 93%
Viento: 19 km/h

Idioma: DE
Ubicación: Berlin, Deutschland
Temperatura: 8.0°C
Condición: Stark bewölkt
Humedad: 82%
Viento: 5 km/h
"""