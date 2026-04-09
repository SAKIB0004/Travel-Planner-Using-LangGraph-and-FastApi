from __future__ import annotations

from typing import Any

from app.config.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Mock flight and transit data
FLIGHT_BASELINES = {
    "japan": {
        "from_us": {"price_range": (600, 900), "duration_hours": 14},
        "from_eu": {"price_range": (500, 800), "duration_hours": 12},
        "from_asia": {"price_range": (200, 500), "duration_hours": 3},
    },
    "default": {
        "from_us": {"price_range": (800, 1200), "duration_hours": 16},
        "from_eu": {"price_range": (400, 700), "duration_hours": 8},
    },
}

LOCAL_TRANSIT = {
    "japan": {
        "options": ["JR Train", "Subway", "Bus", "IC Card (Suica/Pasmo)"],
        "ic_card_cost": 30,
        "daily_transit_cost": 12,
        "travel_time_tokyo_osaka": 2.5,  # hours by Shinkansen
        "tips": [
            "Get a Suica or Pasmo card at the airport or convenience stores.",
            "Shinkansen (bullet train) connects major cities efficiently.",
            "Subway maps are in English and very accessible.",
            "Buses have English announcements in major cities.",
        ],
    },
    "default": {
        "options": ["Public Transit", "Taxi", "Ride-share"],
        "daily_transit_cost": 10,
        "tips": [
            "Plan routes using Google Maps.",
            "Validate passes/cards regularly.",
            "Avoid peak hours if possible.",
            "Keep emergency taxi numbers.",
        ],
    },
}


class TransportationToolService:
    async def get_flights(
        self, origin_country: str, destination: str, duration_days: int | None = None
    ) -> dict[str, Any]:
        """Get flight information for the trip."""
        normalized_dest = (destination or "").strip().lower()
        normalized_origin = (origin_country or "US").strip().lower()

        dest_flights = FLIGHT_BASELINES.get(normalized_dest, FLIGHT_BASELINES["default"])
        origin_key = "from_us" if "us" in normalized_origin else "from_eu"

        flight_info = dest_flights.get(origin_key, dest_flights.get(list(dest_flights.keys())[0]))

        return {
            "destination": destination,
            "origin": origin_country,
            "estimated_price_range": f"${flight_info['price_range'][0]}-${flight_info['price_range'][1]}",
            "duration_hours": flight_info["duration_hours"],
            "airlines": ["United", "JAL", "ANA", "Lufthansa"],
            "booking_tips": [
                "Book flights 3-6 weeks in advance.",
                "Use flight comparison sites (Google Flights, Skyscanner, Kayak).",
                "Flying mid-week is often cheaper.",
                "Round-trip is usually cheaper than one-way.",
                "Sign up for price alerts.",
            ],
            "note": "Prices vary with season, airline, and booking timing.",
        }

    async def get_local_transit(self, destination: str) -> dict[str, Any]:
        """Get local transportation information for a destination."""
        normalized_dest = (destination or "").strip().lower()
        transit_info = LOCAL_TRANSIT.get(normalized_dest, LOCAL_TRANSIT["default"])

        return {
            "destination": destination,
            "transit_options": transit_info.get("options", []),
            "daily_cost": transit_info.get("daily_transit_cost", 10),
            "ic_card_cost": transit_info.get("ic_card_cost"),
            "tips": transit_info.get("tips", []),
            "recommended_apps": (
                ["Google Maps", "Suica App", "Tabinote"] if normalized_dest == "japan" else ["Google Maps", "Citymapper"]
            ),
        }

    async def get_travel_between_cities(
        self, origin_city: str, destination_city: str, destination_country: str
    ) -> dict[str, Any]:
        """Get travel information between cities."""
        # Mock data for inter-city travel
        city_pair = f"{origin_city.lower()}-{destination_city.lower()}"

        if destination_country.lower() == "japan" and "tokyo" in city_pair and "osaka" in city_pair:
            return {
                "from_city": origin_city,
                "to_city": destination_city,
                "options": [
                    {
                        "method": "Shinkansen (Bullet Train)",
                        "duration": "2.5 hours",
                        "price": 120,
                        "frequency": "Every 10 minutes",
                    },
                    {
                        "method": "Regular Train",
                        "duration": "3.5 hours",
                        "price": 60,
                        "frequency": "Hourly",
                    },
                    {
                        "method": "Flight",
                        "duration": "1 hour flight + 2 hours airport time",
                        "price": 100,
                        "frequency": "Multiple daily",
                    },
                ],
                "recommendation": "Shinkansen offers best value and experience.",
            }
        else:
            return {
                "from_city": origin_city,
                "to_city": destination_city,
                "options": [
                    {
                        "method": "Train/Bus",
                        "duration": "Check schedules",
                        "price": "Varies",
                    },
                    {
                        "method": "Flight",
                        "duration": "Check airports",
                        "price": "Varies",
                    },
                ],
                "recommendation": "Research route-specific options via Google Maps or Rome2Rio.",
            }

    async def estimate_transportation_costs(
        self, destination: str, cities: list[str], duration_days: int
    ) -> dict[str, Any]:
        """Estimate total transportation costs for the trip."""
        local_transit = await self.get_local_transit(destination)
        daily_local_cost = local_transit.get("daily_cost", 10)

        # Inter-city costs (rough estimate)
        inter_city_cost = 100 if len(cities) > 1 else 0

        total = (daily_local_cost * duration_days) + inter_city_cost

        return {
            "destination": destination,
            "cities": cities,
            "daily_local_transit": daily_local_cost,
            "inter_city_travel": inter_city_cost,
            "total_transportation": total,
            "currency": "USD",
            "breakdown": {
                "local_transit": daily_local_cost * duration_days,
                "inter_city": inter_city_cost,
                "contingency": int(total * 0.1),  # 10% buffer
            },
        }


transportation_service = TransportationToolService()
