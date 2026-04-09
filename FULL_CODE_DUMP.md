# Full Project Code Dump

## `.env.example`

```text
APP_NAME=Travel Planner API
APP_ENV=dev
APP_HOST=0.0.0.0
APP_PORT=8000
LOG_LEVEL=INFO
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-20b
USE_MOCK_LLM=true
USE_MOCK_WEATHER=true
OPEN_METEO_BASE_URL=https://api.open-meteo.com/v1/forecast
DEFAULT_SESSION_TTL_MINUTES=120
SEARCH_PROVIDER=duckduckgo
ENABLE_WIKIPEDIA_TOOL=true
ENABLE_SEARCH_TOOL=true
STREAMLIT_API_URL=http://localhost:8000/api/v1/travel/plan

```

## `.pytest_cache/.gitignore`

```
# Created by pytest automatically.
*

```

## `.pytest_cache/CACHEDIR.TAG`

```
Signature: 8a477f597d28d172789f06886806bc55
# This file is a cache directory tag created by pytest.
# For information about cache directory tags, see:
#	https://bford.info/cachedir/spec.html

```

## `.pytest_cache/README.md`

```markdown
# pytest cache directory #

This directory contains data from the pytest's cache plugin,
which provides the `--lf` and `--ff` options, as well as the `cache` fixture.

**Do not** commit this to version control.

See [the docs](https://docs.pytest.org/en/stable/how-to/cache.html) for more information.

```

## `.pytest_cache/v/cache/lastfailed`

```
{
  "tests/test_trip_service.py": true
}
```

## `.pytest_cache/v/cache/nodeids`

```
[]
```

## `README.md`

```markdown
# Multi-Agent Travel Planner

A production-minded, modular AI travel planning system built with **Python**, **LangChain**, **LangGraph**, **Groq**, **FastAPI**, **Pydantic**, and **Streamlit**.

It uses a **coordinator agent** plus **specialist agents** to build structured travel plans instead of relying on one monolithic prompt.

---

## Overview

This project implements a graph-based multi-agent travel planner where a coordinator agent:
- receives the travel request
- extracts structured trip context
- decides which specialist agents are needed
- delegates focused work
- synthesizes the final answer into one user-friendly travel plan

Example use case:
> “I’m planning a 2-week cultural immersion trip to Japan (Tokyo and Osaka) as a first-time visitor. I want traditional culture, historical places, weather guidance, and language/cultural tips. I only speak English.”

---

## Why LangGraph?

**LangGraph** is used because the workflow is not a single linear chain.
The system needs:
- stateful orchestration
- dynamic routing
- conditional specialist execution
- graph-style synthesis after multiple agent branches

This makes LangGraph a better fit than a single prompt chain or a simple agent executor.

---

## Architecture

### Agents

#### 1. Travel Coordinator Agent
Responsible for:
- parsing trip requirements
- deciding which specialists are needed
- managing graph state
- synthesizing final output

#### 2. Destination Research Agent
Responsible for:
- attractions
- cultural and historical highlights
- transport basics
- safety notes
- destination logistics

#### 3. Weather Planning Agent
Responsible for:
- seasonal expectations
- clothing and packing
- weather-aware activity planning

#### 4. Language & Culture Agent
Responsible for:
- etiquette
- dining and tipping behavior
- social norms
- local phrases
- communication tips

### Graph Flow

```text
input -> router -> destination/weather/culture -> synthesis -> final response
```

The router dynamically decides which specialist agents are necessary based on user intent and structured trip info.

---

## Folder Structure

```text
travel-planner/
├── app/
│   ├── main.py
│   ├── api/
│   │   └── routes_travel.py
│   ├── config/
│   │   └── settings.py
│   ├── schemas/
│   │   ├── request.py
│   │   └── response.py
│   ├── graph/
│   │   ├── state.py
│   │   ├── builder.py
│   │   ├── router.py
│   │   └── nodes.py
│   ├── agents/
│   │   ├── coordinator.py
│   │   ├── destination_agent.py
│   │   ├── weather_agent.py
│   │   └── culture_agent.py
│   ├── prompts/
│   │   ├── coordinator_prompt.py
│   │   ├── destination_prompt.py
│   │   ├── weather_prompt.py
│   │   └── culture_prompt.py
│   ├── tools/
│   │   ├── search_tools.py
│   │   ├── weather_tools.py
│   │   └── helper_tools.py
│   ├── services/
│   │   └── trip_service.py
│   ├── utils/
│   │   ├── logger.py
│   │   └── helpers.py
│   └── memory/
│       └── session_memory.py
├── tests/
│   └── test_trip_service.py
├── .env.example
├── requirements.txt
├── README.md
├── run.py
└── streamlit_app.py
```

---

## Environment Variables

Copy `.env.example` into `.env` and update values.

```env
APP_NAME=Travel Planner API
APP_ENV=dev
APP_HOST=0.0.0.0
APP_PORT=8000
LOG_LEVEL=INFO
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-20b
USE_MOCK_LLM=true
USE_MOCK_WEATHER=true
OPEN_METEO_BASE_URL=https://api.open-meteo.com/v1/forecast
DEFAULT_SESSION_TTL_MINUTES=120
SEARCH_PROVIDER=duckduckgo
ENABLE_WIKIPEDIA_TOOL=true
ENABLE_SEARCH_TOOL=true
STREAMLIT_API_URL=http://localhost:8000/api/v1/travel/plan
```

### Notes
- Set `USE_MOCK_LLM=false` to use **Groq** via `ChatGroq`.
- Set `USE_MOCK_WEATHER=false` when wiring a real weather service.
- The project still works in mock mode for local demos, testing, and portfolio use.

---

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
# Windows: .venv\Scriptsctivate

pip install -r requirements.txt
cp .env.example .env
```

