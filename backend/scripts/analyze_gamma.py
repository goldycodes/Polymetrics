import json
import sys
from typing import Dict, List, Any

def analyze_sports_events(data: List[Dict[str, Any]]) -> None:
    """Analyze events from Gamma API for sports-related content."""
    print(f"\nTotal events: {len(data)}")
    
    # Define sports-related keywords
    sports_keywords = {
        'leagues': ['nfl', 'nba', 'mlb', 'nhl', 'ncaa', 'ufc'],
        'sports': ['soccer', 'football', 'basketball', 'baseball', 'tennis', 'hockey'],
        'teams': [
            'lakers', 'warriors', 'celtics', 'bulls', 'nets',
            'patriots', 'cowboys', 'eagles', 'chiefs', '49ers'
        ]
    }
    
    # Find sports events
    sports_events = []
    for event in data:
        question = event.get('question', '').lower()
        if any(kw in question for cat in sports_keywords.values() for kw in cat):
            sports_events.append(event)
    
    print(f"\nPotential sports events found: {len(sports_events)}")
    
    if sports_events:
        print("\nTop 3 sports events:")
        for i, event in enumerate(sorted(sports_events, 
                                      key=lambda x: float(x.get('volume', 0)), 
                                      reverse=True)[:3], 1):
            print(f"\n{i}. Question: {event.get('question')}")
            print(f"   Volume: {event.get('volume', 'N/A')}")
            print(f"   Open Interest: {event.get('openInterest', 'N/A')}")
            
            # Print matched keywords
            keywords_found = set()
            for cat, keywords in sports_keywords.items():
                matches = [kw for kw in keywords if kw in event.get('question', '').lower()]
                if matches:
                    keywords_found.update(matches)
            print(f"   Sports keywords found: {', '.join(keywords_found)}")

def main():
    try:
        data = json.load(sys.stdin)
        analyze_sports_events(data)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error processing data: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
