#!/usr/bin/env python
"""Test duration extraction for various input formats"""

from app.utils.helpers import extract_trip_details

test_cases = [
    ("I'm planning a 2-day trip to Paris", 2),
    ("I want 3 days in Tokyo", 3),
    ("a 5-day cultural tour to Japan", 5),
    ("Planning a 10 day vacation in October", 10),
    ("10-day cultural trip to Japan (Tokyo and Osaka)", 10),
    ("2 days in Italy", 2),
    ("7 days visiting England", 7),
    ("just a trip", 7),  # Should default to 7
]

print("Testing duration extraction:\n")
for query, expected in test_cases:
    result = extract_trip_details(query, {})
    extracted_duration = result.get("duration_days", 7)
    status = "✅" if extracted_duration == expected else "❌"
    print(f"{status} '{query}'")
    print(f"   Expected: {expected} days, Got: {extracted_duration} days")
    if extracted_duration != expected:
        print(f"   MISMATCH!")
    print()
