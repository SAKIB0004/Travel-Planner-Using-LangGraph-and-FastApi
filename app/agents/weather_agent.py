from __future__ import annotations

from typing import Any

from app.config.settings import get_settings
from app.prompts.weather_prompt import WEATHER_PROMPT
from app.tools.weather_tools import weather_service
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class WeatherPlanningAgent:
    def __init__(self) -> None:
        self._llm = None
        if not settings.use_mock_llm:
            from langchain_groq import ChatGroq
            self._llm = ChatGroq(model=settings.groq_model, api_key=settings.groq_api_key, temperature=0.2)

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        parsed = state["parsed_trip_info"]
        weather_context = await weather_service.get_weather_guidance(
            parsed.get("destination") or "",
            parsed.get("travel_month"),
            parsed.get("season"),
        )
        if weather_context.get("fallback_reason"):
            state["tool_failures"].append(f"weather_fallback_used: {weather_context['fallback_reason']}")

        if settings.use_mock_llm:
            return self._heuristic_output(parsed, weather_context)

        from langchain_core.messages import HumanMessage
        
        prompt = (
            f"{WEATHER_PROMPT}\n\n"
            f"Parsed trip info: {parsed}\n\n"
            f"Weather context: {weather_context}"
        )
        message = await self._llm.ainvoke([HumanMessage(content=prompt)])
        return self._heuristic_output(parsed, weather_context, llm_text=message.content)

    def _heuristic_output(self, parsed: dict[str, Any], weather_context: dict[str, Any], llm_text: str | None = None) -> dict[str, Any]:
        return {
            "summary": llm_text or f"Weather guidance prepared for {parsed.get('destination') or 'the trip'}.",
            "weather_expectations": [weather_context["summary"]],
            "packing_suggestions": weather_context["packing"],
            "activity_advice": weather_context["activity_advice"],
        }


weather_agent = WeatherPlanningAgent()
