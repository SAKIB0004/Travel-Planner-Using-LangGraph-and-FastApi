#!/usr/bin/env python
"""Test that different trip durations are respected end-to-end"""

import asyncio
from app.services.trip_service import TripService
from app.schemas.request import TripPlanningRequest

async def test_different_durations():
    """Test that 2, 3, and 10 day plans generate correctly"""
    service = TripService()
    
    test_cases = [
        ("2 days in Paris exploring culture", 2),
        ("I want 3 days in Tokyo", 3),
        ("10-day cultural trip to Japan", 10),
    ]
    
    print("Testing end-to-end trip generation with different durations:\n")
    
    for query, expected_duration in test_cases:
        payload = TripPlanningRequest(
            session_id=f"test-{expected_duration}d",
            user_query=query,
        )
        
        result = await service.plan_trip(payload)
        
        # Check parsed duration
        parsed_duration = result.parsed_trip_info.get("duration_days", 7)
        
        # Check polished narrative duration
        narrative = result.final_plan.polished_narrative
        
        print(f"Query: '{query}'")
        print(f"  Expected duration: {expected_duration} days")
        print(f"  Parsed duration: {parsed_duration} days")
        
        # Check if narrative mentions the correct number of days
        if f"{expected_duration}-day" in narrative or f"{expected_duration}-Day" in narrative:
            print(f"  ✅ Narrative correctly mentions {expected_duration} days")
        else:
            print(f"  ⚠️  Narrative might not mention {expected_duration} days")
        
        # Show first line of narrative
        first_line = narrative.split('\n')[2] if len(narrative.split('\n')) > 2 else ""
        print(f"  Title: {first_line}")
        
        if parsed_duration == expected_duration:
            print(f"  ✅ PASS\n")
        else:
            print(f"  ❌ FAIL\n")

asyncio.run(test_different_durations())
