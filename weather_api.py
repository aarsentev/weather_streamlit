from datetime import datetime
import requests
import aiohttp

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

MONTH_TO_SEASON = {
    12: "winter", 1: "winter", 2: "winter",
    3: "spring", 4: "spring", 5: "spring",
    6: "summer", 7: "summer", 8: "summer",
    9: "autumn", 10: "autumn", 11: "autumn"
}


def get_current_season() -> str:
    """Получить текущий сезон."""
    return MONTH_TO_SEASON[datetime.now().month]


def check_temperature_anomaly(current_temp: float, season_mean: float, season_std: float) -> dict:
    """
    Проверить, является ли текущая температура аномальной (выход за пределы mean +- 2σ)
    """
    lower_bound = season_mean - 2 * season_std
    upper_bound = season_mean + 2 * season_std
    
    is_anomaly = current_temp < lower_bound or current_temp > upper_bound
    
    return {
        "is_anomaly": is_anomaly,
        "current_temp": current_temp,
        "season_mean": season_mean,
        "season_std": season_std,
        "lower_bound": lower_bound,
        "upper_bound": upper_bound
    }


def get_current_temperature(city: str, api_key: str) -> dict:
    """Получить текущую температуру (синхронно)."""
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    
    if response.status_code != 200:
        return {"city": city, "error": data.get("message", "Unknown error")}
    
    return {
        "city": city,
        "temperature": data["main"]["temp"],
        "description": data["weather"][0]["description"]
    }


async def get_current_temperature_async(
        session: aiohttp.ClientSession,
        city: str,
        api_key: str
    ) -> dict:
    """Получить текущую температуру (асинхронно)."""
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }
    async with session.get(BASE_URL, params=params, ssl=False) as response:
        data = await response.json()
        
        if response.status != 200:
            return {"city": city, "error": data.get("message", "Unknown error")}
        
        return {
            "city": city,
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"]
        }