---

## Run the API

```bash
python run.py
```

Or directly:

```bash
uvicorn app.main:app --reload
```

API docs will be available at:
- `http://localhost:8000/docs`

---

## Run the Streamlit Frontend

```bash
streamlit run streamlit_app.py
```

---

## Example API Request

```json
{
  "session_id": "demo-session",
  "user_query": "I’m planning a 2-week cultural immersion trip to Japan (Tokyo and Osaka) as a first-time visitor. I want traditional culture, historical places, weather guidance, and language/cultural tips. I only speak English.",
  "destination": "Japan",
  "cities": ["Tokyo", "Osaka"],
  "duration_days": 14,
  "travel_style": "cultural",
  "interests": ["culture", "history"],
  "budget": "mid-range",
  "travel_month": "October",
  "language_comfort": "English only",
  "special_preferences": ["traditional culture", "historical places"]
}
```

---

## Example API Response Shape

```json
{
  "success": true,
  "message": "Travel plan created successfully.",
  "data": {
    "session_id": "demo-session",
    "parsed_trip_info": {},
    "called_agents": ["destination", "weather", "culture"],
    "router_reasons": [],
    "tool_failures": [],
    "final_plan": {
      "trip_summary": "...",
      "destination_highlights": ["..."],
      "weather_expectations": ["..."],
      "packing_suggestions": ["..."],
      "cultural_etiquette": ["..."],
      "essential_language_phrases": [
        {
          "phrase": "...",
          "meaning": "...",
          "usage_context": "..."
        }
      ],
      "transport_guidance": ["..."],
      "safety_notes": ["..."],
      "optional_day_wise_itinerary": [],
      "final_travel_tips": ["..."],
      "agent_contributions": {}
    }
  }
}
```

---

## Testing

This project includes four scenarios:
- simple trip scenario
- complex multi-city scenario
- missing-information scenario
- tool failure / fallback scenario

Run tests with:

```bash
pytest -q
```

---

## Design Choices

### Structured output
Pydantic models are used for:
- request validation
- final response validation
- clean serialization for API clients

### Memory
A simple session memory layer stores repeat preferences such as:
- budget
- language comfort
- cities
- interests
- special preferences

### Logging
Structured JSON logging is enabled with `structlog` to make debugging and orchestration tracing easier.

### Fallback strategy
The app is designed to degrade gracefully:
- search tool failures are captured in `tool_failures`
- weather service failures fall back to mock seasonal guidance
- full mock mode supports local development without paid API calls

---

## Future Improvements

- real weather provider integration
- Tavily or SerpAPI support for richer travel search
- hotel and flight planning specialists
- visa and entry requirement specialist
- persistent memory with Redis or PostgreSQL
- authentication and user profiles
- observability with LangSmith or OpenTelemetry
- itinerary optimization based on travel time between neighborhoods

---

## Portfolio Value

This project is useful for:
- internship portfolios
- junior AI engineer roles
- GenAI / agentic AI demos
- showcasing LangGraph orchestration beyond basic chatbots

It demonstrates:
- modular Python architecture
- agent decomposition
- graph-based orchestration
- structured APIs
- production-style configuration and logging

---

## License

Add your preferred license here, such as MIT.

```

## `app/__init__.py`

```python

```

## `app/agents/__init__.py`

```python

