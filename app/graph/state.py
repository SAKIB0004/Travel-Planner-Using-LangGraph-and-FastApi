from __future__ import annotations

from typing import Any, TypedDict


class TravelGraphState(TypedDict, total=False):
    session_id: str
    user_query: str
    request_payload: dict[str, Any]
    parsed_trip_info: dict[str, Any]
    specialist_outputs: dict[str, dict[str, Any]]
    required_agents: list[str]
    completed_agents: list[str]
    router_reasons: list[str]
    final_plan: dict[str, Any]
    metadata: dict[str, Any]
    tool_failures: list[str]
    errors: list[str]
    needs_itinerary: bool
