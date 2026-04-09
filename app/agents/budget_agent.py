from __future__ import annotations

from typing import Any

from app.config.settings import get_settings
from app.prompts.budget_prompt import BUDGET_PROMPT
from app.tools.budget_tools import budget_service
from app.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class BudgetPlanningAgent:
    def __init__(self) -> None:
        self._llm = None
        if not settings.use_mock_llm:
            from langchain_groq import ChatGroq

            self._llm = ChatGroq(model=settings.groq_model, api_key=settings.groq_api_key, temperature=0.2)

    async def run(self, state: dict[str, Any]) -> dict[str, Any]:
        parsed = state["parsed_trip_info"]
        destination = parsed.get("destination") or "destination"
        travel_style = parsed.get("travel_style") or "mid-range"
        duration_days = parsed.get("duration_days") or 7
        budget_preference = parsed.get("budget") or "mid-range"

        # Get budget data from tools
        daily_budget = budget_service.estimate_daily_budget(destination, budget_preference, duration_days)
        category_breakdown = budget_service.breakdown_by_category(destination, budget_preference, duration_days)
        currency_info = budget_service.get_currency_info(destination)
        money_tips = budget_service.get_money_tips(destination)

        if settings.use_mock_llm:
            return self._heuristic_output(parsed, daily_budget, category_breakdown, currency_info, money_tips)

        from langchain_core.messages import HumanMessage
        
        prompt = (
            f"{BUDGET_PROMPT}\n\n"
            f"Parsed trip info: {parsed}\n\n"
            f"Daily budget estimate: {daily_budget}\n\n"
            f"Category breakdown: {category_breakdown}\n\n"
            f"Currency info: {currency_info}\n\n"
            f"Money tips: {money_tips}"
        )
        message = await self._llm.ainvoke([HumanMessage(content=prompt)])
        return self._heuristic_output(parsed, daily_budget, category_breakdown, currency_info, money_tips, llm_text=message.content)

    def _heuristic_output(
        self,
        parsed: dict[str, Any],
        daily_budget: dict[str, Any],
        category_breakdown: dict[str, Any],
        currency_info: dict[str, Any],
        money_tips: dict[str, Any],
        llm_text: str | None = None,
    ) -> dict[str, Any]:
        destination = parsed.get("destination") or "the destination"
        duration_days = parsed.get("duration_days") or 7
        trip_total = daily_budget.get("trip_total") or (daily_budget.get("daily_total", 0) * duration_days)

        return {
            "summary": llm_text or f"Budget planning for {destination} ({duration_days} days) in {parsed.get('travel_style', 'mid-range')} style.",
            "daily_estimate": daily_budget["daily_total"],
            "trip_total_estimate": trip_total,
            "daily_breakdown": daily_budget["daily_breakdown"],
            "category_details": {
                "accommodation": category_breakdown["accommodation"],
                "food": category_breakdown["food"],
                "activities": category_breakdown["activities"],
                "transport": category_breakdown["transport"],
            },
            "currency": currency_info["currency_code"],
            "exchange_rate": currency_info["usd_exchange_rate"],
            "payment_methods": currency_info["payment_methods"],
            "money_tips": money_tips["tips"],
            "general_advice": money_tips["general_advice"],
            "note": "Contingency buffer of 10-15% recommended for flexibility.",
        }

budget_agent = BudgetPlanningAgent()