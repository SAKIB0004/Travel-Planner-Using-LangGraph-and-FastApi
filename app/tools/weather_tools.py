from __future__ import annotations

from typing import Any

import httpx

from app.config.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

MOCK_WEATHER = {
    "japan": {
        "spring": {"summary": "Mild temperatures with some rain and cherry blossom crowds.", "packing": ["light jacket", "umbrella", "comfortable walking shoes"]},
        "summer": {"summary": "Warm to hot, humid, and occasionally rainy.", "packing": ["breathable clothes", "portable fan", "light rain layer"]},
        "autumn": {"summary": "Cool, comfortable, and ideal for city walking.", "packing": ["layered clothing", "light sweater", "comfortable sneakers"]},
        "winter": {"summary": "Cold but manageable in major cities, drier than summer.", "packing": ["coat", "thermal layer", "scarf"]},
    }
}


class WeatherToolService:
    async def get_weather_guidance(self, destination: str, travel_month: str | None, season: str | None) -> dict[str, Any]:
        """Get weather guidance for destination in given month/season using Open-Meteo or mock data."""
        if settings.use_mock_weather:
            return self._mock_weather(destination, travel_month, season)
        
        try:
            # Try to get real weather forecast from Open-Meteo
            weather_data = await self._get_open_meteo_forecast(destination, travel_month)
            if weather_data:
                return weather_data
        except Exception as exc:  # noqa: BLE001
            logger.warning("open_meteo_failed", destination=destination, error=str(exc))
        
        # Fallback to mock if API fails
        return self._mock_weather(destination, travel_month, season, fallback_reason="Open-Meteo API unavailable")

    def _mock_weather(self, destination: str, travel_month: str | None, season: str | None, fallback_reason: str | None = None) -> dict[str, Any]:
        normalized = (destination or "").strip().lower()
        derived_season = (season or self._month_to_season(travel_month)).lower()
        country_data = MOCK_WEATHER.get(normalized, {}) or MOCK_WEATHER.get("japan", {})
        season_data = country_data.get(derived_season, country_data.get("autumn"))
        payload = {
            "summary": season_data["summary"],
            "packing": season_data["packing"],
            "activity_advice": [
                "Keep one indoor backup activity for rainy periods.",
                "Start long walking days early to avoid fatigue and queues.",
            ],
            "fallback_reason": fallback_reason,
        }
        return payload

    async def _get_open_meteo_forecast(self, destination: str, travel_month: str | None) -> dict[str, Any] | None:
        """Fetch real weather forecast from Open-Meteo API for given destination and month."""
        try:
            # Get coordinates for destination (using simple mapping for major cities)
            coords = self._get_destination_coordinates(destination)
            if not coords:
                return None
            
            # Get weather forecast from Open-Meteo
            async with httpx.AsyncClient(timeout=15) as client:
                url = "https://api.open-meteo.com/v1/forecast"
                params = {
                    "latitude": coords["lat"],
                    "longitude": coords["lon"],
                    "current": "temperature_2m,weather_code,precipitation_probability",
                    "temperature_unit": "fahrenheit",
                    "timezone": "auto"
                }
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                # Extract weather info
                current = data.get("current", {})
                temp = current.get("temperature_2m", 70)
                weather_code = current.get("weather_code", 0)
                precip_prob = current.get("precipitation_probability", 10)
                
                # Interpret weather code
                summary = self._interpret_weather_code(weather_code, temp, precip_prob)
                
                # Suggest packing
                packing = self._suggest_packing(temp, weather_code)
                
                return {
                    "summary": summary,
                    "packing": packing,
                    "activity_advice": [
                        "Plan indoor activities for rainy/cold periods.",
                        "Bring weather-appropriate clothing layers.",
                        "Stay hydrated in warm destinations.",
                    ],
                    "temperature_f": temp,
                    "weather_code": weather_code,
                }
        except Exception as exc:
            logger.warning("open_meteo_forecast_error", destination=destination, error=str(exc))
            return None

    def _get_destination_coordinates(self, destination: str) -> dict[str, float] | None:
        """Get latitude/longitude for major destinations."""
        major_destinations = {
            "japan": {"lat": 35.6762, "lon": 139.6503},  # Tokyo
            "tokyo": {"lat": 35.6762, "lon": 139.6503},
            "kyoto": {"lat": 35.0116, "lon": 135.7681},
            "osaka": {"lat": 34.6937, "lon": 135.5023},
            "thailand": {"lat": 13.7563, "lon": 100.5018},  # Bangkok
            "bangkok": {"lat": 13.7563, "lon": 100.5018},
            "vietnam": {"lat": 21.0285, "lon": 105.8542},  # Hanoi
            "hanoi": {"lat": 21.0285, "lon": 105.8542},
            "hochiminh": {"lat": 10.7769, "lon": 106.7009},
            "paris": {"lat": 48.8566, "lon": 2.3522},
            "france": {"lat": 48.8566, "lon": 2.3522},
            "london": {"lat": 51.5074, "lon": -0.1278},
            "uk": {"lat": 51.5074, "lon": -0.1278},
            "spain": {"lat": 40.4168, "lon": -3.7038},  # Madrid
            "madrid": {"lat": 40.4168, "lon": -3.7038},
            "barcelona": {"lat": 41.3851, "lon": 2.1734},
            "italy": {"lat": 41.9028, "lon": 12.4964},  # Rome
            "rome": {"lat": 41.9028, "lon": 12.4964},
            "india": {"lat": 28.7041, "lon": 77.1025},  # Delhi
            "delhi": {"lat": 28.7041, "lon": 77.1025},
            "australia": {"lat": -33.8688, "lon": 151.2093},  # Sydney
            "sydney": {"lat": -33.8688, "lon": 151.2093},
        }
        
        dest_lower = (destination or "").lower().strip()
        return major_destinations.get(dest_lower)

    def _interpret_weather_code(self, code: int, temp: float, precip_prob: int) -> str:
        """Interpret WMO weather code and return human-readable description."""
        # WMO weather codes (simplified)
        descriptions = {
            0: "Clear sky",
            1: "Mostly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            80: "Slight rain showers",
            81: "Moderate rain showers",
            82: "Violent rain showers",
            85: "Slight snow showers",
            86: "Heavy snow showers",
            95: "Thunderstorm with slight hail",
            96: "Thunderstorm with moderate hail",
            99: "Thunderstorm with heavy hail",
        }
        
        base_desc = descriptions.get(code, "Variable weather")
        
        # Add temperature context
        if temp < 32:
            return f"{base_desc}. Cold conditions ({temp}°F) - bring heavy layers and outerwear."
        elif temp < 50:
            return f"{base_desc}. Cool weather ({temp}°F) - bring a light jacket and layers."
        elif temp < 70:
            return f"{base_desc}. Mild conditions ({temp}°F) - perfect for exploring. Bring light layers."
        else:
            rain_note = " Carry an umbrella/rain protection." if precip_prob > 30 else ""
            return f"{base_desc}. Warm ({temp}°F) - comfortable for outdoor activities.{rain_note}"

    def _suggest_packing(self, temp: float, weather_code: int) -> list[str]:
        """Suggest packing items based on weather conditions."""
        items = []
        
        # Temperature-based suggestions
        if temp < 32:
            items.extend(["heavy winter coat", "thermal layers", "gloves", "winter hat", "scarf"])
        elif temp < 50:
            items.extend(["light jacket", "layers", "long pants", "comfortable shoes"])
        elif temp < 70:
            items.extend(["light layers", "comfortable walking shoes", "light sweater"])
        else:
            items.extend(["breathable clothes", "light pants/shorts", "comfortable walking shoes", "sunscreen", "sunglasses"])
        
        # Weather code-based suggestions
        if weather_code in [45, 48, 51, 53, 55, 61, 63, 65, 80, 81, 82]:  # Rain-related
            items.append("compact umbrella")
            items.append("light rain jacket")
        elif weather_code in [71, 73, 75, 85, 86]:  # Snow
            items.append("waterproof boots")
            items.append("heavy winter gear")
        
        if weather_code in [95, 96, 99]:  # Thunderstorms
            items.append("waterproof bag for electronics")
        
        # Common travel items
        if "comfortable shoes" not in " ".join(items).lower():
            items.append("comfortable walking shoes")
        items.extend(["day pack/backpack", "portable charger"])
        
        return list(dict.fromkeys(items))  # Remove duplicates while preserving order

    @staticmethod
    def _month_to_season(travel_month: str | None) -> str:
        if not travel_month:
            return "autumn"
        month = travel_month.strip().lower()
        mapping = {
            "march": "spring", "april": "spring", "may": "spring",
            "june": "summer", "july": "summer", "august": "summer",
            "september": "autumn", "october": "autumn", "november": "autumn",
            "december": "winter", "january": "winter", "february": "winter",
        }
        return mapping.get(month, "autumn")


weather_service = WeatherToolService()
