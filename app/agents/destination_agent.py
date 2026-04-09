from __future__ import annotations

from typing import Any

from app.config.settings import get_settings
from app.prompts.destination_prompt import DESTINATION_PROMPT
from app.tools.search_tools import search_service
from app.tools.country_tools import country_service
from app.tools.geocoding_tools import geocoding_service
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
        
        # Fetch country info in parallel
        country_info = None
        try:
            country_info = await country_service.get_country_info(destination)
        except Exception as exc:  # noqa: BLE001
            logger.warning("destination_country_info_failed", destination=destination, error=str(exc))
        
        try:
            snippets.append(search_service.wikipedia(destination))
        except Exception as exc:  # noqa: BLE001
            state["tool_failures"].append(f"destination_wikipedia_failed: {exc}")
        try:
            snippets.append(search_service.search(query))
        except Exception as exc:  # noqa: BLE001
            state["tool_failures"].append(f"destination_search_failed: {exc}")

        if settings.use_mock_llm:
            return await self._heuristic_output(parsed, snippets, country_info)

        from langchain_core.messages import HumanMessage
        
        prompt = (
            f"{DESTINATION_PROMPT}\n\n"
            f"Parsed trip info: {parsed}\n\n"
            f"Country info: {country_info}\n\n"
            "Research snippets:\n" + "\n\n".join(snippets)
        )
        message = await self._llm.ainvoke([HumanMessage(content=prompt)])
        return await self._heuristic_output(parsed, snippets, country_info, llm_text=message.content)

    async def _heuristic_output(self, parsed: dict[str, Any], snippets: list[str], country_info: dict[str, Any] | None = None, llm_text: str | None = None) -> dict[str, Any]:
        destination = parsed.get("destination") or "the destination"
        cities = parsed.get("cities", [])
        primary_city = cities[0] if cities else destination
        secondary_city = cities[1] if len(cities) > 1 else destination
        
        # Build highlights using country info if available
        highlights = []
        if country_info:
            capital = country_info.get("capital", "")
            region = country_info.get("region", "")
            highlights.append(f"Explore the capital {capital} for government & cultural centers.")
            highlights.append(f"{primary_city} offers unique {region}ian cultural experiences.")
            if secondary_city != primary_city:
                highlights.append(f"Compare {primary_city} and {secondary_city} for different perspectives.")
        else:
            highlights.append(f"Prioritize iconic cultural districts and historic sites in {primary_city}.")
            highlights.append(f"Balance major landmarks with slower neighborhood exploration in {secondary_city}.")
        
        highlights.extend([
            "Reserve one museum, temple, or heritage site visit per full day to avoid rushing.",
            "Book popular experiences in advance during peak seasons.",
        ])
        
        return {
            "summary": llm_text or f"Focused destination research completed for {destination} with emphasis on cultural landmarks, transit, and visitor safety.",
            "highlights": highlights,
            "country_info": country_info or {},
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
