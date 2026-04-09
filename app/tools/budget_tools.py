from __future__ import annotations

from typing import Any

from app.config.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Approximate daily budget baselines by destination and travel style (in USD)
BUDGET_BASELINES = {
    "japan": {
        "budget": {"accommodation": 40, "food": 25, "activities": 20, "transport": 15},
        "mid-range": {"accommodation": 80, "food": 50, "activities": 40, "transport": 20},
        "luxury": {"accommodation": 200, "food": 120, "activities": 80, "transport": 30},
    },
    "default": {
        "budget": {"accommodation": 30, "food": 20, "activities": 15, "transport": 10},
        "mid-range": {"accommodation": 70, "food": 45, "activities": 35, "transport": 15},
        "luxury": {"accommodation": 150, "food": 100, "activities": 70, "transport": 25},
    },
}

CURRENCY_RATES = {
    "japan": {"code": "JPY", "rate": 150.0},
    "uk": {"code": "GBP", "rate": 0.79},
    "eu": {"code": "EUR", "rate": 0.92},
    "default": {"code": "USD", "rate": 1.0},
}

MONEY_TIPS = {
    "japan": [
        "Japan is mostly cash-based; ATMs at convenience stores accept foreign cards.",
        "Many small shops and restaurants only accept cash.",
        "IC cards (Suica/Pasmo) are essential for public transport.",
        "Tipping is not expected and can be considered rude.",
        "Department stores and major chains accept cards.",
    ],
    "default": [
        "Carry some cash as backup.",
        "Notify your bank of travel dates to avoid card blocks.",
        "Use ATMs in safe locations.",
        "Avoid exchanging money at airports (poor rates).",
        "Keep receipts for balance verification.",
    ],
}


class BudgetToolService:
    def estimate_daily_budget(
        self, destination: str, travel_style: str, duration_days: int | None = None
    ) -> dict[str, Any]:
        """Estimate daily and total budget breakdown by category."""
        normalized_dest = (destination or "").strip().lower()
        normalized_style = (travel_style or "mid-range").strip().lower()

        # Get baselines
        dest_budget = BUDGET_BASELINES.get(normalized_dest, BUDGET_BASELINES["default"])
        daily_breakdown = dest_budget.get(normalized_style, dest_budget["mid-range"])

        daily_total = sum(daily_breakdown.values())
        trip_total = daily_total * (duration_days or 7) if duration_days else None

        return {
            "destination": destination,
            "travel_style": travel_style or "mid-range",
            "duration_days": duration_days,
            "daily_breakdown": daily_breakdown,
            "daily_total": daily_total,
            "trip_total": trip_total,
            "currency": "USD",
            "note": "Estimates may vary; actual costs depend on choices and inflation.",
        }

    def breakdown_by_category(
        self, destination: str, travel_style: str, duration_days: int
    ) -> dict[str, Any]:
        """Detailed budget breakdown for all categories."""
        daily = self.estimate_daily_budget(destination, travel_style, duration_days)
        daily_breakdown = daily["daily_breakdown"]

        return {
            "accommodation": {
                "daily": daily_breakdown.get("accommodation", 50),
                "total": daily_breakdown.get("accommodation", 50) * duration_days,
                "tips": [
                    "Book 6-8 weeks in advance for better rates.",
                    f"Consider shared accommodations to save money.",
                    "Check reviews on multiple platforms.",
                ],
            },
            "food": {
                "daily": daily_breakdown.get("food", 40),
                "total": daily_breakdown.get("food", 40) * duration_days,
                "tips": [
                    "Eat where locals eat for cheaper, authentic food.",
                    "Mix fine dining with street food and cheap meals.",
                    "Markets often have affordable fresh food.",
                ],
            },
            "activities": {
                "daily": daily_breakdown.get("activities", 30),
                "total": daily_breakdown.get("activities", 30) * duration_days,
                "tips": [
                    "Many museums have free or discounted hours.",
                    "City passes often provide savings on attractions.",
                    "Some activities (parks, neighborhoods) are free.",
                ],
            },
            "transport": {
                "daily": daily_breakdown.get("transport", 15),
                "total": daily_breakdown.get("transport", 15) * duration_days,
                "tips": [
                    "Get multi-day transit passes for savings.",
                    "Walk when possible for budget and experience.",
                    "Public transit is usually cheaper than taxis.",
                ],
            },
        }

    def get_currency_info(self, destination: str) -> dict[str, Any]:
        """Get currency and exchange rate information."""
        normalized = (destination or "").strip().lower()
        currency_info = CURRENCY_RATES.get(normalized, CURRENCY_RATES["default"])

        return {
            "destination": destination,
            "currency_code": currency_info["code"],
            "usd_exchange_rate": currency_info["rate"],
            "cash_recommendations": "Research current rates before departure.",
            "payment_methods": ["Major credit cards", "Debit cards at ATMs", "Local cash"],
        }

    def get_money_tips(self, destination: str) -> dict[str, Any]:
        """Get destination-specific money and payment tips."""
        normalized = (destination or "").strip().lower()
        tips = MONEY_TIPS.get(normalized, MONEY_TIPS["default"])

        return {
            "destination": destination,
            "tips": tips,
            "general_advice": [
                "Notify your bank before traveling.",
                "Keep copies of card numbers separately.",
                "Use ATMs in well-lit, secure locations.",
                "Divide money across multiple locations.",
            ],
        }


budget_service = BudgetToolService()
