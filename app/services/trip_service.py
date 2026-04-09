from __future__ import annotations

from functools import lru_cache

from app.graph.builder import build_travel_graph
from app.memory.session_memory import session_memory
from app.schemas.request import TripPlanningRequest
from app.schemas.response import FinalTravelPlan, TripPlanningResponse
from app.tools.helper_tools import merge_trip_context
from app.utils.helpers import extract_trip_details
from app.utils.logger import get_logger

logger = get_logger(__name__)



class TripService:
    def __init__(self) -> None:
        self.graph = build_travel_graph()

    async def plan_trip(self, payload: TripPlanningRequest) -> TripPlanningResponse:
        memory_data = session_memory.get(payload.session_id)
        merged_payload = merge_trip_context(payload.model_dump(), memory_data)
        
        # Enrich payload with intelligent trip detail extraction
        extracted_details = extract_trip_details(payload.user_query, merged_payload)
        merged_payload.update(extracted_details)

        state = {
            "session_id": payload.session_id,
            "user_query": payload.user_query,
            "request_payload": merged_payload,
            "parsed_trip_info": {},
            "specialist_outputs": {},
            "required_agents": [],
            "completed_agents": [],
            "router_reasons": [],
            "metadata": {"source": "api"},
            "tool_failures": [],
            "errors": [],
            "needs_itinerary": payload.needs_day_wise_itinerary,
        }

        result = await self.graph.ainvoke(state)
        parsed_trip_info = result.get("parsed_trip_info", {})

        session_memory.upsert(
            payload.session_id,
            {
                "budget": parsed_trip_info.get("budget"),
                "travel_style": parsed_trip_info.get("travel_style"),
                "language_comfort": parsed_trip_info.get("language_comfort"),
                "interests": parsed_trip_info.get("interests", []),
                "food_preferences": merged_payload.get("food_preferences", []),
                "cities": parsed_trip_info.get("cities", []),
                "special_preferences": parsed_trip_info.get("special_preferences", []),
                "destination": parsed_trip_info.get("destination"),
            },
        )

        final_plan = FinalTravelPlan.model_validate(result["final_plan"])
        return TripPlanningResponse(
            session_id=payload.session_id,
            parsed_trip_info=parsed_trip_info,
            called_agents=result.get("completed_agents", []),
            router_reasons=result.get("router_reasons", []),
            tool_failures=result.get("tool_failures", []),
            final_plan=final_plan,
        )


@lru_cache(maxsize=1)
def get_trip_service() -> TripService:
    return TripService()
