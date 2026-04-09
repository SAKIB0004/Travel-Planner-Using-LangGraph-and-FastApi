from __future__ import annotations

from typing import Any

from app.config.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Mock accommodation data by destination and city
ACCOMMODATION_DATA = {
    "japan": {
        "tokyo": {
            "budget": {
                "avg_price": 45,
                "types": ["Capsule Hotel", "Hostel", "Budget Guesthouse"],
                "neighborhoods": ["Asakusa", "Ikebukuro", "Ueno"],
            },
            "mid-range": {
                "avg_price": 90,
                "types": ["Business Hotel", "Ryokan Lite", "Modern Guesthouse"],
                "neighborhoods": ["Shinjuku", "Shibuya", "Sendagi"],
            },
            "luxury": {
                "avg_price": 250,
                "types": ["5-Star Hotel", "Traditional Ryokan", "Boutique Hotel"],
                "neighborhoods": ["Ginza", "Marunouchi", "Roppongi"],
            },
        },
        "osaka": {
            "budget": {
                "avg_price": 40,
                "types": ["Capsule Hotel", "Hostel", "Guesthouse"],
                "neighborhoods": ["Namba", "Nipponbashi", "Kawaramachi"],
            },
            "mid-range": {
                "avg_price": 75,
                "types": ["Business Hotel", "Ryokan", "Guesthouse"],
                "neighborhoods": ["Umeda", "Dotonbori", "Nakazaki"],
            },
            "luxury": {
                "avg_price": 200,
                "types": ["5-Star Hotel", "Luxury Ryokan"],
                "neighborhoods": ["Kobe", "Kyoto suburbs"],
            },
        },
    },
    "default": {
        "default": {
            "budget": {
                "avg_price": 30,
                "types": ["Hostel", "Guesthouse"],
                "neighborhoods": ["City center outskirts", "Near transit"],
            },
            "mid-range": {
                "avg_price": 70,
                "types": ["3-Star Hotel", "Boutique Hotel"],
                "neighborhoods": ["Downtown", "Tourist areas"],
            },
            "luxury": {
                "avg_price": 180,
                "types": ["5-Star Hotel", "Luxury Resort"],
                "neighborhoods": ["Premium districts"],
            },
        },
    },
}

BOOKING_PLATFORMS = {
    "japan": {
        "for_tourists": ["Booking.com", "Agoda", "Hotels.com"],
        "for_locals": ["Airbnb", "Tabichoice (Japanese site)", "Minpaku"],
        "traditional_ryokan": ["Booking.com Ryokan filter", "Japanese inn directories"],
    },
    "default": {
        "for_tourists": ["Booking.com", "Hotels.com", "Tripadvisor"],
        "for_locals": ["Airbnb", "Vrbo"],
    },
}


class AccommodationToolService:
    def search_accommodations(
        self, destination: str, city: str | None, travel_style: str
    ) -> dict[str, Any]:
        """Search accommodations in a destination by city and travel style."""
        normalized_dest = (destination or "").strip().lower()
        normalized_city = (city or "").strip().lower() if city else "default"
        normalized_style = (travel_style or "mid-range").strip().lower()

        # Get accommodation data
        dest_data = ACCOMMODATION_DATA.get(normalized_dest, ACCOMMODATION_DATA["default"])
        city_data = dest_data.get(normalized_city, dest_data.get("default", {}))
        style_data = city_data.get(normalized_style, city_data.get("mid-range", {}))

        return {
            "destination": destination,
            "city": city or "Various",
            "travel_style": travel_style,
            "average_price_per_night": style_data.get("avg_price", 60),
            "accommodation_types": style_data.get("types", []),
            "recommended_neighborhoods": style_data.get("neighborhoods", []),
            "booking_platforms": BOOKING_PLATFORMS.get(normalized_dest, BOOKING_PLATFORMS["default"]),
        }

    def get_accommodation_breakdown(
        self, destination: str, cities: list[str], travel_style: str, duration_days: int
    ) -> dict[str, Any]:
        """Get detailed accommodation cost breakdown for multi-city trip."""
        breakdown = {}
        total_cost = 0

        for city in cities:
            search_result = self.search_accommodations(destination, city, travel_style)
            night_price = search_result["average_price_per_night"]
            # Rough split of nights across cities
            nights_per_city = duration_days // len(cities) if cities else duration_days
            city_cost = night_price * nights_per_city

            breakdown[city] = {
                "nights": nights_per_city,
                "price_per_night": night_price,
                "total": city_cost,
                "neighborhoods": search_result["recommended_neighborhoods"],
            }
            total_cost += city_cost

        return {
            "destination": destination,
            "travel_style": travel_style,
            "total_duration_days": duration_days,
            "by_city": breakdown,
            "total_accommodation_cost": total_cost,
            "average_per_night": int(total_cost / duration_days) if duration_days else 0,
        }

    def get_booking_tips(self, destination: str, travel_style: str) -> dict[str, Any]:
        """Get booking tips specific to destination and travel style."""
        tips_by_style = {
            "budget": [
                "Book well in advance for better rates.",
                "Consider staying slightly outside tourist areas.",
                "Hostels often have budget rooms for solo travelers.",
                "Airbnb can be cheaper than hotels for longer stays.",
                "Check for longer-stay discounts (weekly/monthly).",
            ],
            "mid-range": [
                "Book 4-6 weeks ahead for good prices.",
                "Mix of online booking and direct hotel calls.",
                "Join loyalty programs for discounts.",
                "Travel during shoulder season for better rates.",
                "Negotiate if booking longer stays.",
            ],
            "luxury": [
                "Book directly with hotels for best packages.",
                "Concierge services help with special requests.",
                "Travel insurance recommended for high-value bookings.",
                "Ask about package deals and upgrades.",
                "Confirm all services before booking.",
            ],
        }

        normalized_style = (travel_style or "mid-range").strip().lower()
        tips = tips_by_style.get(normalized_style, tips_by_style["mid-range"])

        return {
            "destination": destination,
            "travel_style": travel_style,
            "booking_tips": tips,
            "general_advice": [
                "Read recent reviews (last 3 months).",
                "Check what's included (WiFi, breakfast, etc.).",
                "Verify cancellation policy.",
                "Confirm location on a map before booking.",
                "Book directly or use reputable platforms.",
            ],
            "red_flags": [
                "Prices too good to be true.",
                "No recent reviews.",
                "Hidden fees in fine print.",
                "Unlicensed or unverified properties.",
                "Poor photo quality or limited information.",
            ],
        }

    def estimate_accommodation_cost(self, destination: str, travel_style: str, duration_days: int) -> dict[str, Any]:
        """Quick estimate of accommodation cost for the trip."""
        search = self.search_accommodations(destination, "default", travel_style)
        nightly_rate = search["average_price_per_night"]
        total = nightly_rate * duration_days

        return {
            "destination": destination,
            "travel_style": travel_style,
            "duration_days": duration_days,
            "nightly_rate_estimate": nightly_rate,
            "total_cost_estimate": total,
            "currency": "USD",
            "note": "Prices vary by season, location, and specific property.",
        }


accommodation_service = AccommodationToolService()
