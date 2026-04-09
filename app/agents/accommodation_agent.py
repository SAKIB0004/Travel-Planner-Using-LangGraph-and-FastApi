from __future__ import annotations

from typing import Any

from app.config.settings import get_settings
from app.prompts.accommodation_prompt import ACCOMMODATION_PROMPT
from app.tools.accommodation_tools import accommodation_service
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class AccommodationAgent:
    def __init__(self) -> None:
        self._llm = None
        if not settings.use_mock_llm:
            from langchain_groq import ChatGroq

            self._llm = ChatGroq(model=settings.groq_model, api_key=settings.groq_api_key, temperature=0.2)

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        parsed = state["parsed_trip_info"]
        destination = parsed.get("destination") or "destination"
        cities = parsed.get("cities", [])
        duration_days = parsed.get("duration_days") or 7
        travel_style = parsed.get("travel_style") or "mid-range"
        budget_preference = parsed.get("budget") or "mid-range"

        # Get accommodation data from tools
        accommodations_by_city = {}
        for city in cities if cities else [destination]:
            accommodations_by_city[city] = accommodation_service.search_accommodations(destination, city, budget_preference)

        accommodation_breakdown = accommodation_service.get_accommodation_breakdown(
            destination, cities if cities else [destination], budget_preference, duration_days
        )
        booking_tips = accommodation_service.get_booking_tips(destination, budget_preference)

        if settings.use_mock_llm:
            return self._heuristic_output(parsed, accommodations_by_city, accommodation_breakdown, booking_tips)

        from langchain_core.messages import HumanMessage
        
        prompt = (
            f"{ACCOMMODATION_PROMPT}\n\n"
            f"Parsed trip info: {parsed}\n\n"
            f"Accommodations by city: {accommodations_by_city}\n\n"
            f"Accommodation breakdown: {accommodation_breakdown}\n\n"
            f"Booking tips: {booking_tips}"
        )
        message = await self._llm.ainvoke([HumanMessage(content=prompt)])
        return self._heuristic_output(parsed, accommodations_by_city, accommodation_breakdown, booking_tips, llm_text=message.content)

    def _heuristic_output(
        self,
        parsed: dict[str, Any],
        accommodations_by_city: dict[str, Any],
        accommodation_breakdown: dict[str, Any],
        booking_tips: dict[str, Any],
        llm_text: str | None = None,
    ) -> dict[str, Any]:
        destination = parsed.get("destination") or "the destination"
        cities = parsed.get("cities", [])
        travel_style = parsed.get("travel_style") or "mid-range"

        return {
            "summary": llm_text
            or f"Accommodation recommendations for {destination} in {travel_style} style across {len(cities)} cities.",
            "by_city": accommodations_by_city,
            "cost_breakdown": {
                "daily_estimates": accommodation_breakdown["by_city"],
                "total_cost": accommodation_breakdown["total_accommodation_cost"],
                "average_per_night": accommodation_breakdown["average_per_night"],
            },
            "booking_platforms": booking_tips.get("booking_platforms", {}),
            "recommended_neighborhoods": {
                city: accom.get("recommended_neighborhoods", [])
                for city, accom in accommodations_by_city.items()
            },
            "accommodation_types": {
                city: accom.get("accommodation_types", [])
                for city, accom in accommodations_by_city.items()
            },
            "booking_tips": booking_tips["booking_tips"],
            "general_advice": booking_tips["general_advice"],
            "red_flags_to_avoid": booking_tips["red_flags"],
            "practical_advice": [
                "Book accommodations 4-8 weeks in advance.",
                "Read recent reviews from the last 3 months.",
                "Verify location on maps before confirming.",
                "Confirm cancellation policy and what's included.",
                "Book directly or through established platforms.",
            ],
        }


accommodation_agent = AccommodationAgent()
