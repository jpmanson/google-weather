import unittest
from unittest.mock import patch, Mock
from google_weather.weather import get_current_weather

class TestGetWeather(unittest.TestCase):
    @patch('google_weather.weather.requests.get')
    def test_get_weather_buenos_aires_default(self, mock_get):
        # Configurar el mock de la respuesta HTML
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''
            <div id="wob_tm">25</div>
            <div id="wob_hm">80%</div>
            <span id="wob_ws">10 km/h</span>
            <span id="wob_tws">6 mph</span>
            <div id="wob_dc">Soleado</div>
            <div class="wob_loc">Buenos Aires</div>
            <div class="vk_bk wob-unit"><span aria-disabled="true" style="display:inline">°C</span></div>
        '''
        mock_get.return_value = mock_response

        result = get_current_weather('Buenos Aires')
        
        # Verificar estructura y formato en lugar de valores específicos
        self.assertIsInstance(result, dict)
        self.assertEqual(set(result.keys()), {'temperature', 'humidity', 'wind', 'condition', 'location'})
        
        # Verificar formato de temperatura
        self.assertTrue(result['temperature'].endswith('°C'))
        self.assertTrue(float(result['temperature'].rstrip('°C')))
        
        # Verificar formato de humedad
        self.assertTrue(result['humidity'].endswith('%'))
        
        # Verificar formato de viento
        self.assertTrue(result['wind'].endswith('kmh'))
        
        # Verificar que condition y location no están vacíos
        self.assertTrue(len(result['condition']) > 0)
        self.assertTrue(len(result['location']) > 0)

    @patch('google_weather.weather.requests.get')
    def test_get_weather_custom_units(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''
            <div id="wob_tm">25</div>
            <div id="wob_hm">80%</div>
            <span id="wob_ws">10 km/h</span>
            <span id="wob_tws">6 mph</span>
            <div id="wob_dc">Soleggiato</div>
            <div class="wob_loc">Buenos Aires</div>
            <div class="vk_bk wob-unit"><span aria-disabled="true" style="display:inline">°C</span></div>
        '''
        mock_get.return_value = mock_response

        result = get_current_weather('Buenos Aires', wind_unit='mph', lang='it', temp_unit='F')
        
        # Verificar unidades personalizadas
        self.assertTrue(result['temperature'].endswith('°F'))
        self.assertTrue(float(result['temperature'].rstrip('°F')))
        self.assertTrue(result['wind'].endswith('mph'))

    @patch('google_weather.weather.requests.get')
    def test_get_weather_error_response(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        with self.assertRaises(Exception) as context:
            get_current_weather('New York', lang='en')
        
        self.assertTrue('Error getting weather: 404' in str(context.exception))

if __name__ == '__main__':
    unittest.main()