```

## `app/agents/coordinator.py`

```python
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.config.settings import get_settings
from app.prompts.coordinator_prompt import COORDINATOR_PARSE_PROMPT, COORDINATOR_SYNTHESIS_PROMPT
from app.schemas.response import FinalTravelPlan, ItineraryDay, PhraseItem
from app.utils.logger import get_logger

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

        structured_llm = self._llm.with_structured_output(ParsedTripInfo)
        user_query = payload.get("user_query", "")
        prompt = (
            f"{COORDINATOR_PARSE_PROMPT}\n\n"
            f"Input payload:\n{payload}\n\n"
            f"User query:\n{user_query}"
        )
        result = await structured_llm.ainvoke(prompt)
        return result

    async def synthesize(self, state: dict[str, Any]) -> FinalTravelPlan:
        logger.info("coordinator_synthesis_started")
        if settings.use_mock_llm:
            return self._heuristic_synthesis(state)

        structured_llm = self._llm.with_structured_output(FinalTravelPlan)
        prompt = (
            f"{COORDINATOR_SYNTHESIS_PROMPT}\n\n"
            f"Parsed trip info:\n{state['parsed_trip_info']}\n\n"
            f"Destination output:\n{state['specialist_outputs'].get('destination', {})}\n\n"
            f"Weather output:\n{state['specialist_outputs'].get('weather', {})}\n\n"
            f"Culture output:\n{state['specialist_outputs'].get('culture', {})}"
        )
        return await structured_llm.ainvoke(prompt)

    def _heuristic_parse(self, payload: dict[str, Any]) -> ParsedTripInfo:
        missing = []
        if not payload.get("destination"):
            missing.append("destination")
        if not payload.get("duration_days"):
            missing.append("duration_days")
        return ParsedTripInfo(
            destination=payload.get("destination"),
            cities=payload.get("cities", []),
            duration_days=payload.get("duration_days"),
            travel_style=payload.get("travel_style"),
            interests=payload.get("interests", []),
            budget=payload.get("budget"),
            season=payload.get("season"),
            travel_month=payload.get("travel_month"),
            language_comfort=payload.get("language_comfort"),
            special_preferences=payload.get("special_preferences", []),
            missing_details=missing,
        )

    def _heuristic_synthesis(self, state: dict[str, Any]) -> FinalTravelPlan:
        parsed = state["parsed_trip_info"]
        destination_output = state["specialist_outputs"].get("destination", {})
        weather_output = state["specialist_outputs"].get("weather", {})
        culture_output = state["specialist_outputs"].get("culture", {})
        cities = parsed.get("cities", [])
        city_text = ", ".join(cities) if cities else parsed.get("destination", "your destination")
        itinerary = []
        if state.get("needs_itinerary"):
            itinerary = [
                ItineraryDay(day=1, theme="Arrival and neighborhood orientation", activities=["Check in and rest", f"Evening walk around {cities[0] if cities else city_text}", "Early dinner near hotel"]),
                ItineraryDay(day=2, theme="Core cultural highlights", activities=destination_output.get("sample_day", ["Visit a historic district", "Try a traditional meal", "Use transit for city exploration"])),
                ItineraryDay(day=3, theme="Flexible local immersion", activities=["Museum or temple visit", "Local market stop", "Relaxed evening in a quiet area"]),
            ]
        return FinalTravelPlan(
            trip_summary=(
                f"This plan is designed for a {parsed.get('duration_days', 'multi-day')} day trip to {parsed.get('destination', 'the destination')} "
                f"with focus areas around {city_text}. It combines logistics, local culture, weather readiness, and practical first-time visitor advice."
            ),
            destination_highlights=destination_output.get("highlights", []),
            weather_expectations=weather_output.get("weather_expectations", []),
            packing_suggestions=weather_output.get("packing_suggestions", []),
            cultural_etiquette=culture_output.get("etiquette", []),
            essential_language_phrases=[PhraseItem(**item) for item in culture_output.get("phrases", [])],
            transport_guidance=destination_output.get("transport", []),
            safety_notes=destination_output.get("safety", []),
            optional_day_wise_itinerary=itinerary,
            final_travel_tips=destination_output.get("final_tips", []) + weather_output.get("activity_advice", []) + culture_output.get("behavior_tips", []),
            agent_contributions={
                "destination": destination_output.get("summary", ""),
                "weather": weather_output.get("summary", ""),
                "culture": culture_output.get("summary", ""),
            },
        )


coordinator_agent = CoordinatorAgent()

```

## `app/agents/culture_agent.py`

```python
from __future__ import annotations

from typing import Any

from app.config.settings import get_settings
from app.prompts.culture_prompt import CULTURE_PROMPT
from app.tools.search_tools import search_service
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class CultureAgent:
    def __init__(self) -> None:
        self._llm = None
        if not settings.use_mock_llm:
            from langchain_groq import ChatGroq
            self._llm = ChatGroq(model=settings.groq_model, api_key=settings.groq_api_key, temperature=0.2)

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        parsed = state["parsed_trip_info"]
        destination = parsed.get("destination") or "destination"
        snippets = []
        query = f"etiquette language phrases tipping dining customs in {destination} for English-speaking travelers"
        try:
            snippets.append(search_service.search(query))
        except Exception as exc:  # noqa: BLE001
            state["tool_failures"].append(f"culture_search_failed: {exc}")

        if settings.use_mock_llm:
            return self._heuristic_output(destination, snippets)

        prompt = (
            f"{CULTURE_PROMPT}\n\n"
            f"Parsed trip info: {parsed}\n\n"
            f"Research snippets: {snippets}"
        )
        message = await self._llm.ainvoke(prompt)
        return self._heuristic_output(destination, snippets, llm_text=message.content)

    def _heuristic_output(self, destination: str, snippets: list[str], llm_text: str | None = None) -> dict[str, Any]:
        phrases = [
            {"phrase": "Sumimasen", "meaning": "Excuse me / sorry", "usage_context": "Getting attention politely or passing through"},
            {"phrase": "Arigatou gozaimasu", "meaning": "Thank you", "usage_context": "Shops, restaurants, daily politeness"},
            {"phrase": "Eigo wa hanasemasu ka?", "meaning": "Do you speak English?", "usage_context": "Asking for language help"},
        ] if destination.lower() == "japan" else [
            {"phrase": "Hello", "meaning": "Greeting", "usage_context": "Basic politeness"},
            {"phrase": "Thank you", "meaning": "Gratitude", "usage_context": "General daily use"},
        ]
        return {
            "summary": llm_text or f"Culture and etiquette guidance prepared for {destination}.",
            "etiquette": [
                "Speak softly on public transport and keep phone calls minimal.",
                "Follow queue order carefully in stations, elevators, and shops.",
                "Check house rules before taking photos inside temples, museums, or small eateries.",
                "Carry a small bag for your own trash when public bins are limited.",
            ],
            "phrases": phrases,
            "behavior_tips": [
                "Politeness and patience usually matter more than perfect pronunciation.",
                "Pointing at menu pictures or translation text is often acceptable when done respectfully.",
                "Tipping customs vary by country, so follow local practice instead of assuming it is expected.",
            ],
            "source_notes": snippets,
        }


