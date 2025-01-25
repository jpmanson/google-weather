import re
from playwright.sync_api import Page, expect, sync_playwright
import pytest
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_get_weather_with_playwright():
    # Crear directorio para screenshots si no existe
    screenshots_dir = Path("debug_screenshots")
    screenshots_dir.mkdir(exist_ok=True)
    
    with sync_playwright() as p:
        # Launch browser with specific options
        browser = p.chromium.launch(
            headless=False,  # Cambiar a True después de debuggear
            args=['--disable-blink-features=AutomationControlled']
        )
        
        # Create context with specific options
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 720},
            locale='es-ES'  # Cambiado a español
        )
        
        page = context.new_page()

        try:
            # First visit Google homepage
            logger.info("Visiting Google homepage...")
            page.goto('https://www.google.com')
            page.screenshot(path=str(screenshots_dir / "1_homepage.png"))
            
            # Wait for and handle any consent dialogs
            try:
                consent_button = page.get_by_role("button", name=re.compile("Accept|Aceptar", re.IGNORECASE))
                if consent_button.is_visible(timeout=5000):
                    logger.info("Consent dialog found, accepting...")
                    consent_button.click()
                    page.screenshot(path=str(screenshots_dir / "2_after_consent.png"))
            except Exception as e:
                logger.info(f"No consent dialog found or error: {str(e)}")

            # Now search for weather
            logger.info("Searching for weather...")
            search_box = page.locator('textarea[name="q"]')
            search_box.fill('weather buenos aires')
            search_box.press('Enter')
            
            # Wait for navigation
            page.wait_for_load_state('networkidle')
            page.screenshot(path=str(screenshots_dir / "3_search_result.png"))
            
            # Wait for the weather widget
            logger.info("Waiting for weather widget...")
            page.wait_for_selector('div[data-wob-di]', timeout=5000)
            
            # Get location from the heading
            location_text = page.locator('text=Resultados para Buenos Aires').first
            location = location_text.text_content().replace('Resultados para ', '').strip()
            logger.info(f"Found location: {location}")
            
            # Get weather data using the correct selectors
            temperature = page.locator('span#wob_tm').first.text_content()
            condition = page.locator('span#wob_dc').first.text_content()
            
            # Get humidity and wind with Spanish labels
            humidity_text = page.locator('text=Humedad: >> span').first.text_content()
            wind_text = page.locator('text=Viento: >> span').first.text_content()
            
            # Obtener y mostrar el HTML de los elementos del clima
            print("\nHTML de los elementos del clima:")
            temp_html = page.locator('span#wob_tm').first.evaluate('el => el.outerHTML')
            condition_html = page.locator('span#wob_dc').first.evaluate('el => el.outerHTML')
            humidity_html = page.locator('text=Humedad: >> span').first.evaluate('el => el.parentElement.outerHTML')
            wind_html = page.locator('text=Viento: >> span').first.evaluate('el => el.parentElement.outerHTML')
            
            print(f"Temperatura HTML: {temp_html}")
            print(f"Condición HTML: {condition_html}")
            print(f"Humedad HTML: {humidity_html}")
            print(f"Viento HTML: {wind_html}")
            
            print(f"\nWeather data found:")
            print(f"Location: {location}")
            print(f"Temperature: {temperature}°C")
            print(f"Condition: {condition}")
            print(f"Humidity: {humidity_text}")
            print(f"Wind: {wind_text}")
            
            # Take final screenshot
            page.screenshot(path=str(screenshots_dir / "4_weather_widget.png"))
            
            # Basic assertions
            assert temperature.strip(), "Temperature should not be empty"
            assert condition.strip(), "Condition should not be empty"
            assert location.strip(), "Location should not be empty"
            assert 'buenos aires' in location.lower(), "Location should contain Buenos Aires"
            
        except Exception as e:
            logger.error(f"Error extracting weather data: {str(e)}")
            page.screenshot(path=str(screenshots_dir / "error_state.png"))
            raise
            
        finally:
            context.close()
            browser.close()

if __name__ == '__main__':
    pytest.main([__file__, "-v"])