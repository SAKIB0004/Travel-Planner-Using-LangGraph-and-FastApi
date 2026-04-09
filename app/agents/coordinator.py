from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.config.settings import get_settings
from app.prompts.coordinator_prompt import COORDINATOR_PARSE_PROMPT, COORDINATOR_SYNTHESIS_PROMPT
from app.schemas.response import FinalTravelPlan, ItineraryDay, PhraseItem
from app.utils.logger import get_logger
from app.utils.helpers import (
    extract_trip_details, 
    create_polished_response,
    normalize_travel_type,
    normalize_budget_style,
    resolve_destination,
    validate_itinerary,
    estimate_city_days,
)

logger = get_logger(__name__)
settings = get_settings()



class ParsedTripInfo(BaseModel):
    destination: str | None = None
    cities: list[str] = Field(default_factory=list)
    duration_days: int | None = None
    travel_style: str | None = None
    interests: list[str] = Field(default_factory=list)
    budget: str | None = None
    season: str | None = None
    travel_month: str | None = None
    language_comfort: str | None = None
    special_preferences: list[str] = Field(default_factory=list)
    missing_details: list[str] = Field(default_factory=list)


class CoordinatorAgent:
    def __init__(self) -> None:
        self._llm = None
        if not settings.use_mock_llm:
            from langchain_groq import ChatGroq
            self._llm = ChatGroq(model=settings.groq_model, api_key=settings.groq_api_key, temperature=0.2)

    async def parse_trip_info(self, payload: dict[str, Any]) -> ParsedTripInfo:
        logger.info("coordinator_parse_started")
        if settings.use_mock_llm:
            return self._heuristic_parse(payload)

        from langchain_core.messages import HumanMessage
        
        structured_llm = self._llm.with_structured_output(ParsedTripInfo)
        user_query = payload.get("user_query", "")
        prompt = (
            f"{COORDINATOR_PARSE_PROMPT}\n\n"
            f"Input payload:\n{payload}\n\n"
            f"User query:\n{user_query}"
        )
        result = await structured_llm.ainvoke([HumanMessage(content=prompt)])
        return result

    async def synthesize(self, state: dict[str, Any]) -> FinalTravelPlan:
        logger.info("coordinator_synthesis_started")
        if settings.use_mock_llm:
            return self._heuristic_synthesis(state)

        from langchain_core.messages import HumanMessage
        
        structured_llm = self._llm.with_structured_output(FinalTravelPlan)
        prompt = (
            f"{COORDINATOR_SYNTHESIS_PROMPT}\n\n"
            f"Parsed trip info:\n{state['parsed_trip_info']}\n\n"
            f"Destination output:\n{state['specialist_outputs'].get('destination', {})}\n\n"
            f"Transportation output:\n{state['specialist_outputs'].get('transportation', {})}\n\n"
            f"Accommodation output:\n{state['specialist_outputs'].get('accommodation', {})}\n\n"
            f"Budget output:\n{state['specialist_outputs'].get('budget', {})}\n\n"
            f"Weather output:\n{state['specialist_outputs'].get('weather', {})}\n\n"
            f"Culture output:\n{state['specialist_outputs'].get('culture', {})}"
        )
        return await structured_llm.ainvoke([HumanMessage(content=prompt)])

    def _heuristic_parse(self, payload: dict[str, Any]) -> ParsedTripInfo:
        user_query = payload.get("user_query", "")
        
        # Use intelligent extraction to fill missing details
        extracted = extract_trip_details(user_query, payload)
        
        # Ensure normalization of budget and travel_style
        normalized_budget = normalize_budget_style(extracted.get("budget"))
        normalized_travel_style = normalize_travel_type(extracted.get("travel_style"))
        
        # Resolve destination and cities properly
        primary_destination, cities = resolve_destination(
            destination=extracted.get("destination"),
            cities=extracted.get("cities", []),
            country=extracted.get("country")
        )
        
        missing = []
        if not primary_destination:
            missing.append("destination")
        if not extracted.get("duration_days"):
            missing.append("duration_days")
        
        return ParsedTripInfo(
            destination=primary_destination,
            cities=cities,
            duration_days=extracted.get("duration_days"),
            travel_style=normalized_travel_style,
            interests=extracted.get("interests", []),
            budget=normalized_budget,
            season=extracted.get("season"),
            travel_month=extracted.get("travel_month"),
            language_comfort=extracted.get("language_comfort"),
            special_preferences=extracted.get("special_preferences", []),
            missing_details=missing,
        )

    def _heuristic_synthesis(self, state: dict[str, Any]) -> FinalTravelPlan:
        parsed = state["parsed_trip_info"]
        specialist_outputs = state["specialist_outputs"]
        
        # Prepare trip_info dict for helpers
        trip_info = {
            "destination": parsed.get("destination"),
            "cities": parsed.get("cities", []),
            "duration_days": parsed.get("duration_days"),
            "travel_style": parsed.get("travel_style"),
            "budget": parsed.get("budget"),
            "travel_month": parsed.get("travel_month"),
            "interests": parsed.get("interests", []),
        }
        
        # Generate polished markdown response using all agent outputs
        polished_narrative = create_polished_response(trip_info, specialist_outputs, include_raw=False)
        
        # Build detailed FinalTravelPlan for structured API response
        destination_output = specialist_outputs.get("destination", {})
        transportation_output = specialist_outputs.get("transportation", {})
        accommodation_output = specialist_outputs.get("accommodation", {})
        budget_output = specialist_outputs.get("budget", {})
        weather_output = specialist_outputs.get("weather", {})
        culture_output = specialist_outputs.get("culture", {})
        
        cities = parsed.get("cities", [])
        duration = parsed.get("duration_days", 7)
        city_text = ", ".join(cities) if cities else parsed.get("destination", "your destination")
        
        # Generate smarter itinerary with proper day allocation
        itinerary = []
        if state.get("needs_itinerary") and cities:
            # Use the new day estimation for better allocation
            city_days = estimate_city_days(cities, duration)
            day_counter = 1
            
            for idx, city in enumerate(cities):
                num_days = city_days.get(city, 1)
                day_start = day_counter
                day_end = day_counter + num_days - 1
                
                # Arrival day special handling
                if idx == 0:
                    itinerary.append(ItineraryDay(
                        day=day_start,
                        theme="Arrival and neighborhood orientation",
                        activities=[
                            "Check in and rest",
                            f"Evening walk around {city}",
                            "Early dinner at a local restaurant",
                            "Get your bearings in the neighborhood"
                        ]
                    ))
                    day_counter += 1
                
                # Full days in the city
                remaining_days = num_days - (1 if idx == 0 else 0) - (1 if idx == len(cities) - 1 else 0)
                if remaining_days > 0:
                    activities = destination_output.get("sample_day", [
                        f"Visit main attractions and cultural sites",
                        "Try local cuisine and street food",
                        "Explore different neighborhoods",
                        "Take a guided tour or museum visit"
                    ])[:remaining_days + 2]
                    
                    itinerary.append(ItineraryDay(
                        day=day_counter if idx > 0 else day_start + 1,
                        theme=f"Explore {city}",
                        activities=activities
                    ))
                    day_counter += remaining_days
                
                # Last day handling
                if idx == len(cities) - 1 and day_counter <= duration:
                    itinerary.append(ItineraryDay(
                        day=day_counter,
                        theme="Final exploration and departure prep",
                        activities=[
                            "Visit any missed attractions",
                            "Last local meal experience",
                            "Shopping or souvenir hunting",
                            f"Prepare for departure from {city}"
                        ]
                    ))
                elif idx < len(cities) - 1 and day_counter <= duration:
                    # Travel day to next city
                    next_city = cities[idx + 1] if idx + 1 < len(cities) else ""
                    itinerary.append(ItineraryDay(
                        day=day_counter,
                        theme=f"Travel to {next_city}",
                        activities=[
                            "Morning checkout and last activities",
                            f"Travel to {next_city}",
                            "Check in and settle",
                            "Evening exploration"
                        ]
                    ))
                    day_counter += 1
        
        # Validate itinerary doesn't exceed duration
        itinerary_dict = {f"day{i.day}": i.theme for i in itinerary}
        validated_itinerary_dict = validate_itinerary(itinerary_dict, duration)
        
        # Reconstruct itinerary list (only keep validated days)
        validated_days = set(int(k.replace("day", "")) for k in validated_itinerary_dict.keys())
        itinerary = [day for day in itinerary if day.day in validated_days]
        
        return FinalTravelPlan(
            trip_summary=(
                f"A comprehensive {parsed.get('duration_days', 'multi-day')} day travel plan to {parsed.get('destination', 'your destination')} "
                f"focusing on {city_text}. This plan integrates destination highlights, transportation logistics, accommodation recommendations, "
                f"budget planning, weather preparation, and cultural insights for a seamless journey."
            ),
            destination_highlights=destination_output.get("highlights", []),
            accommodation_recommendations=accommodation_output.get("by_city", {}),
            transportation_guide=transportation_output.get("local_transportation", {}),
            estimated_budget=budget_output.get("category_details", {}),
            weather_expectations=weather_output.get("weather_expectations", []),
            packing_suggestions=weather_output.get("packing_suggestions", []),
            cultural_etiquette=culture_output.get("etiquette", []),
            essential_language_phrases=[PhraseItem(**item) for item in culture_output.get("phrases", [])] if culture_output.get("phrases") else [],
            transport_guidance=transportation_output.get("practical_advice", []) + destination_output.get("transport", []),
            safety_notes=destination_output.get("safety", []),
            optional_day_wise_itinerary=itinerary,
            final_travel_tips=(
                destination_output.get("final_tips", []) 
                + weather_output.get("activity_advice", []) 
                + culture_output.get("behavior_tips", [])
                + culture_output.get("etiquette", [])
                + budget_output.get("money_tips", [])
                + transportation_output.get("practical_advice", [])
            ),
            agent_contributions={
                "destination": destination_output.get("summary", ""),
                "transportation": transportation_output.get("summary", ""),
                "accommodation": accommodation_output.get("summary", ""),
                "budget": budget_output.get("summary", ""),
                "weather": weather_output.get("summary", ""),
                "culture": culture_output.get("summary", ""),
            },
            polished_narrative=polished_narrative,  # NEW: Add the polished markdown narrative
        )


coordinator_agent = CoordinatorAgent()
