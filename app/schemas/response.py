from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PhraseItem(BaseModel):
    phrase: str
    meaning: str
    usage_context: str


class ItineraryDay(BaseModel):
    day: int
    theme: str
    activities: list[str] = Field(default_factory=list)


class FinalTravelPlan(BaseModel):
    trip_summary: str
    destination_highlights: list[str] = Field(default_factory=list)
    accommodation_recommendations: dict[str, Any] = Field(default_factory=dict)
    transportation_guide: dict[str, Any] = Field(default_factory=dict)
    estimated_budget: dict[str, Any] = Field(default_factory=dict)
    weather_expectations: list[str] = Field(default_factory=list)
    packing_suggestions: list[str] = Field(default_factory=list)
    cultural_etiquette: list[str] = Field(default_factory=list)
    essential_language_phrases: list[PhraseItem] = Field(default_factory=list)
    transport_guidance: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)
    optional_day_wise_itinerary: list[ItineraryDay] = Field(default_factory=list)
    final_travel_tips: list[str] = Field(default_factory=list)
    agent_contributions: dict[str, str] = Field(default_factory=dict)
    polished_narrative: str = Field(default="", description="Polished markdown-formatted travel narrative combining all agent outputs")


class TripPlanningResponse(BaseModel):
    session_id: str
    parsed_trip_info: dict[str, Any] = Field(default_factory=dict)
    called_agents: list[str] = Field(default_factory=list)
    router_reasons: list[str] = Field(default_factory=list)
    tool_failures: list[str] = Field(default_factory=list)
    final_plan: FinalTravelPlan


class ApiResponse(BaseModel):
    success: bool
    message: str
    data: TripPlanningResponse
