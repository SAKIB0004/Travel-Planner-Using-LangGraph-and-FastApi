#!/usr/bin/env python
"""Display full polished narrative output"""

from app.utils.helpers import sanitize_value, create_polished_response

trip_info = {
    'destination': 'Japan',
    'cities': ['Tokyo', 'Osaka'],
    'duration_days': 10,
    'budget': 'mid-range',
    'travel_month': 'October',
    'travel_style': 'cultural',
    'interests': ['culture', 'history'],
}

agent_outputs = {
    'destination': {
        'summary': 'Japan is a wonderful cultural destination with a perfect blend of ancient traditions and modern innovation.',
        'highlights': ['Senso-ji Temple in Tokyo (oldest temple)', 'Arashiyama Bamboo Grove', 'Hiroshima Peace Memorial'],
        'transport': 'Excellent public transit with JR and subway systems',
        'safety': 'Very safe with low crime rates'
    },
    'transportation': {
        'summary': 'Efficient and well-connected transportation network.',
        'international_flights': 'Round-trip flights from US typically range $650–$1,050 depending on departure city and booking timing',
        'local_transportation': {
            'options': ['JR Pass', 'Suica Card', 'Subway'],
            'daily_cost': 18,
            'tips': ['Buy Suica IC card at Tokyo Station for all transit', 'Use JR Pass for Shinkansen between Tokyo and Osaka']
        }
    },
    'accommodation': {
        'summary': 'Wide range of high-quality accommodation options at all price points.',
        'by_city': {
            'Tokyo': {
                'recommended_neighborhoods': [
                    {'name': 'Asakusa', 'description': 'ideal for traditional atmosphere, temple access, and slower-paced evenings'},
                    {'name': 'Ueno', 'description': 'good for museums, parks, and practical train connections'},
                    {'name': 'Ginza', 'description': 'a polished central base with easy city access'}
                ],
                'min_price': 100,
                'max_price': 160
            },
            'Osaka': {
                'recommended_neighborhoods': [
                    {'name': 'Namba', 'description': 'lively, convenient, and great for local food culture'},
                    {'name': 'Umeda', 'description': 'useful for rail connections and a more polished city base'},
                    {'name': 'Tennoji', 'description': 'often a practical mid-range option with good transport links'}
                ],
                'min_price': 85,
                'max_price': 145
            }
        }
    },
    'budget': {
        'summary': 'Daily budget: $80–$120 recommended for comfortable mid-range travel.',
        'daily_estimate': '$100/day average',
        'money_tips': ['Use JR Pass for long-distance trains', 'Eat at local restaurants in residential areas for cheaper meals']
    },
    'weather': {
        'summary': 'October offers ideal conditions with mild temperatures 64–75°F, comfortable walking weather, and low rainfall.',
        'weather_expectations': ['18–24°C (64–75°F)', 'Low rainfall, clear skies'],
        'packing_suggestions': ['Light layers', 'Thin sweater or jacket', 'Comfortable walking shoes', 'Compact umbrella'],
        'activity_advice': ['Perfect for hiking and outdoor activities', 'Ideal for exploring temples and gardens']
    },
    'culture': {
        'summary': 'Japanese culture emphasizes respect, harmony, and attention to detail.',
        'etiquette': [
            'Keep your voice low on trains and avoid phone calls in crowded carriages',
            'Follow queue order carefully in stations, elevators, and shops',
            'Check signs before taking photos inside temples, shrines, or museums',
            'Do not tip—service is included'
        ],
        'essential_language_phrases': [
            {'phrase': 'Sumimasen', 'meaning': 'Excuse me / Sorry', 'usage_context': 'getting attention or apologizing'},
            {'phrase': 'Arigatou gozaimasu', 'meaning': 'Thank you (formal)', 'usage_context': 'in shops and restaurants'},
            {'phrase': 'Eki wa doko desu ka?', 'meaning': 'Where is the station?', 'usage_context': 'asking for directions'},
            {'phrase': 'Kore wa ikura desu ka?', 'meaning': 'How much is this?', 'usage_context': 'asking prices'},
        ],
        'behavior_tips': ['Slurp noodles to show appreciation', 'Bow slightly when greeting or leaving']
    }
}

print("\n" + "="*70)
narrative = create_polished_response(trip_info, agent_outputs, include_raw=False)
print(narrative)
print("="*70)
print(f"\n✅ Output quality test complete ({len(narrative)} characters)")
