# core/weather.py
import aiohttp
from datetime import datetime

CITIES = [
    ("Алексин", 54.5000, 38.6833),
    ("Белёв", 53.7833, 36.3000),
    ("Венёв", 54.3667, 38.2833),
    ("Ефремов", 53.1500, 38.1333),
    ("Новомосковск", 54.0000, 38.3167),
    ("Чернь", 53.9000, 36.9167),
    ("Тула", 54.1931, 37.6173),
]

WEATHER_CODES = {
    0: "ясно", 1: "незначительная облачность", 2: "переменная облачность", 3: "облачно",
    45: "туман", 48: "туман с изморозью", 51: "слабый моросящий дождь", 53: "морось",
    55: "сильная морось", 56: "слабый ледяной дождь", 57: "сильный ледяной дождь",
    61: "слабый дождь", 63: "дождь", 65: "сильный дождь", 66: "слабый ледяной дождь",
    67: "сильный ледяной дождь", 71: "слабый снег", 73: "снег", 75: "сильный снег",
    77: "снежные крупки", 80: "слабый ливень", 81: "ливень", 82: "сильный ливень",
    85: "слабая снегопад", 86: "сильная снегопад", 95: "гроза", 96: "гроза с градом",
    99: "гроза с градом",
}

async def get_weather_response(mode: str) -> str:
    lats = ",".join(str(lat) for _, lat, _ in CITIES)
    lons = ",".join(str(lon) for _, _, lon in CITIES)

    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lats}&longitude={lons}"
        f"&daily=weathercode,temperature_2m_max,temperature_2m_min"
        f"&timezone=Europe/Moscow"
        f"&forecast_days=16"
    )

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()

    all_forecasts = data if isinstance(data, list) else [data]
    today = datetime.now().date()
    blocks = []

    def format_date_label(date_str: str) -> str:
        d = datetime.fromisoformat(date_str).date()
        day_month = d.strftime("%d %B").lstrip("0")
        ru_months = {
            "January": "января", "February": "февраля", "March": "марта", "April": "апреля",
            "May": "мая", "June": "июня", "July": "июля", "August": "августа",
            "September": "сентября", "October": "октября", "November": "ноября", "December": "декабря"
        }
        for en, ru in ru_months.items():
            day_month = day_month.replace(en, ru)
        return f"**{day_month}**"

    day_offsets = [1] if mode == "tomorrow" else [1, 2, 3, 4, 5]

    for day_offset in day_offsets:
        day_data = []
        valid = False
        for i, (city_name, _, _) in enumerate(CITIES):
            forecast = all_forecasts[i]["daily"]
            times = forecast["time"]
            if len(times) <= day_offset:
                continue
            date_str = times[day_offset]
            temp_max = forecast["temperature_2m_max"][day_offset]
            temp_min = forecast["temperature_2m_min"][day_offset]
            code = forecast["weathercode"][day_offset]
            cond = WEATHER_CODES.get(code, "погода неизвестна")

            city_lines = [
                f"{city_name}:",
                f"днём {int(temp_max)}° — {cond}",
                f"вечером {int((temp_max + temp_min) / 2)}° — {cond}"
            ]
            day_data.append("\n".join(city_lines))
            valid = True

        if valid:
            date_label = format_date_label(times[day_offset])
            day_block = [date_label]
            day_block.extend(day_data)
            blocks.append("\n\n".join(day_block))

    if not blocks:
        raise Exception("Нет данных о погоде")

    return "\n\n".join(blocks)