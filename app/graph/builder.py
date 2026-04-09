from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from app.graph.nodes import (
    accommodation_node,
    budget_node,
    culture_node,
    destination_node,
    final_response_node,
    input_node,
    planning_router_node,
    synthesis_node,
    transportation_node,
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
    graph.add_node("transportation", transportation_node)
    graph.add_node("accommodation", accommodation_node)
    graph.add_node("budget", budget_node)
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
            "transportation": "transportation",
            "accommodation": "accommodation",
            "budget": "budget",
            "weather": "weather",
            "culture": "culture",
            "synthesis": "synthesis",
        },
    )
    graph.add_edge("destination", "router")
    graph.add_edge("transportation", "router")
    graph.add_edge("accommodation", "router")
    graph.add_edge("budget", "router")
    graph.add_edge("weather", "router")
    graph.add_edge("culture", "router")
    graph.add_edge("synthesis", "final_response")
    graph.add_edge("final_response", END)

    return graph.compile()