culture_agent = CultureAgent()

```

## `app/agents/destination_agent.py`

```python
from __future__ import annotations

from typing import Any

from app.config.settings import get_settings
from app.prompts.destination_prompt import DESTINATION_PROMPT
from app.tools.search_tools import search_service
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class DestinationResearchAgent:
    def __init__(self) -> None:
        self._llm = None
        if not settings.use_mock_llm:
            from langchain_groq import ChatGroq
            self._llm = ChatGroq(model=settings.groq_model, api_key=settings.groq_api_key, temperature=0.2)

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        parsed = state["parsed_trip_info"]
        destination = parsed.get("destination") or "destination"
        query = f"best cultural attractions history transport safety tips for {destination} {' '.join(parsed.get('cities', []))}"
        snippets = []
        try:
            snippets.append(search_service.wikipedia(destination))
        except Exception as exc:  # noqa: BLE001
            state["tool_failures"].append(f"destination_wikipedia_failed: {exc}")
        try:
            snippets.append(search_service.search(query))
        except Exception as exc:  # noqa: BLE001
            state["tool_failures"].append(f"destination_search_failed: {exc}")

        if settings.use_mock_llm:
            return self._heuristic_output(parsed, snippets)

        prompt = (
            f"{DESTINATION_PROMPT}\n\n"
            f"Parsed trip info: {parsed}\n\n"
            "Research snippets:\n" + "\n\n".join(snippets)
        )
        message = await self._llm.ainvoke(prompt)
        return self._heuristic_output(parsed, snippets, llm_text=message.content)

    def _heuristic_output(self, parsed: dict[str, Any], snippets: list[str], llm_text: str | None = None) -> dict[str, Any]:
        destination = parsed.get("destination") or "the destination"
        cities = parsed.get("cities", [])
        primary_city = cities[0] if cities else destination
        secondary_city = cities[1] if len(cities) > 1 else destination
        return {
            "summary": llm_text or f"Focused destination research completed for {destination} with emphasis on cultural landmarks, transit, and visitor safety.",
            "highlights": [
                f"Prioritize iconic cultural districts and historic sites in {primary_city}.",
                f"Balance major landmarks with slower neighborhood exploration in {secondary_city}.",
                "Reserve one museum, temple, or heritage site visit per full day to avoid rushing.",
                "Book popular experiences in advance during peak seasons.",
            ],
            "transport": [
                "Use reloadable transit cards for metro and local train convenience.",
                "Choose accommodations near a major station to reduce transfers.",
                "Keep a navigation app and offline map ready before moving between cities.",
            ],
            "safety": [
                "Carry your hotel address in writing for easy navigation or taxi help.",
                "Keep cash and one backup card for smaller local shops.",
                "Watch the last-train timing if staying out late.",
            ],
            "sample_day": [
                f"Morning visit to a signature cultural site in {primary_city}",
                "Lunch at a traditional local restaurant",
                "Afternoon walk through a heritage or shopping district",
                "Evening observation spot or quiet cultural performance",
            ],
            "final_tips": [
                "Cluster attractions by neighborhood instead of crossing the city repeatedly.",
                "Start temple or museum visits early for calmer crowds.",
            ],
            "source_notes": snippets,
        }


destination_agent = DestinationResearchAgent()

```

## `app/agents/weather_agent.py`

```python
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

        prompt = (
            f"{WEATHER_PROMPT}\n\n"
            f"Parsed trip info: {parsed}\n\n"
            f"Weather context: {weather_context}"
        )
        message = await self._llm.ainvoke(prompt)
        return self._heuristic_output(parsed, weather_context, llm_text=message.content)

    def _heuristic_output(self, parsed: dict[str, Any], weather_context: dict[str, Any], llm_text: str | None = None) -> dict[str, Any]:
        return {
            "summary": llm_text or f"Weather guidance prepared for {parsed.get('destination') or 'the trip'}.",
            "weather_expectations": [weather_context["summary"]],
            "packing_suggestions": weather_context["packing"],
            "activity_advice": weather_context["activity_advice"],
        }


weather_agent = WeatherPlanningAgent()

```

## `app/api/__init__.py`

```python

```

## `app/api/routes_travel.py`

```python
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.schemas.request import TripPlanningRequest
from app.schemas.response import ApiResponse, TripPlanningResponse
from app.services.trip_service import get_trip_service

router = APIRouter(prefix="/api/v1/travel", tags=["travel"])


