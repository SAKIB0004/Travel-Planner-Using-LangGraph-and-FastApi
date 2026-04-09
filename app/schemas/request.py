from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class TripPlanningRequest(BaseModel):
    session_id: str = Field(..., min_length=2, max_length=100)
    user_query: str = Field(..., min_length=10, max_length=2000)
    destination: str | None = Field(default=None, max_length=120)
    cities: list[str] = Field(default_factory=list)
    duration_days: int | None = Field(default=None, ge=1, le=60)
    travel_style: Literal["budget", "mid-range", "luxury", "family", "solo", "cultural", "adventure", "mixed"] | None = None
    interests: list[str] = Field(default_factory=list)
    budget: Literal["budget", "mid-range", "luxury"] | None = None
    season: str | None = None
    travel_month: str | None = None
    language_comfort: str | None = None
    food_preferences: list[str] = Field(default_factory=list)
    special_preferences: list[str] = Field(default_factory=list)
    needs_day_wise_itinerary: bool = True

    @field_validator("cities", "interests", "food_preferences", "special_preferences", mode="before")
    @classmethod
    def strip_list_items(cls, value):
        if value is None:
            return []
        if isinstance(value, str):
            return [value.strip()] if value.strip() else []
        return [str(item).strip() for item in value if str(item).strip()]
