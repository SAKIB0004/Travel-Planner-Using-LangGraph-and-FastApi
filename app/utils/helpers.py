from __future__ import annotations

import re
import json
from typing import Any, Iterable
from datetime import datetime, timedelta
from functools import lru_cache


# ===== Simple In-Memory Caching with TTL =====
_cache: dict[str, tuple[Any, float]] = {}
CACHE_TTL_HOURS = 24

def cache_get(key: str) -> Any | None:
    """Get cached value if not expired."""
    if key in _cache:
        value, timestamp = _cache[key]
        if datetime.now().timestamp() - timestamp < CACHE_TTL_HOURS * 3600:
            return value
        else:
            del _cache[key]
    return None

def cache_set(key: str, value: Any) -> None:
    """Store value in cache with timestamp."""
    _cache[key] = (value, datetime.now().timestamp())

def cache_clear() -> None:
    """Clear all cached data."""
    global _cache
    _cache = {}


# ===== Basic Utilities =====

def safe_join(items: Iterable[str], sep: str = ", ") -> str:
    """Join items, filtering out empty/None values."""
    return sep.join([str(item).strip() for item in items if item])


def unique_preserve_order(items: list[str]) -> list[str]:
    """Remove duplicates while preserving order."""
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


# ===== Normalization Helpers =====

def normalize_budget_style(budget_text: str | None) -> str:
    """Normalize budget style to standard format."""
    if not budget_text:
        return "mid-range"
    
    text_lower = str(budget_text).lower().strip()
    
    if any(w in text_lower for w in ["budget", "cheap", "tight", "backpack", "economy"]):
        return "budget"
    elif any(w in text_lower for w in ["luxury", "premium", "exclusive", "high-end"]):
        return "luxury"
    elif any(w in text_lower for w in ["mid", "moderate", "average", "standard", "mid range"]):
        return "mid-range"
    else:
        return "mid-range"  # Default

def normalize_travel_type(travel_text: str | None) -> str:
    """Normalize travel type/style."""
    if not travel_text:
        return "mixed"
    
    text_lower = str(travel_text).lower().strip()
    
    if any(w in text_lower for w in ["budget", "backpack"]):
        return "budget"
    elif any(w in text_lower for w in ["luxury", "premium"]):
        return "luxury"
    elif any(w in text_lower for w in ["culture", "history", "heritage", "immersion"]):
        return "cultural"
    elif any(w in text_lower for w in ["adventure", "outdoor", "active"]):
        return "adventure"
    elif any(w in text_lower for w in ["food", "culinary", "gastro"]):
        return "culinary"
    elif any(w in text_lower for w in ["family", "kid"]):
        return "family"
    elif any(w in text_lower for w in ["solo", "alone"]):
        return "solo"
    else:
        return "mixed"

def detect_traveler_type(user_query: str) -> str:
    """Detect if traveler is solo, couple, family, group, etc."""
    query_lower = (user_query or "").lower()
    
    if any(w in query_lower for w in ["solo", "alone", "myself"]):
        return "solo"
    elif any(w in query_lower for w in ["couple", "partner", "spouse", "girlfriend", "boyfriend"]):
        return "couple"
    elif any(w in query_lower for w in ["family", "kids", "children", "baby"]):
        return "family"
    elif any(w in query_lower for w in ["friend", "group", "team"]):
        return "group"
    else:
        return "unknown"

def is_country_name(name: str) -> bool:
    """Heuristic check if a name is likely a country vs city."""
    # Known countries list (common ones)
    # Note: City-states like Singapore/Hong Kong/Monaco are treated as cities in this context
    countries_heuristic = {
        "japan", "thailand", "vietnam", "india", "france", "italy", "spain", "germany",
        "uk", "united kingdom", "australia", "canada", "usa", "united states", "mexico",
        "brazil", "argentina", "south korea", "korea", "china", "philippines", "indonesia",
        "greece", "turkey", "egypt", "morocco", "new zealand", "portugal", "switzerland",
        "netherlands", "belgium", "sweden", "norway", "finland", "denmark", "poland",
        # "hongkong", "hong kong", "singapore", - treated as cities, not countries
        "malaysia", "cambodia", "laos", "myanmar"
    }
    name_lower = (name or "").lower().strip()
    return name_lower in countries_heuristic