@router.post("/plan", response_model=ApiResponse)
async def plan_trip(payload: TripPlanningRequest) -> ApiResponse:
    service = get_trip_service()
    try:
        response = await service.plan_trip(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Trip planning failed: {exc}") from exc

    return ApiResponse(success=True, message="Travel plan created successfully.", data=response)

```

## `app/config/__init__.py`

```python

```

## `app/config/settings.py`

```python
from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = Field(default="Travel Planner API", alias="APP_NAME")
    app_env: Literal["dev", "test", "prod"] = Field(default="dev", alias="APP_ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    groq_api_key: str = Field(default="", alias="GROQ_API_KEY")
    groq_model: str = Field(default="openai/gpt-oss-20b", alias="GROQ_MODEL")
    use_mock_llm: bool = Field(default=True, alias="USE_MOCK_LLM")
    use_mock_weather: bool = Field(default=True, alias="USE_MOCK_WEATHER")

    open_meteo_base_url: str = Field(default="https://api.open-meteo.com/v1/forecast", alias="OPEN_METEO_BASE_URL")
    default_session_ttl_minutes: int = Field(default=120, alias="DEFAULT_SESSION_TTL_MINUTES")

    search_provider: str = Field(default="duckduckgo", alias="SEARCH_PROVIDER")
    enable_wikipedia_tool: bool = Field(default=True, alias="ENABLE_WIKIPEDIA_TOOL")
    enable_search_tool: bool = Field(default=True, alias="ENABLE_SEARCH_TOOL")

    streamlit_api_url: str = Field(default="http://localhost:8000/api/v1/travel/plan", alias="STREAMLIT_API_URL")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

```

## `app/graph/__init__.py`

```python

```

## `app/graph/builder.py`

```python
from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from app.graph.nodes import (
    culture_node,
    destination_node,
    final_response_node,
    input_node,
    planning_router_node,
    synthesis_node,
    weather_node,
)
from app.graph.router import router
from app.graph.state import TravelGraphState


def _route_after_router(state: TravelGraphState) -> str:
    return router.next_node(state)


def build_travel_graph():
    graph = StateGraph(TravelGraphState)
    graph.add_node("input", input_node)
    graph.add_node("router", planning_router_node)
    graph.add_node("destination", destination_node)
    graph.add_node("weather", weather_node)
    graph.add_node("culture", culture_node)
    graph.add_node("synthesis", synthesis_node)
    graph.add_node("final_response", final_response_node)

    graph.add_edge(START, "input")
    graph.add_edge("input", "router")
    graph.add_conditional_edges(
        "router",
        _route_after_router,
        {
            "destination": "destination",
            "weather": "weather",
            "culture": "culture",
            "synthesis": "synthesis",
        },
    )
    graph.add_edge("destination", "router")
    graph.add_edge("weather", "router")
    graph.add_edge("culture", "router")
    graph.add_edge("synthesis", "final_response")
    graph.add_edge("final_response", END)

    return graph.compile()

```

## `app/graph/nodes.py`

```python
from __future__ import annotations

from copy import deepcopy

from app.agents.coordinator import coordinator_agent
from app.agents.culture_agent import culture_agent
from app.agents.destination_agent import destination_agent
from app.agents.weather_agent import weather_agent
from app.graph.router import router
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def input_node(state: dict) -> dict:
    logger.info("node_input_started", session_id=state["session_id"])
    new_state = deepcopy(state)
    new_state.setdefault("specialist_outputs", {})
    new_state.setdefault("completed_agents", [])
    new_state.setdefault("router_reasons", [])
    new_state.setdefault("tool_failures", [])
    new_state.setdefault("errors", [])
    return new_state


async def planning_router_node(state: dict) -> dict:
    logger.info("node_router_started", session_id=state["session_id"])
    new_state = deepcopy(state)
    if not new_state.get("parsed_trip_info"):
        parsed = await coordinator_agent.parse_trip_info(new_state["request_payload"])
        new_state["parsed_trip_info"] = parsed.model_dump()
    required, reasons = router.decide_required_agents(new_state["parsed_trip_info"], new_state["user_query"])
    new_state["required_agents"] = required
    new_state["router_reasons"] = reasons
    return new_state


async def destination_node(state: dict) -> dict:
    logger.info("node_destination_started", session_id=state["session_id"])
    new_state = deepcopy(state)
    output = await destination_agent.run(new_state)
    new_state["specialist_outputs"]["destination"] = output
    new_state["completed_agents"] = list(dict.fromkeys(new_state["completed_agents"] + ["destination"]))
    return new_state


async def weather_node(state: dict) -> dict:
    logger.info("node_weather_started", session_id=state["session_id"])
    new_state = deepcopy(state)
    output = await weather_agent.run(new_state)
    new_state["specialist_outputs"]["weather"] = output
    new_state["completed_agents"] = list(dict.fromkeys(new_state["completed_agents"] + ["weather"]))
    return new_state


async def culture_node(state: dict) -> dict:
    logger.info("node_culture_started", session_id=state["session_id"])
    new_state = deepcopy(state)
    output = await culture_agent.run(new_state)
    new_state["specialist_outputs"]["culture"] = output
    new_state["completed_agents"] = list(dict.fromkeys(new_state["completed_agents"] + ["culture"]))
    return new_state


async def synthesis_node(state: dict) -> dict:
    logger.info("node_synthesis_started", session_id=state["session_id"])
    new_state = deepcopy(state)
    final_plan = await coordinator_agent.synthesize(new_state)
    new_state["final_plan"] = final_plan.model_dump()
    return new_state


async def final_response_node(state: dict) -> dict:
    logger.info("node_final_response_started", session_id=state["session_id"])
    return state

```

## `app/graph/router.py`

```python
from __future__ import annotations

from app.utils.logger import get_logger

logger = get_logger(__name__)


SPECIALIST_ORDER = ["destination", "weather", "culture"]


class Router:
    def decide_required_agents(self, parsed_trip_info: dict, user_query: str) -> tuple[list[str], list[str]]:
        query = (user_query or "").lower()
        interests = " ".join(parsed_trip_info.get("interests", [])).lower()
        prefs = " ".join(parsed_trip_info.get("special_preferences", [])).lower()
        combined = f"{query} {interests} {prefs}"
        required = ["destination"]
        reasons = ["destination agent is the default foundation for travel planning."]

        if any(keyword in combined for keyword in ["weather", "season", "packing", "rain", "temperature", "month"]):
            required.append("weather")
            reasons.append("weather-related details were requested or inferred from the trip context.")

        if any(keyword in combined for keyword in ["language", "culture", "etiquette", "english", "phrases", "customs", "tips"]):
            required.append("culture")
            reasons.append("language or cultural guidance was requested or inferred.")

        if parsed_trip_info.get("travel_month") or parsed_trip_info.get("season"):
            if "weather" not in required:
                required.append("weather")
                reasons.append("season or travel month was provided, so weather planning adds value.")

        return required, reasons

    def next_node(self, state: dict) -> str:
        required = state.get("required_agents", [])
        completed = state.get("completed_agents", [])
        for agent_name in SPECIALIST_ORDER:
            if agent_name in required and agent_name not in completed:
                return agent_name
        return "synthesis"


router = Router()

```

## `app/graph/state.py`

```python
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

```

## `app/main.py`

```python
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_travel import router as travel_router
from app.config.settings import get_settings
from app.utils.logger import configure_logging, get_logger

settings = get_settings()
configure_logging(settings.log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("application_starting", app_name=settings.app_name, env=settings.app_env)
    yield
    logger.info("application_stopping", app_name=settings.app_name)


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "app": settings.app_name}


app.include_router(travel_router)

```

## `app/memory/__init__.py`

```python

```

## `app/memory/session_memory.py`

```python
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from app.config.settings import get_settings


class SessionMemoryStore:
    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}
        self._settings = get_settings()

    def get(self, session_id: str) -> dict[str, Any]:
        record = self._store.get(session_id, {})
        expires_at = record.get("expires_at")
        if expires_at and datetime.now(timezone.utc) > expires_at:
            self._store.pop(session_id, None)
            return {}
        return record.get("preferences", {})

    def upsert(self, session_id: str, preferences: dict[str, Any]) -> None:
        current = self.get(session_id)
        current.update({k: v for k, v in preferences.items() if v not in (None, [], "")})
        ttl = timedelta(minutes=self._settings.default_session_ttl_minutes)
        self._store[session_id] = {
            "preferences": current,
            "expires_at": datetime.now(timezone.utc) + ttl,
        }


session_memory = SessionMemoryStore()

```

## `app/prompts/__init__.py`

```python

```

## `app/prompts/coordinator_prompt.py`

```python
COORDINATOR_PARSE_PROMPT = """
You are the Travel Coordinator. Extract structured trip information from the user request.
Be concise, infer only when reasonable, and list any missing details.
"""

COORDINATOR_SYNTHESIS_PROMPT = """
You are the Travel Coordinator. Your job is not to act like a general travel expert.
Instead, synthesize specialist outputs into one clean, practical travel plan.
Resolve overlap, remove repetition, and keep the final output user-friendly.
"""

```

## `app/prompts/culture_prompt.py`

```python
CULTURE_PROMPT = """
You are the Language & Culture Agent.
Focus only on etiquette, local norms, cultural sensitivity, dining behavior, tipping, social conduct, and useful survival phrases.
Do not recommend tourist attractions unless needed for etiquette context.
"""

```

## `app/prompts/destination_prompt.py`

```python
DESTINATION_PROMPT = """
You are the Destination Research Agent.
Focus only on attractions, historical and cultural highlights, timing, transportation basics, safety, and destination-specific travel tips.
Do not give weather, etiquette, or language advice unless it directly affects logistics.
"""

```

## `app/prompts/weather_prompt.py`

```python
WEATHER_PROMPT = """
You are the Weather Planning Agent.
Focus only on weather expectations, seasonal advice, clothing, packing, and weather-aware activity planning.
Do not cover destination attractions or social etiquette.
"""

```

## `app/schemas/__init__.py`

```python

```

## `app/schemas/request.py`

```python
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

```

## `app/schemas/response.py`

```python
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
    weather_expectations: list[str] = Field(default_factory=list)
    packing_suggestions: list[str] = Field(default_factory=list)
    cultural_etiquette: list[str] = Field(default_factory=list)
    essential_language_phrases: list[PhraseItem] = Field(default_factory=list)
    transport_guidance: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)
    optional_day_wise_itinerary: list[ItineraryDay] = Field(default_factory=list)
    final_travel_tips: list[str] = Field(default_factory=list)
    agent_contributions: dict[str, str] = Field(default_factory=dict)


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

