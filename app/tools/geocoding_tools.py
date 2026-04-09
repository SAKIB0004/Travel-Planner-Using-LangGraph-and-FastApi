"""Nominatim geocoding and distance calculation service."""
from __future__ import annotations

import math
from typing import Any

import httpx

from app.config.settings import get_settings
from app.utils.helpers import cache_get, cache_set
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class GeocodingToolService:
    """Service for geocoding cities and calculating distances using Nominatim."""
    
    async def get_city_coordinates(self, city_name: str, country: str | None = None) -> dict[str, float] | None:
        """
        Get latitude/longitude for a city using Nominatim OpenStreetMap.
        Results are cached to avoid repeated calls.
        """
        # Check cache
        cache_key = f"geocode:{city_name.lower()}:{(country or 'unknown').lower()}"
        cached = cache_get(cache_key)
        if cached:
            return cached
        
        try:
            # Try Nominatim API
            result = await self._nominatim_search(city_name, country)
            if result:
                cache_set(cache_key, result)
                return result
        except Exception as exc:
            logger.warning("nominatim_search_error", city=city_name, country=country, error=str(exc))
        
        # Fallback to known major cities
        return self._get_known_city_coordinates(city_name, country)
    
    async def _nominatim_search(self, city_name: str, country: str | None = None) -> dict[str, float] | None:
        """Search for city using Nominatim API (OpenStreetMap)."""
        try:
            query = f"{city_name}, {country}" if country else city_name
            
            async with httpx.AsyncClient(timeout=10) as client:
                url = "https://nominatim.openstreetmap.org/search"
                params = {
                    "q": query,
                    "format": "json",
                    "limit": 1,
                }
                headers = {
                    "User-Agent": "TravelPlanner/1.0",
                }
                
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()
                
                if data and len(data) > 0:
                    result = data[0]
                    return {
                        "lat": float(result["lat"]),
                        "lon": float(result["lon"]),
                        "display_name": result.get("display_name", ""),
                    }
        except Exception as exc:
            logger.debug("nominatim_api_error", city=city_name, error=str(exc))
            return None
        
        return None
    
    def _get_known_city_coordinates(self, city_name: str, country: str | None = None) -> dict[str, float] | None:
        """Fallback to pre-defined coordinates for major cities."""
        known_locations = {
            ("tokyo", "japan"): {"lat": 35.6762, "lon": 139.6503},
            ("tokyo", None): {"lat": 35.6762, "lon": 139.6503},
            ("kyoto", "japan"): {"lat": 35.0116, "lon": 135.7681},
            ("kyoto", None): {"lat": 35.0116, "lon": 135.7681},
            ("osaka", "japan"): {"lat": 34.6937, "lon": 135.5023},
            ("osaka", None): {"lat": 34.6937, "lon": 135.5023},
            ("bangkok", "thailand"): {"lat": 13.7563, "lon": 100.5018},
            ("bangkok", None): {"lat": 13.7563, "lon": 100.5018},
            ("phuket", "thailand"): {"lat": 8.1409, "lon": 98.3013},
            ("chiang mai", "thailand"): {"lat": 18.7883, "lon": 98.9853},
            ("hanoi", "vietnam"): {"lat": 21.0285, "lon": 105.8542},
            ("hochiminh", "vietnam"): {"lat": 10.7769, "lon": 106.7009},
            ("saigon", "vietnam"): {"lat": 10.7769, "lon": 106.7009},
            ("paris", "france"): {"lat": 48.8566, "lon": 2.3522},
            ("paris", None): {"lat": 48.8566, "lon": 2.3522},
            ("london", "uk"): {"lat": 51.5074, "lon": -0.1278},
            ("london", None): {"lat": 51.5074, "lon": -0.1278},
            ("barcelona", "spain"): {"lat": 41.3851, "lon": 2.1734},
            ("madrid", "spain"): {"lat": 40.4168, "lon": -3.7038},
            ("rome", "italy"): {"lat": 41.9028, "lon": 12.4964},
            ("rome", None): {"lat": 41.9028, "lon": 12.4964},
            ("venice", "italy"): {"lat": 45.4408, "lon": 12.3155},
            ("delhi", "india"): {"lat": 28.7041, "lon": 77.1025},
            ("sydney", "australia"): {"lat": -33.8688, "lon": 151.2093},
            ("sydney", None): {"lat": -33.8688, "lon": 151.2093},
            ("singapore", "singapore"): {"lat": 1.3521, "lon": 103.8198},
            ("singapore", None): {"lat": 1.3521, "lon": 103.8198},
        }
        
        city_lower = city_name.lower().strip()
        country_lower = (country or "").lower().strip()
        
        # Try with country first
        if country:
            coords = known_locations.get((city_lower, country_lower))
            if coords:
                return coords
        
        # Try without country
        coords = known_locations.get((city_lower, None))
        if coords:
            return coords
        
        return None
    
    def calculate_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
    ) -> float:
        """
        Calculate distance between two coordinates using Haversine formula.
        Returns distance in kilometers.
        """
        R = 6371  # Earth radius in km
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = (
            math.sin(dlat / 2) ** 2 +
            math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    async def get_travel_time_hint(self, city1: str, city2: str, country: str | None = None) -> str:
        """
        Get approximate travel time between two cities.
        Based on distance (rough estimates for different transport modes).
        """
        coords1 = await self.get_city_coordinates(city1, country)
        coords2 = await self.get_city_coordinates(city2, country)
        
        if not coords1 or not coords2:
            return "Check travel times for these cities."
        
        distance_km = self.calculate_distance(
            coords1["lat"], coords1["lon"],
            coords2["lat"], coords2["lon"]
        )
        
        # Estimate travel times
        if distance_km < 50:
            return f"{distance_km:.0f}km apart - About {int(distance_km / 4)} hours by car, 1-2 hours by train if available."
        elif distance_km < 200:
            hours_drive = int(distance_km / 80)
            return f"{distance_km:.0f}km apart - About {hours_drive} hours by car, or 2-3 hours by train/bus."
        elif distance_km < 500:
            hours_drive = int(distance_km / 60)
            return f"{distance_km:.0f}km apart - About {hours_drive}+ hours by car. Consider internal flights or buses (4-6 hours)."
        else:
            return f"{distance_km:.0f}km apart - Too far for day trip. Plan 1+ nights travel or fly."


geocoding_service = GeocodingToolService()
