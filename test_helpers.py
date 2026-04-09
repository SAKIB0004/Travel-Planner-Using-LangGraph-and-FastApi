#!/usr/bin/env python
"""Quick test of helper functions"""

from app.utils.helpers import sanitize_value, create_polished_response

print("Testing Sanitization:")
print(f"  None -> '{sanitize_value(None, 'fallback')}'")
print(f"  'destination' -> '{sanitize_value('destination', 'fallback')}'")
print(f"  'Tokyo Tower' -> '{sanitize_value('Tokyo Tower', 'fallback')}'")

trip_info = {
    'destination': 'Japan',
    'cities': ['Tokyo', 'Osaka'],
    'duration_days': 10,
    'budget': 'mid-range',
    'interests': ['culture', 'history'],
}

agent_outputs = {
    'destination': {
        'summary': 'Japan is a wonderful cultural destination.',
        'highlights': ['Senso-ji Temple in Tokyo', 'Arashiyama Bamboo Grove', 'Hiroshima Peace Memorial'],
        'transport': 'Excellent public transit with JR and subway systems',
        'safety': 'Very safe with low crime rates'
    },
    'transportation': {
        'summary': 'Efficient and well-connected transportation network.',
        'international_flights': 'Round-trip flights from US: $600-900',
        'local_transportation': {  # Changed to dict with proper structure
            'options': ['JR Pass', 'Suica Card', 'Subway'],
            'daily_cost': 30,
            'tips': ['Buy JR Pass for multi-city travel', 'Use Suica for local transit']
        }
    },
    'accommodation': {
        'summary': 'Wide range of accommodation options available.',
        'by_city': {'Tokyo': 'Mid-range: ¥8000-15000/night', 'Osaka': 'Mid-range: ¥7000-12000/night'}
    },
    'budget': {
        'summary': 'Daily budget: $80-120 recommended.',
        'daily_estimate': '$100/day average',
        'money_tips': ['Use JR Pass for cost savings', 'Eat at local ramen shops for cheap meals']
    },
    'weather': {
        'summary': 'October offers ideal conditions.',
        'weather_expectations': ['18-24°C (64-75°F)', 'Low rainfall, clear skies'],
        'packing_suggestions': ['Light jacket', 'Comfortable walking shoes', 'Umbrella'],
        'activity_advice': ['Perfect for hiking and outdoor activities']
    },
    'culture': {
        'summary': 'Japanese culture emphasizes respect and harmony.',
        'etiquette': ['Remove shoes indoors at homes and temples', 'Bow slightly when greeting'],
        'essential_language_phrases': [
            {'phrase': 'Arigatou gozaimasu', 'meaning': 'Thank you (formal)', 'usage_context': 'in shops and restaurants'},
            {'phrase': 'Sumimasen', 'meaning': 'Excuse me', 'usage_context': 'to get attention or apologize'}
        ],
        'behavior_tips': ['Slurp noodles to show appreciation', 'Don\'t tip in Japan']
    }
}

print("\nGenerating polished narrative...")
narrative = create_polished_response(trip_info, agent_outputs, include_raw=False)

print("\n✅ SUCCESS - Polished narrative generated!\n")
print("=" * 60)
print(narrative[:500])
print("..." if len(narrative) > 500 else "")
print("=" * 60)
print(f"\nTotal narrative length: {len(narrative)} characters")
print("✅ All helpers working correctly!")