```

## `app/services/__init__.py`

```python

```

## `app/services/trip_service.py`

```python
from __future__ import annotations

from functools import lru_cache

from app.graph.builder import build_travel_graph
from app.memory.session_memory import session_memory
from app.schemas.request import TripPlanningRequest
from app.schemas.response import FinalTravelPlan, TripPlanningResponse
from app.tools.helper_tools import merge_trip_context
from app.utils.logger import get_logger

logger = get_logger(__name__)


class TripService:
    def __init__(self) -> None:
        self.graph = build_travel_graph()

    async def plan_trip(self, payload: TripPlanningRequest) -> TripPlanningResponse:
        memory_data = session_memory.get(payload.session_id)
        merged_payload = merge_trip_context(payload.model_dump(), memory_data)

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

```

## `app/tools/__init__.py`

```python

```

## `app/tools/helper_tools.py`

```python
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

```

## `app/tools/search_tools.py`

```python
from __future__ import annotations

from app.config.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

try:
    from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun
    from langchain_community.utilities import WikipediaAPIWrapper
except Exception:  # noqa: BLE001
    DuckDuckGoSearchRun = None
    WikipediaQueryRun = None
    WikipediaAPIWrapper = None


class SearchToolService:
    def __init__(self) -> None:
        self.enable_search = settings.enable_search_tool and DuckDuckGoSearchRun is not None
        self.enable_wikipedia = settings.enable_wikipedia_tool and WikipediaQueryRun is not None and WikipediaAPIWrapper is not None
        self._search = DuckDuckGoSearchRun() if self.enable_search else None
        self._wiki = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=1200)) if self.enable_wikipedia else None

    def search(self, query: str) -> str:
        if not query:
            return ""
        try:
            if self._search:
                return self._search.run(query)
        except Exception as exc:  # noqa: BLE001
            logger.warning("search_tool_failed", query=query, error=str(exc))
            raise
        return f"Mock search result: common travel facts for {query}."

    def wikipedia(self, query: str) -> str:
        if not query:
            return ""
        try:
            if self._wiki:
                return self._wiki.run(query)
        except Exception as exc:  # noqa: BLE001
            logger.warning("wikipedia_tool_failed", query=query, error=str(exc))
            raise
        return f"Mock encyclopedia note: {query} is a major travel destination with cultural highlights and public transit."


