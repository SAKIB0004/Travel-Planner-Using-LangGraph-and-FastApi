from __future__ import annotations

from copy import deepcopy

from app.agents.accommodation_agent import accommodation_agent
from app.agents.budget_agent import budget_agent
from app.agents.coordinator import coordinator_agent
from app.agents.culture_agent import culture_agent
from app.agents.destination_agent import destination_agent
from app.agents.transportation_agent import transportation_agent
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


async def transportation_node(state: dict) -> dict:
    logger.info("node_transportation_started", session_id=state["session_id"])
    new_state = deepcopy(state)
    output = await transportation_agent.run(new_state)
    new_state["specialist_outputs"]["transportation"] = output
    new_state["completed_agents"] = list(dict.fromkeys(new_state["completed_agents"] + ["transportation"]))
    return new_state


async def accommodation_node(state: dict) -> dict:
    logger.info("node_accommodation_started", session_id=state["session_id"])
    new_state = deepcopy(state)
    output = await accommodation_agent.run(new_state)
    new_state["specialist_outputs"]["accommodation"] = output
    new_state["completed_agents"] = list(dict.fromkeys(new_state["completed_agents"] + ["accommodation"]))
    return new_state


async def budget_node(state: dict) -> dict:
    logger.info("node_budget_started", session_id=state["session_id"])
    new_state = deepcopy(state)
    output = await budget_agent.run(new_state)
    new_state["specialist_outputs"]["budget"] = output
    new_state["completed_agents"] = list(dict.fromkeys(new_state["completed_agents"] + ["budget"]))
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
