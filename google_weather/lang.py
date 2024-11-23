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

# Ejemplo de uso:
city = "Buenos Aires"
query = lang_queries['es'].format(city=city.replace(' ', '+'))
# Resultado: "clima+en+Buenos+Aires"