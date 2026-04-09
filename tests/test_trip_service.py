from __future__ import annotations

import pytest

from app.schemas.request import TripPlanningRequest
from app.services.trip_service import TripService


@pytest.mark.asyncio
async def test_simple_trip_scenario(monkeypatch):
    monkeypatch.setenv("USE_MOCK_LLM", "true")
    monkeypatch.setenv("USE_MOCK_WEATHER", "true")
    service = TripService()
    payload = TripPlanningRequest(
        session_id="s1",
        user_query="Plan a 5-day first trip to Japan with highlights in Tokyo.",
        destination="Japan",
        cities=["Tokyo"],
        duration_days=5,
        interests=["culture"],
        language_comfort="English",
    )
    result = await service.plan_trip(payload)
    assert result.session_id == "s1"
    assert "destination" in result.called_agents
    assert result.final_plan.destination_highlights


@pytest.mark.asyncio
async def test_complex_multi_city_scenario(monkeypatch):
    monkeypatch.setenv("USE_MOCK_LLM", "true")
    monkeypatch.setenv("USE_MOCK_WEATHER", "true")
    service = TripService()
    payload = TripPlanningRequest(
        session_id="s2",
        user_query="I need weather, culture, and transport help for a 14-day Japan trip across Tokyo and Osaka.",
        destination="Japan",
        cities=["Tokyo", "Osaka"],
        duration_days=14,
        interests=["culture", "history"],
        travel_month="October",
        language_comfort="English only",
        special_preferences=["traditional culture", "historical places"],
    )
    result = await service.plan_trip(payload)
    assert set(result.called_agents) >= {"destination", "weather", "culture"}
    assert result.final_plan.optional_day_wise_itinerary


@pytest.mark.asyncio
async def test_missing_information_scenario(monkeypatch):
    monkeypatch.setenv("USE_MOCK_LLM", "true")
    monkeypatch.setenv("USE_MOCK_WEATHER", "true")
    service = TripService()
    payload = TripPlanningRequest(
        session_id="s3",
        user_query="Plan me a relaxing cultural trip.",
        destination="Japan",
    )
    result = await service.plan_trip(payload)
    assert "duration_days" in result.parsed_trip_info.get("missing_details", [])


@pytest.mark.asyncio
async def test_tool_failure_fallback_scenario(monkeypatch):
    monkeypatch.setenv("USE_MOCK_LLM", "true")
    monkeypatch.setenv("USE_MOCK_WEATHER", "false")

    from app.tools.weather_tools import WeatherToolService
    from app.agents.weather_agent import WeatherPlanningAgent

    async def broken_weather(*args, **kwargs):
        return {
            "summary": "Fallback weather guidance still available.",
            "packing": ["light jacket"],
            "activity_advice": ["Carry an umbrella"],
            "fallback_reason": "Injected test failure",
        }

    monkeypatch.setattr(WeatherToolService, "get_weather_guidance", broken_weather)
    service = TripService()
    payload = TripPlanningRequest(
        session_id="s4",
        user_query="Need a Japan packing and weather guide.",
        destination="Japan",
        duration_days=7,
        travel_month="October",
    )
    result = await service.plan_trip(payload)
    assert any("weather_fallback_used" in item for item in result.tool_failures)
    assert result.final_plan.packing_suggestions
