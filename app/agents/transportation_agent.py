from __future__ import annotations

from typing import Any

from app.config.settings import get_settings
from app.prompts.transportation_prompt import TRANSPORTATION_PROMPT
from app.tools.transportation_tools import transportation_service
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class TransportationAgent:
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
        request_payload = state.get("request_payload", {})
        origin_country = request_payload.get("origin_country") or "US"

        # Get transportation data from tools
        flights = await transportation_service.get_flights(origin_country, destination, duration_days)
        local_transit = await transportation_service.get_local_transit(destination)
        inter_city_travel = None
        if cities and len(cities) > 1:
            inter_city_travel = await transportation_service.get_travel_between_cities(
                cities[0], cities[1] if len(cities) > 1 else cities[0], destination
            )
        transportation_costs = await transportation_service.estimate_transportation_costs(destination, cities, duration_days)

        if settings.use_mock_llm:
            return self._heuristic_output(parsed, flights, local_transit, inter_city_travel, transportation_costs)

        from langchain_core.messages import HumanMessage
        
        prompt = (
            f"{TRANSPORTATION_PROMPT}\n\n"
            f"Parsed trip info: {parsed}\n\n"
            f"Flights: {flights}\n\n"
            f"Local transit: {local_transit}\n\n"
            f"Inter-city travel: {inter_city_travel}\n\n"
            f"Transportation costs: {transportation_costs}"
        )
        message = await self._llm.ainvoke([HumanMessage(content=prompt)])
        return self._heuristic_output(parsed, flights, local_transit, inter_city_travel, transportation_costs, llm_text=message.content)

    def _heuristic_output(
        self,
        parsed: dict[str, Any],
        flights: dict[str, Any],
        local_transit: dict[str, Any],
        inter_city_travel: dict[str, Any] | None,
        transportation_costs: dict[str, Any],
        llm_text: str | None = None,
    ) -> dict[str, Any]:
        destination = parsed.get("destination") or "the destination"
        cities = parsed.get("cities", [])

        return {
            "summary": llm_text or f"Transportation planning for {destination} including flights, local transit, and inter-city options.",
            "international_flights": {
                "estimate": flights["estimated_price_range"],
                "duration_hours": flights["duration_hours"],
                "airlines": flights["airlines"],
                "booking_tips": flights["booking_tips"],
            },
            "local_transportation": {
                "options": local_transit["transit_options"],
                "daily_cost": local_transit["daily_cost"],
                "ic_card_cost": local_transit.get("ic_card_cost"),
                "recommended_apps": local_transit["recommended_apps"],
                "tips": local_transit["tips"],
            },
            "inter_city_travel": inter_city_travel
            if inter_city_travel
            else {"note": "Single city trip - no inter-city travel needed"},
            "cost_summary": {
                "daily_local_transit": transportation_costs["daily_local_transit"],
                "inter_city_travel": transportation_costs["inter_city_travel"],
                "total_ground_transportation": transportation_costs["total_transportation"],
            },
            "practical_advice": [
                "Book international flights immediately after deciding on dates.",
                "Get IC cards or transit passes upon arrival.",
                "Download offline maps as backup.",
                "Keep emergency taxi numbers handy.",
            ],
        }


transportation_agent = TransportationAgent()