search_service = SearchToolService()

```

## `app/tools/weather_tools.py`

```python
from __future__ import annotations

from typing import Any

import httpx

from app.config.settings import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

MOCK_WEATHER = {
    "japan": {
        "spring": {"summary": "Mild temperatures with some rain and cherry blossom crowds.", "packing": ["light jacket", "umbrella", "comfortable walking shoes"]},
        "summer": {"summary": "Warm to hot, humid, and occasionally rainy.", "packing": ["breathable clothes", "portable fan", "light rain layer"]},
        "autumn": {"summary": "Cool, comfortable, and ideal for city walking.", "packing": ["layered clothing", "light sweater", "comfortable sneakers"]},
        "winter": {"summary": "Cold but manageable in major cities, drier than summer.", "packing": ["coat", "thermal layer", "scarf"]},
    }
}


class WeatherToolService:
    async def get_weather_guidance(self, destination: str, travel_month: str | None, season: str | None) -> dict[str, Any]:
        if settings.use_mock_weather:
            return self._mock_weather(destination, travel_month, season)
        try:
            # Placeholder real-weather integration point.
            async with httpx.AsyncClient(timeout=20) as client:
                await client.get("https://api.open-meteo.com")
            return self._mock_weather(destination, travel_month, season)
        except Exception as exc:  # noqa: BLE001
            logger.warning("weather_api_failed", destination=destination, error=str(exc))
            return self._mock_weather(destination, travel_month, season, fallback_reason=str(exc))

    def _mock_weather(self, destination: str, travel_month: str | None, season: str | None, fallback_reason: str | None = None) -> dict[str, Any]:
        normalized = (destination or "").strip().lower()
        derived_season = (season or self._month_to_season(travel_month)).lower()
        country_data = MOCK_WEATHER.get(normalized, {}) or MOCK_WEATHER.get("japan", {})
        season_data = country_data.get(derived_season, country_data.get("autumn"))
        payload = {
            "summary": season_data["summary"],
            "packing": season_data["packing"],
            "activity_advice": [
                "Keep one indoor backup activity for rainy periods.",
                "Start long walking days early to avoid fatigue and queues.",
            ],
            "fallback_reason": fallback_reason,
        }
        return payload

    @staticmethod
    def _month_to_season(travel_month: str | None) -> str:
        if not travel_month:
            return "autumn"
        month = travel_month.strip().lower()
        mapping = {
            "march": "spring", "april": "spring", "may": "spring",
            "june": "summer", "july": "summer", "august": "summer",
            "september": "autumn", "october": "autumn", "november": "autumn",
            "december": "winter", "january": "winter", "february": "winter",
        }
        return mapping.get(month, "autumn")


weather_service = WeatherToolService()

```

## `app/utils/__init__.py`

```python

```

## `app/utils/helpers.py`

```python
from __future__ import annotations

from typing import Iterable


def safe_join(items: Iterable[str], sep: str = ", ") -> str:
    return sep.join([item for item in items if item])



def unique_preserve_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result

```

## `app/utils/logger.py`

```python
from __future__ import annotations

import logging
import sys

import structlog


_CONFIGURED = False


def configure_logging(level: str = "INFO") -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper(), logging.INFO),
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, level.upper(), logging.INFO)),
        cache_logger_on_first_use=True,
    )
    _CONFIGURED = True



def get_logger(name: str):
    return structlog.get_logger(name)

