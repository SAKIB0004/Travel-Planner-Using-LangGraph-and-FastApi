from __future__ import annotations

from typing import Any

from app.utils.helpers import unique_preserve_order



def merge_trip_context(request_data: dict[str, Any], memory_data: dict[str, Any]) -> dict[str, Any]:
    merged = {**memory_data, **{k: v for k, v in request_data.items() if v not in (None, [], "")}}
    merged["cities"] = unique_preserve_order(memory_data.get("cities", []) + request_data.get("cities", []))
    merged["interests"] = unique_preserve_order(memory_data.get("interests", []) + request_data.get("interests", []))
    merged["food_preferences"] = unique_preserve_order(memory_data.get("food_preferences", []) + request_data.get("food_preferences", []))
    merged["special_preferences"] = unique_preserve_order(memory_data.get("special_preferences", []) + request_data.get("special_preferences", []))
    return merged
