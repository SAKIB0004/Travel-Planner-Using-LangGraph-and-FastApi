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
