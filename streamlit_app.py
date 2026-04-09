from __future__ import annotations

import json
import os
from typing import Any

import requests
import streamlit as st
from dotenv import load_dotenv

from app.utils.helpers import sanitize_value, format_list_as_markdown

load_dotenv()

API_URL = os.getenv("STREAMLIT_API_URL", "http://localhost:8000/api/v1/travel/plan")

st.set_page_config(page_title="Multi-Agent Travel Planner", page_icon="✈️", layout="wide")
st.title("✈️ Multi-Agent Travel Planner")
st.caption("LangGraph + LangChain + Groq + FastAPI + Streamlit")

with st.sidebar:
    st.subheader("⚙️ Session Settings")
    session_id = st.text_input("Session ID", value="travel-session-001", help="Used to save your preferences across queries")
    
    st.divider()
    st.subheader("ℹ️ How to Use")
    st.info(
        "**Describe your trip naturally** in the text area below. Include:\n"
        "- Destination & cities\n"
        "- Duration & dates/month\n"
        "- Budget/travel style\n"
        "- Interests & preferences\n\n"
        "Our 6 agents will handle the rest!"
    )
    
    st.divider()
    st.subheader("🎯 Quick Starts")
    quick_templates = {
        "Japan Cultural Trip": "I'm planning a 10-day cultural trip to Japan (Tokyo and Osaka) in October. Mid-range budget. First time visitor interested in tradition, history, and local culture. Need flights, hotels, budget breakdown, weather info, and language help.",
        "Europe Budget": "Planning a 2-week backpacking trip across Europe (Paris, Rome, Barcelona) in September on a tight budget. Interested in history, food, and nightlife. Need cost estimates, transport routes, and hostel/budget hotel recommendations.",
        "Thailand Adventure": "I want a 7-day adventure trip to Thailand (Bangkok and Phuket) in November. Adventure seeker with moderate budget. Interested in nature, food, and local experiences. Need travel guides and cost estimates.",
    }
    
    selected_template = st.selectbox("Or choose a template:", ["Custom"] + list(quick_templates.keys()))
    if selected_template != "Custom":
        default_query = quick_templates[selected_template]
    else:
        default_query = ""
    
    st.divider()
    st.subheader("📊 API Status")
    try:
        api_response = requests.get("http://localhost:8000/health", timeout=2)
        if api_response.status_code == 200:
            st.success("✅ API Running")
        else:
            st.error("⚠️ API Error")
    except:
        st.error("❌ API Offline - Start with: uvicorn app.main:app --reload")




user_query = st.text_area(
    "📝 Describe Your Trip",
    value=default_query if 'default_query' in locals() and default_query else (
        "I'm planning a 10-day cultural trip to Japan (Tokyo and Osaka) in October. "
        "Mid-range budget. First time visitor interested in tradition, history, and local culture. "
        "Need flights, hotels, budget breakdown, weather info, and language help."
    ),
    height=180,
    help="The more details you provide, the better our agents can plan your trip!"
)


def call_api(payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(API_URL, json=payload, timeout=120)
    response.raise_for_status()
    return response.json()


if st.button("🚀 Generate Travel Plan", type="primary", use_container_width=True):
    payload = {
        "session_id": session_id,
        "user_query": user_query,
        # Optional: These will be extracted from user_query by the coordinator agent
        "destination": None,
        "cities": [],
        "duration_days": None,
        "travel_style": None,
        "interests": [],
        "budget": None,
        "travel_month": None,
        "language_comfort": None,
        "special_preferences": [],
    }

    with st.spinner("🔄 Planning your trip with 6 AI agents..."):
        try:
            data = call_api(payload)
        except Exception as exc:  # noqa: BLE001
            st.error(f"Request failed: {exc}")
        else:
            result = data["data"]
            final_plan = result["final_plan"]

            # ===== MAIN POLISHED OUTPUT =====
            st.markdown("---")
            
            # Display polished narrative as PRIMARY content
            if final_plan.get("polished_narrative"):
                st.markdown(final_plan["polished_narrative"])
            else:
                # Fallback to summary if narrative not available
                st.subheader("Trip Summary")
                st.write(sanitize_value(final_plan.get("trip_summary", ""), "No trip summary available"))
            
            st.markdown("---")
            
            # ===== OPTIONAL: DETAILED BREAKDOWN =====
            with st.expander("📋 Planning Details & Data", expanded=False):
                st.markdown("### Key Information Extracted")
                
                # Parsed trip info
                st.markdown("**Trip Details**")
                parsed = result.get("parsed_trip_info", {})
                st.markdown(f"""
- **Destination**: {sanitize_value(parsed.get('destination'), 'Not specified')}
- **Cities**: {', '.join(parsed.get('cities', [])) if parsed.get('cities') else 'Not specified'}
- **Duration**: {sanitize_value(parsed.get('duration_days'), 'Not specified')} days
- **Travel Style**: {sanitize_value(parsed.get('travel_style'), 'Not specified')}
- **Budget**: {sanitize_value(parsed.get('budget'), 'Not specified')}
- **Interests**: {', '.join(parsed.get('interests', [])) if parsed.get('interests') else 'Not specified'}
                """)
                
                # Agents involved
                st.markdown("**AI Agents Involved**")
                agents_text = ", ".join(result.get("called_agents", []))
                st.markdown(f"- {agents_text if agents_text else 'No agents called'}")
                
                # Router reasoning
                if result.get("router_reasons"):
                    st.markdown("**Agent Selection Rationale**")
                    for reason in result["router_reasons"]:
                        st.markdown(f"- {sanitize_value(reason, '')}")
                
                # Any tool failures
                if result.get("tool_failures"):
                    st.warning("⚠️ Some Data Fetch Issues")
                    for failure in result["tool_failures"]:
                        st.markdown(f"- {sanitize_value(failure, '')}")
            
            # ===== DEVELOPER VIEW (Hidden by default) =====
            with st.expander("🔧 Developer View (Agent Outputs & Raw Data)", expanded=False):
                st.markdown("### Agent Raw Outputs")
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    if final_plan.get("agent_contributions"):
                        st.markdown("**Agent Outputs**")
                        for agent, content in final_plan["agent_contributions"].items():
                            with st.expander(f"{agent.capitalize()}"):
                                safe_content = sanitize_value(content, "(no output)")
                                st.text(safe_content[:500] + "..." if len(str(safe_content)) > 500 else safe_content)
                with col2:
                    st.markdown("**Destination Highlights**")
                    if final_plan.get("destination_highlights"):
                        for item in final_plan["destination_highlights"][:5]:
                            safe_item = sanitize_value(item, None)
                            if safe_item:
                                st.markdown(f"- {safe_item}")
                
                st.markdown("---")
                st.markdown("### Complete Raw JSON")
                st.code(json.dumps(data, indent=2), language="json", line_numbers=False)