```

## `requirements.txt`

```text
fastapi>=0.116.0
uvicorn[standard]>=0.35.0
streamlit>=1.48.0
requests>=2.32.0
python-dotenv>=1.0.1
pydantic>=2.11.0
pydantic-settings>=2.10.0
langchain>=0.3.27
langgraph>=0.6.0
langchain-groq>=0.3.6
langchain-community>=0.3.27
wikipedia>=1.4.0
duckduckgo-search>=6.3.0
structlog>=25.4.0
httpx>=0.28.0
pytest>=8.3.0
pytest-asyncio>=1.1.0

```

## `run.py`

```python
import os
import uvicorn


if __name__ == "__main__":
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))
    uvicorn.run("app.main:app", host=host, port=port, reload=True)

```

## `streamlit_app.py`

```python
from __future__ import annotations

import json
import os
from typing import Any

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("STREAMLIT_API_URL", "http://localhost:8000/api/v1/travel/plan")

st.set_page_config(page_title="Multi-Agent Travel Planner", page_icon="✈️", layout="wide")
st.title("✈️ Multi-Agent Travel Planner")
st.caption("LangGraph + LangChain + Groq + FastAPI + Streamlit")

with st.sidebar:
    st.subheader("Trip Preferences")
    session_id = st.text_input("Session ID", value="demo-session")
    destination = st.text_input("Destination", value="Japan")
    cities = st.text_input("Cities (comma-separated)", value="Tokyo, Osaka")
    duration_days = st.number_input("Duration (days)", min_value=1, max_value=60, value=14)
    travel_style = st.selectbox("Travel style", ["cultural", "budget", "luxury", "family", "solo", "mixed"], index=0)
    budget = st.selectbox("Budget", ["budget", "mid-range", "luxury"], index=1)
    travel_month = st.text_input("Travel month", value="October")
    language_comfort = st.text_input("Language comfort", value="English only")
    interests = st.multiselect(
        "Interests",
        ["culture", "history", "food", "nature", "shopping", "nightlife", "architecture", "anime"],
        default=["culture", "history"],
    )
    special_preferences = st.text_area(
        "Special preferences",
        value="First-time visitor, traditional culture, historical places, weather guidance, language help",
    )

user_query = st.text_area(
    "Travel request",
    value=(
        "I’m planning a 2-week cultural immersion trip to Japan (Tokyo and Osaka) as a first-time visitor. "
        "I want traditional culture, historical places, weather guidance, and language/cultural tips. I only speak English."
    ),
    height=140,
)


def call_api(payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(API_URL, json=payload, timeout=120)
    response.raise_for_status()
    return response.json()


if st.button("Generate Travel Plan", type="primary"):
    payload = {
        "session_id": session_id,
        "user_query": user_query,
        "destination": destination,
        "cities": [c.strip() for c in cities.split(",") if c.strip()],
        "duration_days": int(duration_days),
        "travel_style": travel_style,
        "interests": interests,
        "budget": budget,
        "travel_month": travel_month,
        "language_comfort": language_comfort,
        "special_preferences": [p.strip() for p in special_preferences.split(",") if p.strip()],
    }

    with st.spinner("Planning your trip..."):
        try:
            data = call_api(payload)
        except Exception as exc:  # noqa: BLE001
            st.error(f"Request failed: {exc}")
        else:
            result = data["data"]
            final_plan = result["final_plan"]

            col1, col2 = st.columns([2, 1])
            with col1:
                st.subheader("Trip Summary")
                st.write(final_plan["trip_summary"])
                st.subheader("Destination Highlights")
                for item in final_plan["destination_highlights"]:
                    st.markdown(f"- {item}")
                st.subheader("Weather Expectations")
                for item in final_plan["weather_expectations"]:
                    st.markdown(f"- {item}")
                st.subheader("Packing Suggestions")
                for item in final_plan["packing_suggestions"]:
                    st.markdown(f"- {item}")
                st.subheader("Cultural Etiquette")
                for item in final_plan["cultural_etiquette"]:
                    st.markdown(f"- {item}")
                st.subheader("Essential Language Phrases")
                for item in final_plan["essential_language_phrases"]:
                    st.markdown(f"- **{item['phrase']}** — {item['meaning']} ({item['usage_context']})")
                st.subheader("Transport Guidance")
                for item in final_plan["transport_guidance"]:
                    st.markdown(f"- {item}")
                st.subheader("Safety Notes")
                for item in final_plan["safety_notes"]:
                    st.markdown(f"- {item}")
                if final_plan["optional_day_wise_itinerary"]:
                    st.subheader("Optional Day-wise Itinerary")
                    for day in final_plan["optional_day_wise_itinerary"]:
                        st.markdown(f"**Day {day['day']}: {day['theme']}**")
                        for activity in day["activities"]:
                            st.markdown(f"- {activity}")
                st.subheader("Final Travel Tips")
                for item in final_plan["final_travel_tips"]:
                    st.markdown(f"- {item}")

            with col2:
                st.subheader("Agent Contributions")
                for agent, content in final_plan["agent_contributions"].items():
                    st.markdown(f"**{agent}**")
                    st.code(content or "No output")
                st.subheader("Execution")
                st.json({
                    "called_agents": result["called_agents"],
                    "router_reasons": result["router_reasons"],
                    "tool_failures": result["tool_failures"],
                })
                with st.expander("Raw JSON"):
                    st.code(json.dumps(data, indent=2), language="json")

```

## `tests/test_trip_service.py`

```python
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

```
