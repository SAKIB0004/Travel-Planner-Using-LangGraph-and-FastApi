from __future__ import annotations

from app.utils.logger import get_logger

logger = get_logger(__name__)


SPECIALIST_ORDER = ["destination", "transportation", "accommodation", "budget", "weather", "culture"]


class Router:
    def decide_required_agents(self, parsed_trip_info: dict, user_query: str) -> tuple[list[str], list[str]]:
        query = (user_query or "").lower()
        interests = " ".join(parsed_trip_info.get("interests", [])).lower()
        prefs = " ".join(parsed_trip_info.get("special_preferences", [])).lower()
        combined = f"{query} {interests} {prefs}"
        required = ["destination"]
        reasons = ["destination agent is the default foundation for travel planning."]

        # Transportation agent
        if any(keyword in combined for keyword in ["flight", "transport", "train", "bus", "taxi", "airport", "transit", "travel between"]):
            required.append("transportation")
            reasons.append("transportation and logistics guidance was requested or inferred.")
        else:
            # Transportation is always useful for multi-city trips
            if parsed_trip_info.get("cities") and len(parsed_trip_info.get("cities", [])) > 1:
                required.append("transportation")
                reasons.append("multi-city trip detected; transportation planning is essential.")

        # Accommodation agent
        if any(keyword in combined for keyword in ["hotel", "accommodation", "lodging", "stay", "airbnb", "hostel", "booking", "where to sleep"]):
            required.append("accommodation")
            reasons.append("accommodation and lodging guidance was requested or inferred.")
        else:
            # Accommodation is always useful
            required.append("accommodation")
            reasons.append("accommodation planning is fundamental to travel planning.")

        # Budget agent
        if any(keyword in combined for keyword in ["budget", "cost", "price", "afford", "money", "expense", "free", "cheap"]):
            required.append("budget")
            reasons.append("budget and cost planning was requested or inferred.")
        else:
            # Budget is always useful
            required.append("budget")
            reasons.append("budget planning is essential for all trips.")

        # Weather agent
        if any(keyword in combined for keyword in ["weather", "season", "packing", "rain", "temperature", "month", "climate"]):
            required.append("weather")
            reasons.append("weather-related details were requested or inferred from the trip context.")

        if parsed_trip_info.get("travel_month") or parsed_trip_info.get("season"):
            if "weather" not in required:
                required.append("weather")
                reasons.append("season or travel month was provided, so weather planning adds value.")

        # Culture agent
        if any(keyword in combined for keyword in ["language", "culture", "etiquette", "english", "phrases", "customs", "tips", "local"]):
            required.append("culture")
            reasons.append("language or cultural guidance was requested or inferred.")

        return required, reasons

    def next_node(self, state: dict) -> str:
        required = state.get("required_agents", [])
        completed = state.get("completed_agents", [])
        for agent_name in SPECIALIST_ORDER:
            if agent_name in required and agent_name not in completed:
                return agent_name
        return "synthesis"


router = Router()
