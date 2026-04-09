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

        from langchain_core.messages import HumanMessage
        
        prompt = (
            f"{CULTURE_PROMPT}\n\n"
            f"Parsed trip info: {parsed}\n\n"
            f"Research snippets: {snippets}"
        )
        message = await self._llm.ainvoke([HumanMessage(content=prompt)])
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
