"""REST Countries API integration for destination metadata."""
from __future__ import annotations

from typing import Any

import httpx

from app.config.settings import get_settings
from app.utils.helpers import cache_get, cache_set
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class CountryToolService:
    """Service for fetching country metadata from REST Countries API."""
    
    async def get_country_info(self, country_name: str) -> dict[str, Any]:
        """
        Get comprehensive country information including official name, capital,
        currencies, languages, region, and travel advisories.
        
        Uses caching to avoid repeated API calls.
        """
        # Check cache first
        cache_key = f"country_info:{country_name.lower()}"
        cached = cache_get(cache_key)
        if cached:
            return cached
        
        try:
            # Try REST Countries API
            result = await self._fetch_rest_countries(country_name)
            if result:
                cache_set(cache_key, result)
                return result
        except Exception as exc:
            logger.warning("rest_countries_api_error", country=country_name, error=str(exc))
        
        # Fallback to mock data
        return self._get_mock_country_info(country_name)
    
    async def _fetch_rest_countries(self, country_name: str) -> dict[str, Any] | None:
        """Fetch country data from REST Countries API."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                # Try by common name first
                url = f"https://restcountries.com/v3.1/name/{country_name}"
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
                if not data or len(data) == 0:
                    return None
                
                # Get the first result (closest match)
                country = data[0]
                
                # Extract useful info
                info = {
                    "name": country.get("name", {}).get("common", country_name),
                    "official_name": country.get("name", {}).get("official", ""),
                    "capital": country.get("capital", [""])[0] if country.get("capital") else "Unknown",
                    "region": country.get("region", "Unknown"),
                    "subregion": country.get("subregion", "Unknown"),
                    "population": country.get("population", 0),
                    "area_km2": country.get("area", 0),
                    "currencies": list(country.get("currencies", {}).keys()),
                    "languages": list(country.get("languages", {}).values()),
                    "timezones": country.get("timezones", []),
                    "driving_side": country.get("car", {}).get("side", "Unknown"),
                    "flag": country.get("flag", ""),
                    "maps_url": country.get("maps", {}).get("googleMaps", ""),
                }
                
                return info
        except Exception as exc:
            logger.warning("fetch_rest_countries_error", country=country_name, error=str(exc))
            return None
    
    def _get_mock_country_info(self, country_name: str) -> dict[str, Any]:
        """Fallback mock data for common destinations."""
        mock_data = {
            "japan": {
                "name": "Japan",
                "official_name": "Nippon-koku",
                "capital": "Tokyo",
                "region": "Asia",
                "subregion": "East Asia",
                "population": 125000000,
                "area_km2": 377975,
                "currencies": ["JPY"],
                "languages": ["Japanese"],
                "timezones": ["UTC+09:00"],
                "driving_side": "left",
                "flag": "🇯🇵",
                "visa_notes": "Visa-free for 90 days (most countries). Haneda and Narita airports.",
            },
            "thailand": {
                "name": "Thailand",
                "official_name": "Kingdom of Thailand",
                "capital": "Bangkok",
                "region": "Asia",
                "subregion": "Southeast Asia",
                "population": 70000000,
                "area_km2": 513120,
                "currencies": ["THB"],
                "languages": ["Thai"],
                "timezones": ["UTC+07:00"],
                "driving_side": "left",
                "flag": "🇹🇭",
                "visa_notes": "Visa-free 30 days or get 60-day tourist visa. Mostly affordable.",
            },
            "france": {
                "name": "France",
                "official_name": "French Republic",
                "capital": "Paris",
                "region": "Europe",
                "subregion": "Western Europe",
                "population": 68000000,
                "area_km2": 551695,
                "currencies": ["EUR"],
                "languages": ["French"],
                "timezones": ["UTC+01:00", "UTC+02:00"],
                "driving_side": "right",
                "flag": "🇫🇷",
                "visa_notes": "Schengen visa may be required. Excellent rail network.",
            },
            "uk": {
                "name": "United Kingdom",
                "official_name": "United Kingdom of Great Britain",
                "capital": "London",
                "region": "Europe",
                "subregion": "Northern Europe",
                "population": 67000000,
                "area_km2": 242495,
                "currencies": ["GBP"],
                "languages": ["English"],
                "timezones": ["UTC+00:00", "UTC+01:00"],
                "driving_side": "left",
                "flag": "🇬🇧",
                "visa_notes": "Visa-free for many nationalities. No Schengen.",
            },
            "india": {
                "name": "India",
                "official_name": "India",
                "capital": "New Delhi",
                "region": "Asia",
                "subregion": "South Asia",
                "population": 1400000000,
                "area_km2": 3287263,
                "currencies": ["INR"],
                "languages": ["Hindi", "English"],
                "timezones": ["UTC+05:30"],
                "driving_side": "left",
                "flag": "🇮🇳",
                "visa_notes": "Tourist visa (e-visa available). Best Oct-Mar.",
            },
        }
        
        country_lower = country_name.lower().strip()
        return mock_data.get(country_lower, {
            "name": country_name,
            "official_name": country_name,
            "capital": "Unknown",
            "region": "Unknown",
            "subregion": "Unknown",
            "currencies": ["Unknown"],
            "languages": ["Unknown"],
            "flag": "🌍",
            "visa_notes": "Check your embassy for visa requirements.",
        })


country_service = CountryToolService()
