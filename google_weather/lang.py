lang_queries = {
    'es': 'clima+en+{city}',
    'en': 'weather+in+{city}',
    'zh': '{city}+天气',
    'hi': '{city}+में+मौसम',
    'ar': 'الطقس+في+{city}',
    'bn': '{city}+আবহাওয়া',
    'pt': 'tempo+em+{city}',
    'ru': 'погода+в+{city}',
    'ja': '{city}+の天気',
    'fr': 'météo+à+{city}',
    'de': 'wetter+in+{city}',
    'ko': '{city}+날씨',
    'tr': '{city}+hava+durumu',
    'it': 'meteo+a+{city}',
    'pl': 'pogoda+w+{city}',
    'uk': 'погода+у+{city}',
    'nl': 'weer+in+{city}',
    'vi': 'thời+tiết+tại+{city}',
    'fa': 'آب+و+هوا+در+{city}',
    'th': 'สภาพอากาศ+ใน+{city}',
    'id': 'cuaca+di+{city}',
    'cs': 'počasí+v+{city}',
    'ro': 'vremea+în+{city}',
    'el': 'καιρός+στην+{city}',
    'hu': 'időjárás+{city}',
    'sv': 'väder+i+{city}',
    'da': 'vejr+i+{city}',
    'fi': 'sää+{city}',
    'no': 'vær+i+{city}',
    'he': 'מזג+אוויר+ב{city}'
}

# Mapeo de etiquetas según idioma
weather_labels = {
    'es': {'humidity': 'Humedad:', 'wind': 'Viento:', 'condition': 'Condición:'},
    'en': {'humidity': 'Humidity:', 'wind': 'Wind:', 'condition': 'Condition:'},
    'fr': {'humidity': 'Humidité:', 'wind': 'Vent:', 'condition': 'Condition:'},
    'de': {'humidity': 'Luftfeuchtigkeit:', 'wind': 'Wind:', 'condition': 'Wetterlage:'},
    'it': {'humidity': 'Umidità:', 'wind': 'Vento:', 'condition': 'Condizione:'},
    'pt': {'humidity': 'Umidade:', 'wind': 'Vento:', 'condition': 'Condição:'},
    'ru': {'humidity': 'Влажность:', 'wind': 'Ветер:', 'condition': 'Погода:'},
    'zh': {'humidity': '湿度:', 'wind': '风速:', 'condition': '天气:'},
    'ja': {'humidity': '湿度:', 'wind': '風速:', 'condition': '天気:'},
    'ko': {'humidity': '습도:', 'wind': '바람:', 'condition': '날씨:'}
}

# Mapeo de configuraciones regionales
locale_configs = {
    'es': {'locale': 'es-ES', 'timezone': 'Europe/Madrid'},
    'en': {'locale': 'en-US', 'timezone': 'America/New_York'},
    'fr': {'locale': 'fr-FR', 'timezone': 'Europe/Paris'},
    'de': {'locale': 'de-DE', 'timezone': 'Europe/Berlin'},
    'it': {'locale': 'it-IT', 'timezone': 'Europe/Rome'},
    'pt': {'locale': 'pt-PT', 'timezone': 'Europe/Lisbon'},
    'ru': {'locale': 'ru-RU', 'timezone': 'Europe/Moscow'},
    'zh': {'locale': 'zh-CN', 'timezone': 'Asia/Shanghai'},
    'ja': {'locale': 'ja-JP', 'timezone': 'Asia/Tokyo'},
    'ko': {'locale': 'ko-KR', 'timezone': 'Asia/Seoul'},
    'ar': {'locale': 'ar-SA', 'timezone': 'Asia/Riyadh'},
    'hi': {'locale': 'hi-IN', 'timezone': 'Asia/Kolkata'},
    'tr': {'locale': 'tr-TR', 'timezone': 'Europe/Istanbul'},
    'pl': {'locale': 'pl-PL', 'timezone': 'Europe/Warsaw'},
    'nl': {'locale': 'nl-NL', 'timezone': 'Europe/Amsterdam'},
    'cs': {'locale': 'cs-CZ', 'timezone': 'Europe/Prague'},
    'sv': {'locale': 'sv-SE', 'timezone': 'Europe/Stockholm'},
    'da': {'locale': 'da-DK', 'timezone': 'Europe/Copenhagen'},
    'fi': {'locale': 'fi-FI', 'timezone': 'Europe/Helsinki'},
    'no': {'locale': 'nb-NO', 'timezone': 'Europe/Oslo'}
}

# Mapeo de condiciones climáticas comunes
weather_conditions = {
    'en': {
        'sunny': 'Sunny',
        'clear': 'Clear',
        'partly_cloudy': 'Partly cloudy',
        'cloudy': 'Cloudy',
        'rain': 'Rain',
        'snow': 'Snow',
        'thunderstorm': 'Thunderstorm'
    },
    'es': {
        'sunny': 'Soleado',
        'clear': 'Despejado',
        'partly_cloudy': 'Parcialmente nublado',
        'cloudy': 'Nublado',
        'rain': 'Lluvia',
        'snow': 'Nieve',
        'thunderstorm': 'Tormenta'
    },
    'fr': {
        'sunny': 'Ensoleillé',
        'clear': 'Dégagé',
        'partly_cloudy': 'Partiellement nuageux',
        'cloudy': 'Nuageux',
        'rain': 'Pluie',
        'snow': 'Neige',
        'thunderstorm': 'Orage'
    },
    'de': {
        'sunny': 'Sonnig',
        'clear': 'Klar',
        'partly_cloudy': 'Teilweise bewölkt',
        'cloudy': 'Bewölkt',
        'rain': 'Regen',
        'snow': 'Schnee',
        'thunderstorm': 'Gewitter'
    }
}

# Mapeo de unidades por región
unit_preferences = {
    'en-US': {'temp': 'F', 'wind': 'mph'},
    'en-GB': {'temp': 'C', 'wind': 'mph'},
    'default': {'temp': 'C', 'wind': 'kmh'}
}

# Ejemplo de uso:
city = "Buenos Aires"
query = lang_queries['es'].format(city=city.replace(' ', '+'))
# Resultado: "clima+en+Buenos+Aires"