def distinguish_country_from_cities(destination: str | None, cities: list[str]) -> tuple[str | None, list[str]]:
    """
    Separate country name from city list.
    Returns (country, cleaned_cities)
    """
    if not destination:
        dest_country = None
    else:
        dest_country = destination if is_country_name(destination) else None
    
    # Filter cities to remove country names
    cleaned_cities = [c for c in cities if not is_country_name(c)]
    
    return dest_country, cleaned_cities


# ===== Trip Extraction & Normalization =====

def extract_trip_details(user_query: str, payload: dict[str, Any]) -> dict[str, Any]:
    """
    Extract and normalize trip details from user query and payload.
    Fills in missing details intelligently, distinguishes country from cities,
    normalizes budget and travel style, detects traveler type.
    """
    query_lower = (user_query or "").lower()
    
    # Extract destination (from payload or query)
    destination = payload.get("destination")
    if not destination:
        # Try to infer from query: "trip to Japan" → "Japan"
        match = re.search(r"\bto\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", user_query)
        if match:
            destination = match.group(1)
    
    # Extract cities if not provided
    cities = payload.get("cities", [])
    if not cities or (len(cities) == 0):
        # Try to find city names in query (capitalized words)
        # Exclude common words that aren't cities
        common_words = {"trip", "planning", "travel", "plan", "explore", "visit", "vacation", "visiting", "day", "days"}
        potential_cities = re.findall(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b", user_query)
        potential_cities = [c for c in potential_cities if c.lower() not in common_words]
        
        if potential_cities:
            cities = unique_preserve_order(potential_cities[:5])  # Get up to 5
    
    # Distinguish country from cities
    country, cities = distinguish_country_from_cities(destination, cities)
    
    # Determine final destination and cities structure
    # Priority: country > destination > first city
    if country:
        # Country-level trip
        final_destination = country
        final_cities = cities
    elif destination and not is_country_name(destination):
        # Single-city trip (destination is a city)
        final_destination = destination
        final_cities = []  # Don't duplicate as a city
    elif destination and is_country_name(destination):
        # Destination is already a country
        final_destination = destination
        final_cities = cities
    elif cities:
        # Multiple cities provided, use first as primary destination
        final_destination = cities[0]
        final_cities = cities[1:]
    else:
        # No destination or cities provided
        final_destination = None
        final_cities = []
    
    # Limit to 3 cities (avoid generating day allocations for too many places)
    final_cities = final_cities[:3]
    
    # Extract duration
    duration_days = payload.get("duration_days")
    if not duration_days:
        patterns = [
            r"(\d+)[-\s]*days?\b",
            r"\ba\s+(\d+)[-\s]*days?\s+",
            r"(\d+)[-\s]*days?\s+(?:trip|visit|tour)",
        ]
        for pattern in patterns:
            match = re.search(pattern, query_lower)
            if match:
                duration_days = int(match.group(1))
                break
    duration_days = max(1, min(duration_days or 7, 60))  # Clamp between 1-60
    
    # Extract month/season
    travel_month = payload.get("travel_month")
    if not travel_month:
        months = ["january", "february", "march", "april", "may", "june",
                  "july", "august", "september", "october", "november", "december"]
        for month in months:
            if month in query_lower:
                travel_month = month.capitalize()
                break
    
    # Extract and normalize travel style
    travel_style = payload.get("travel_style")
    if not travel_style:
        travel_style = normalize_travel_type(query_lower)
    else:
        travel_style = normalize_travel_type(travel_style)
    
    # Extract and normalize budget level
    budget = payload.get("budget")
    if not budget:
        budget = normalize_budget_style(query_lower)
    else:
        budget = normalize_budget_style(budget)
    
    # Extract interests
    interests = payload.get("interests", [])
    if not interests:
        interest_keywords = {
            "culture": ["culture", "cultural", "heritage", "tradition", "historical"],
            "history": ["history", "historical", "ancient", "monument"],
            "food": ["food", "cuisine", "eat", "restaurant", "culinary", "gastro"],
            "nature": ["nature", "outdoor", "hiking", "national park", "wildlife"],
            "adventure": ["adventure", "extreme", "adrenaline", "active"],
            "nightlife": ["nightlife", "party", "club", "bar", "nightlife"],
            "shopping": ["shopping", "shop", "mall", "boutique"],
            "relaxation": ["relax", "spa", "beach", "resort"],
        }
        for category, keywords in interest_keywords.items():
            if any(kw in query_lower for kw in keywords):
                if category not in interests:
                    interests.append(category)
        if not interests:
            interests = ["culture"]
    
    # Extract language comfort
    language_comfort = payload.get("language_comfort")
    if not language_comfort:
        if "english only" in query_lower or ("only" in query_lower and "english" in query_lower):
            language_comfort = "English only"
        elif "english" in query_lower:
            language_comfort = "English comfortable"
        else:
            language_comfort = "Language comfort unknown"
    
    # Detect traveler type
    traveler_type = detect_traveler_type(user_query)
    
    return {
        "destination": final_destination or "your destination",
        "cities": final_cities or [],
        "country": country,
        "duration_days": duration_days,
        "travel_month": travel_month,
        "travel_style": travel_style,
        "budget": budget,
        "interests": interests,
        "language_comfort": language_comfort,
        "traveler_type": traveler_type,
        "user_query": user_query,
    }


# ===== Output Sanitization & Formatting =====

def sanitize_value(value: Any, fallback: str = "") -> str:
    """Convert value to safe string, handling None, empty, and placeholders."""
    if value is None:
        return fallback
    if isinstance(value, str):
        value = value.strip()
        # Don't render placeholder-like values
        if value.lower() in ["none", "null", "n/a", "destination", "the destination", ""]:
            return fallback
        return value
    if isinstance(value, (list, dict)):
        if not value:
            return fallback
        return str(value)
    return str(value) if value else fallback


def format_list_as_markdown(items: list[str], bullet: str = "-") -> str:
    """Convert list to markdown bullet points."""
    safe_items = [sanitize_value(item) for item in items if sanitize_value(item)]
    if not safe_items:
        return ""
    return "\n".join([f"{bullet} {item}" for item in safe_items])


def format_dict_section(data: dict[str, Any], title: str = "") -> str:
    """Format dictionary as readable markdown section."""
    if not data or all(not v for v in data.values()):
        return ""
    
    lines = []
    if title:
        lines.append(f"## {title}\n")
    
    for key, value in data.items():
        if value is None or (isinstance(value, str) and not value.strip()):
            continue
        
        key_display = key.replace("_", " ").title()
        
        if isinstance(value, list):
            if value:
                lines.append(f"**{key_display}:**")
                lines.append(format_list_as_markdown(value))
                lines.append("")
        elif isinstance(value, dict):
            if value:
                lines.append(f"**{key_display}:**")
                for sub_key, sub_val in value.items():
                    safe_val = sanitize_value(sub_val)
                    if safe_val:
                        sub_display = sub_key.replace("_", " ").title()
                        lines.append(f"  • {sub_display}: {safe_val}")
                lines.append("")
        else:
            safe_val = sanitize_value(value)
            if safe_val:
                lines.append(f"**{key_display}:** {safe_val}")
                lines.append("")
    
    return "\n".join(lines)


def create_polished_response(
    trip_info: dict[str, Any],
    agent_outputs: dict[str, Any],
    include_raw: bool = False
) -> str:
    """
    Create a polished, professional travel plan from agent outputs.
    Matches the style of a high-quality travel guide with:
    - Engaging introduction
    - City-specific recommendations
    - Realistic price ranges
    - Practical, actionable advice
    - Warm, professional tone
    - No placeholders or generic language
    Returns markdown-formatted string ready for display.
    """
    destination = sanitize_value(trip_info.get("destination"), "your destination")
    cities = trip_info.get("cities", [])
    duration = trip_info.get("duration_days", 7)
    month = sanitize_value(trip_info.get("travel_month"), "")
    travel_style = sanitize_value(trip_info.get("travel_style"), "").lower()
    interests = trip_info.get("interests", [])
    budget = sanitize_value(trip_info.get("budget"), "mid-range").lower()
    
    # Ensure cities is a list
    if isinstance(cities, str):
        cities = [cities]
    cities = [c for c in cities if c and c.lower() not in ["destination", "plan"]][:3]
    
    # Build main heading
    response = "# ✨ Your Travel Plan\n\n"
    
    # Trip title
    trip_type = ""
    if interests:
        if any(x in interests for x in ["culture", "history"]):
            trip_type = "Cultural"
        elif any(x in interests for x in ["adventure", "nature"]):
            trip_type = "Adventure"
        elif any(x in interests for x in ["food", "cuisine"]):
            trip_type = "Culinary"
        elif any(x in interests for x in ["nightlife", "party"]):
            trip_type = "Urban"
    if not trip_type:
        trip_type = travel_style.title() if travel_style else "Immersive"
    
    cities_text = " + ".join(cities) if cities else destination
    response += f"## {duration}-Day {trip_type} Trip to {destination}: {cities_text}\n\n"
    
    # Opening narrative
    dest_summary = sanitize_value(agent_outputs.get("destination", {}).get("summary"), "")
    accom_summary = sanitize_value(agent_outputs.get("accommodation", {}).get("summary"), "")
    
    if isinstance(interests, list) and interests:
        interests_text = ", ".join(interests[:3])
    else:
        interests_text = "cultural and historical experiences"
    
    response += f"This {duration}-day trip is designed for "
    if travel_style and travel_style != "mixed":
        response += f"a {travel_style} traveler "
    else:
        response += f"a first-time visitor "
    response += f"who wants {interests_text}. "
    
    if len(cities) > 1:
        response += f"{cities[0]} offers {"diverse experiences spanning culture, history, and urban exploration" if not dest_summary else "a range of traditional and contemporary attractions"}, "
        response += f"while {cities[1]} {'complements this with a more local, approachable feel' if len(cities) > 1 else 'further deepens the journey'}."
    else:
        response += f"{cities[0] if cities else destination} is ideal for exploring {'traditional areas and cultural heritage' if interests_text != 'cultural and historical experiences' else interests_text}."
    response += "\n\n"
    
    # Why these destinations fit
    response += "## Why These Destinations Fit Your Trip\n\n"
    if len(cities) >= 1:
        response += f"{cities[0]} is ideal for exploring traditional areas, museums, and neighborhood walks that showcase local culture and history. "
        if len(cities) > 1:
            response += f"{cities[1]} complements this with a more local and approachable city feel, strong street-food culture, and convenient access to heritage-rich day trips or nearby destinations if you want to deepen the cultural side of your journey."
    else:
        response += f"{destination} offers a balanced mix of traditional heritage sites, museums, and modern neighborhoods that are perfect for first-time visitors interested in cultural immersion."
    response += "\n\n"
    
    # Flight Guidance
    response += "## Flight Guidance\n\n"
    trans_data = agent_outputs.get("transportation", {})
    flights_text = sanitize_value(trans_data.get("international_flights", ""), "Check major flight booking sites for current pricing")
    
    # Try to extract price range if available
    price_pattern = r"\$\d+[\d,]*(?:\s*-\s*\$?\d+[\d,]*)?"
    price_matches = re.findall(price_pattern, flights_text)
    if price_matches:
        response += f"For a {budget} {month if month else "mid-season"} trip, round-trip international fares will usually fall in an estimated range of {price_matches[0]}, depending on your departure city and how early you book.\n\n"
    else:
        # Provide reasonable estimates based on budget
        if budget == "budget":
            response += "For a budget trip, round-trip international fares typically range from **$500–$800**, depending on your departure city and how early you book.\n\n"
        elif budget == "luxury":
            response += "For a luxury trip, round-trip international fares typically range from **$1,200–$1,800+**, with options for premium airlines and services.\n\n"
        else:
            response += "For a mid-range trip, round-trip international fares typically range from **$650–$1,050**, depending on your departure city and how early you book.\n\n"
    
    response += "Booking tips:\n"
    response += "- book 6–8 weeks in advance if possible\n"
    response += "- compare Google Flights and Skyscanner\n"
    if len(cities) > 1:
        response += f"- consider arriving in {cities[0]} and departing from {cities[-1]} to reduce backtracking\n"
    response += "- mid-week departures are often slightly cheaper than weekend departures\n\n"
    
    # Accommodation Recommendations
    response += "## Accommodation Recommendations\n\n"
    accom_data = agent_outputs.get("accommodation", {})
    by_city = accom_data.get("by_city", {})
    
    for city in cities:
        response += f"### {city}\n"
        city_data = by_city.get(city, {})
        
        neighborhoods = None
        if isinstance(city_data, dict):
            neighborhoods = city_data.get("recommended_neighborhoods") or city_data.get("neighborhoods")
        
        # Add neighborhood recommendations with descriptions
        response += "Recommended areas:\n"
        if neighborhoods:
            if isinstance(neighborhoods, list):
                for idx, hood in enumerate(neighborhoods[:3]):
                    if isinstance(hood, dict):
                        name = hood.get("name", "")
                        desc = hood.get("description", hood.get("description", ""))
                        response += f"- **{name}**: {desc}\n"
                    else:
                        response += f"- {hood}\n"
            else:
                response += f"- {neighborhoods}\n"
        else:
            response += f"- Central business districts with easy transport access\n"
            response += f"- Neighborhood areas with local character\n"
            response += f"- Budget-friendly residential areas\n"
        response += "\n"
        
        # Add pricing
        if isinstance(city_data, dict):
            price_min = city_data.get("min_price", "80")
            price_max = city_data.get("max_price", "160")
            # Clean up prices
            if isinstance(price_min, str):
                price_min = re.sub(r"[^0-9]", "", price_min) or "80"
            if isinstance(price_max, str):
                price_max = re.sub(r"[^0-9]", "", price_max) or "160"
            response += f"Typical {budget} stay: **${price_min}–${price_max} per night**\n\n"
        else:
            response += f"Typical {budget} stay: **$80–$160 per night**\n\n"
    
    # Transportation Guide
    response += "## Transportation Guide\n\n"
    local_trans = trans_data.get("local_transportation", "")
    
    if local_trans:
        if isinstance(local_trans, dict):
            response += f"For local transport, {destination} has "
            systems = local_trans.get("options") or local_trans.get("transit_systems")
            if systems:
                if isinstance(systems, list):
                    response += f"{', '.join(systems[:2])} systems.\n\n"
                else:
                    response += f"{systems}.\n\n"
            else:
                response += "efficient public transportation.\n\n"
        else:
            response += f"{local_trans}\n\n"
    else:
        response += f"For local transport, {destination} is very convenient for first-time visitors with a well-connected transit system.\n\n"
    
    response += "Practical transport notes:\n"
    response += "- use metro and main transit lines for daily city travel\n"
    if len(cities) > 1:
        response += f"- efficient transportation connects {' and '.join(cities[:2])}\n"
    response += "- stay near major stations to reduce transfers\n"
    response += "- keep Google Maps downloaded for backup navigation\n\n"
    
    daily_cost = trans_data.get("daily_cost", "15")
    if isinstance(daily_cost, str):
        daily_cost = re.sub(r"[^0-9]", "", daily_cost) or "15"
    response += f"Estimated local transport budget: **${daily_cost}–$25 per day**, excluding long-distance train tickets.\n\n"
    
    # Budget Breakdown
    response += "## Estimated Budget Breakdown\n\n"
    budget_data = agent_outputs.get("budget", {})
    
    # Calculate reasonable daily ranges based on budget level
    if budget == "budget":
        daily_min, daily_max = 50, 80
        trip_min = daily_min * duration
        trip_max = daily_max * duration
        daily_range_text = f"${daily_min}–${daily_max}"
    elif budget == "luxury":
        daily_min, daily_max = 180, 300
        trip_min = daily_min * duration
        trip_max = daily_max * duration
        daily_range_text = f"${daily_min}–${daily_max}"
    else:  # mid-range
        daily_min, daily_max = 80, 150
        trip_min = daily_min * duration
        trip_max = daily_max * duration
        daily_range_text = f"${daily_min}–${daily_max}"
    
    response += f"A realistic {budget} estimate for {duration} days is around **${trip_min}–${trip_max} excluding shopping**, plus international flights.\n\n"
    response += "Typical daily budget:\n"
    response += f"- Accommodation: **${daily_min - 60}–${daily_max - 60}**\n"
    response += "- Food: **$30–$60**\n"
    response += "- Local transport: **$10–$20**\n"
    response += "- Attractions: **$15–$40**\n\n"
    
    # Weather Expectations
    response += "## Weather Expectations\n\n"
    weather_data = agent_outputs.get("weather", {})
    weather_summary = sanitize_value(weather_data.get("summary", ""), "")
    
    if month:
        response += f"{month} is one of the most comfortable months to visit {destination}. "
    response += weather_summary if weather_summary else "Expect mild temperatures, comfortable walking weather, and generally pleasant conditions. Check specific forecasts closer to your travel dates.\n\n"
    response += "\n"
    
    # Packing Tips
    response += "## Packing Tips\n\n"
    response += "Bring:\n"
    packing_suggestions = weather_data.get("packing_suggestions", [])
    if packing_suggestions:
        response += format_list_as_markdown(packing_suggestions)
    else:
        response += "- light layers\n"
        response += "- comfortable walking shoes\n"
        response += "- a compact umbrella or rain jacket\n"
        response += "- a small day bag for long walking days\n"
        response += "- universal power adapter\n"
    response += "\n"
    
    # Cultural Etiquette
    response += "## Cultural Etiquette\n\n"
    culture_data = agent_outputs.get("culture", {})
    etiquette = culture_data.get("etiquette") or culture_data.get("cultural_etiquette", [])
    if etiquette:
        response += format_list_as_markdown(etiquette)
    else:
        response += "- be respectful in temples and sacred spaces\n"
        response += "- maintain quiet on public transport\n"
        response += "- follow local customs in dining and social situations\n"
        response += "- tip only when explicitly indicated\n"
    response += "\n"
    
    # Essential Language Phrases
    response += "## Essential Language Phrases\n\n"
    phrases = culture_data.get("essential_language_phrases") or culture_data.get("phrases", [])
    if phrases and isinstance(phrases, list) and len(phrases) > 0:
        for phrase_item in phrases[:6]:
            if isinstance(phrase_item, dict):
                phrase = sanitize_value(phrase_item.get("phrase"), "")
                meaning = sanitize_value(phrase_item.get("meaning"), "")
                if phrase and meaning:
                    response += f"- **{phrase}** — {meaning}\n"
    else:
        response += f"- Key phrases for {destination} visitors\n"
        response += "- Consider downloading a translation app as backup\n"
    response += "\n"
    
    # Day-wise Itinerary (optional)
    if len(cities) > 0:
        response += "## Optional Day-wise Itinerary\n\n"
        days_per_city = max(1, duration // len(cities))
        day_counter = 1
        
        for city in cities:
            num_cities = len(cities)
            day_start = day_counter
            day_end = day_counter + days_per_city - 1
            
            response += f"### Days {day_start}–{day_end}: {city}\n"
            response += f"- Explore main attractions and cultural sites\n"
            response += f"- Spend time in different neighborhoods\n"
            response += f"- Try local food and street food culture\n"
            if city == cities[-1] and num_cities > 1:
                response += f"- Consider a day trip to nearby heritage sites\n"
            response += "\n"
            day_counter += days_per_city
    
    # Final Travel Tips
    response += "## Final Travel Tips\n\n"
    response += "- start temple and museum visits early for a quieter experience\n"
    response += "- cluster attractions by area instead of crossing the city repeatedly\n"
    response += "- leave some unscheduled time for neighborhood walks and discoveries\n"
    response += "- notify your bank before traveling\n"
    response += f"- have a wonderful trip to {destination}!\n"
    
    return response


# ===== Validation & Verification Helpers =====

def validate_itinerary(itinerary: dict[str, Any], duration_days: int) -> dict[str, Any]:
    """
    Validate and fix itinerary to ensure day allocations don't exceed total trip duration.
    Redistributes days proportionally if needed.
    
    Args:
        itinerary: Dict with keys like "day1", "day2", etc.
        duration_days: Total trip duration in days
    
    Returns:
        Corrected itinerary dict with day count matching duration
    """
    if not itinerary or not isinstance(itinerary, dict):
        return itinerary
    
    total_days_allocated = sum(1 for day_key in itinerary.keys() if day_key.startswith("day"))
    
    # If itinerary days exceed trip duration, compress proportionally
    if total_days_allocated > duration_days and total_days_allocated > 0:
        fix_ratio = duration_days / total_days_allocated
        new_itinerary = {}
        for day_num in range(1, duration_days + 1):
            old_day_num = max(1, int(day_num / fix_ratio))
            old_key = f"day{old_day_num}"
            if old_key in itinerary:
                new_itinerary[f"day{day_num}"] = itinerary[old_key]
            else:
                new_itinerary[f"day{day_num}"] = itinerary.get("day1", "Explore your destination")
        return new_itinerary
    
    return itinerary


def resolve_destination(
    destination: str | None,
    cities: list[str],
    country: str | None = None
) -> tuple[str | None, list[str]]:
    """
    Resolve final destination and city list for output.
    
    Args:
        destination: Primary destination from request
        cities: List of specific cities
        country: Extracted country name (if known)
    
    Returns:
        (primary_destination, cities_list) tuple
        
    Logic:
    - If country is known, use it as primary destination
    - Otherwise use first city if available
    - Return remaining cities as secondary list
    """
    if country:
        # Country-level trip: all cities are secondary
        return country, cities
    
    if not destination and not cities:
        return None, []
    
    if destination and not cities:
        return destination, []
    
    if not destination and cities:
        # If only cities provided, use first as primary
        if len(cities) > 0:
            return cities[0], cities[1:]
        return None, []
    
    # Both destination and cities exist
    # If destination looks like a country, use it; otherwise it's a city
    if is_country_name(destination):
        return destination, cities
    else:
        # Destination is really a city
        return (cities[0] if cities else destination), (cities[1:] or [destination])


def detect_placeholder_text(text: str) -> bool:
    """
    Detect if text is a placeholder or auto-generated generic content.
    
    Args:
        text: Text to check
    
    Returns:
        True if text appears to be placeholder/generic
    """
    if not text:
        return True
    
    text_lower = text.lower().strip()
    placeholder_indicators = [
        "explore your destination",
        "based on your itinerary",
        "enjoy the beauty",
        "relax and enjoy",
        "visit the local",
        "experience the culture",
        "to be determined",
        "tbd",
        "[placeholder]",
        "[auto-generated]",
        "we recommend",
        "you may want to",
    ]
    
    return any(indicator in text_lower for indicator in placeholder_indicators)


def estimate_city_days(cities: list[str], total_days: int) -> dict[str, int]:
    """
    Estimate reasonable day allocation for multiple cities.
    Uses heuristic: more days for larger cities, minimum 1 day per city.
    
    Args:
        cities: List of city names
        total_days: Total trip duration
    
    Returns:
        Dict mapping city name to recommended days
    """
    if not cities:
        return {}
    
    num_cities = len(cities)
    
    # Reserve travel time (at least 1 day per city transition)
    travel_days = max(1, num_cities - 1)
    
    # Available days for visiting cities
    available_days = max(num_cities, total_days - travel_days)
    
    # Distribute: give each city at least 1 day, then distribute remainder
    base_days_per_city = available_days // num_cities
    remainder = available_days % num_cities
    
    allocation = {}
    for i, city in enumerate(cities):
        days = base_days_per_city + (1 if i < remainder else 0)
        allocation[city] = max(1, days)
    
    return allocation

