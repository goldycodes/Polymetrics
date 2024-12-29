import aiohttp
import logging
from typing import List, Dict, Any, Optional
from app.models import EventMarket

logger = logging.getLogger(__name__)

SPORTS_KEYWORDS = [
    # Leagues
    'nfl', 'nba', 'mlb', 'nhl', 'mls',
    'premier league', 'la liga', 'bundesliga', 'serie a',
    
    # Sports
    'soccer', 'football', 'basketball', 'baseball',
    'tennis', 'hockey', 'golf', 'boxing', 'ufc',
    'racing', 'formula 1', 'f1', 'nascar',
    
    # Events
    'championship', 'league', 'tournament',
    'match', 'game', 'playoff', 'playoffs',
    'world cup', 'finals', 'super bowl',
    'all-star', 'all star', 'draft',
    
    # NFL Teams
    'bills', 'dolphins', 'patriots', 'jets',
    'ravens', 'bengals', 'browns', 'steelers',
    'titans', 'colts', 'texans', 'jaguars',
    'chiefs', 'raiders', 'chargers', 'broncos',
    'cowboys', 'eagles', 'commanders', 'giants',
    'vikings', 'packers', 'bears', 'lions',
    'buccaneers', 'saints', 'falcons', 'panthers',
    '49ers', 'seahawks', 'rams', 'cardinals',
    
    # NBA Teams
    'celtics', 'nets', 'knicks', 'raptors',
    'bucks', 'cavaliers', 'hawks', 'heat',
    'warriors', 'clippers', 'suns', 'lakers',
    'nuggets', 'timberwolves', 'thunder', 'jazz',
    
    # General Terms
    'score', 'win', 'winner', 'champion',
    'roster', 'trade', 'transfer', 'season',
    'coach', 'player', 'team', 'sports'
]

class GammaClient:
    """Client for interacting with Polymarket's Gamma API."""

    @staticmethod
    def is_sports_market(event: Dict[str, Any]) -> bool:
        """
        Check if an event is sports-related based on its question and description.
        
        Args:
            event (Dict[str, Any]): Event data from EventMarket model
            
        Returns:
            bool: True if the event is sports-related, False otherwise
        """
        # Log the event structure for debugging
        logger.debug(f"Checking event data: {event}")
        
        # Check question and description fields (title is mapped to question in EventMarket)
        question = str(event.get('question', '')).lower()
        description = str(event.get('description', '')).lower()
        
        # Log the extracted fields
        logger.debug(f"Checking question: {question}")
        logger.debug(f"Checking description: {description}")
        
        # Check both fields for sports keywords
        is_sports = any(keyword in question or keyword in description for keyword in SPORTS_KEYWORDS)
        if is_sports:
            logger.info(f"Found sports market - Question: {question}, Description: {description}")
        return is_sports
    
    def __init__(self):
        self.base_url = "https://gamma-api.polymarket.com"
    
    async def fetch_events(self, closed: bool = False) -> List[EventMarket]:
        """
        Fetch events from Gamma API.
        
        Args:
            closed (bool): If True, include closed events. Defaults to False.
            
        Returns:
            List[EventMarket]: List of events with market details
        """
        url = f"{self.base_url}/events"
        if not closed:
            url += "?closed=false"
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    events_data = await response.json()
                    if not isinstance(events_data, list):
                        events_data = []
                    
                    # Log raw event data before conversion
                    logger.debug("Raw events data from Gamma API:")
                    for event in events_data:
                        logger.debug(f"Raw event data:")
                        logger.debug(f"  ID: {event.get('id')}")
                        logger.debug(f"  Title: {event.get('title')}")
                        logger.debug(f"  Description: {event.get('description')}")
                        logger.debug(f"  Status: {event.get('status')}")
                        logger.debug("---")
                    
                    events = []
                    for event in events_data:
                        market = EventMarket.from_gamma_event(event)
                        logger.debug(f"Converted market {market.id}:")
                        logger.debug(f"  Question: {market.question}")
                        logger.debug(f"  Description: {market.description}")
                        logger.debug(f"  Active: {market.is_active}")
                        events.append(market)
                    logger.debug(f"Fetched and converted {len(events)} events from Gamma API")
                    return events
        except aiohttp.ClientError as e:
            logger.error(f"Error fetching events from Gamma API: {str(e)}")
            raise
            
    async def fetch_event_by_id(self, event_id: str) -> Optional[EventMarket]:
        """
        Fetch a specific event by ID.
        
        Args:
            event_id (str): The ID of the event to fetch
            
        Returns:
            Optional[EventMarket]: Event data if found, None otherwise
        """
        url = f"{self.base_url}/events/{event_id}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status in (404, 422):
                        return None
                    response.raise_for_status()
                    event_data = await response.json()
                    return EventMarket.from_gamma_event(event_data)
        except aiohttp.ClientError as e:
            logger.error(f"Error fetching event {event_id} from Gamma API: {str(e)}")
            raise

    async def fetch_sports_markets(self, closed: bool = False) -> List[EventMarket]:
        """
        Fetch and filter sports-related markets from Gamma API, sorted by open interest.
        
        Args:
            closed (bool): If True, include closed events. Defaults to False.
            
        Returns:
            List[EventMarket]: List of sports-related events sorted by open interest (descending)
        """
        url = f"{self.base_url}/events"
        if not closed:
            url += "?closed=false"
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    response.raise_for_status()
                    events_data = await response.json()
                    if not isinstance(events_data, list):
                        events_data = []
                    
                    # Filter sports events from raw data before conversion
                    sports_events_data = [
                        event for event in events_data 
                        if self.is_sports_market(event)
                    ]
                    
                    # Convert filtered events to EventMarket objects
                    sports_events = [
                        EventMarket.from_gamma_event(event)
                        for event in sports_events_data
                    ]
                    
                    # Sort by open interest (descending)
                    sports_events.sort(
                        key=lambda e: float(e.open_interest or 0), 
                        reverse=True
                    )
                    
                    logger.info(f"Found {len(sports_events)} sports markets")
                    return sports_events
            
        except Exception as e:
            logger.error(f"Error fetching sports markets: {str(e)}")
            raise
