import aiohttp
import logging
from typing import List, Dict, Any, Optional
from app.models import EventMarket

logger = logging.getLogger(__name__)

SPORTS_KEYWORDS = [
    # Leagues with full names
    'national football league', 'national basketball association',
    'major league baseball', 'national hockey league',
    'ultimate fighting championship',
    # League abbreviations
    'nfl', 'nba', 'mlb', 'nhl', 'ncaa', 'ufc', 'pga',
    # Sports
    'football', 'basketball', 'baseball', 'hockey',
    'soccer', 'tennis', 'golf', 'boxing', 'mma',
    # Specific sports terms
    'touchdown', 'field goal', 'quarterback', 'rushing',
    'three pointer', 'slam dunk', 'home run', 'pitcher',
    'goal keeper', 'penalty kick', 'grand slam',
    # Team identifiers
    'team', 'roster', 'coach', 'player', 'draft',
    # Event types
    'game', 'match', 'tournament', 'championship',
    'playoff', 'finals', 'super bowl', 'world cup',
    'world series', 'all star game',
    # NBA Teams (full names)
    'los angeles lakers', 'golden state warriors',
    'boston celtics', 'chicago bulls', 'brooklyn nets',
    'new york knicks', 'miami heat', 'phoenix suns',
    # NFL Teams (full names)
    'new england patriots', 'dallas cowboys',
    'philadelphia eagles', 'kansas city chiefs',
    'san francisco 49ers', 'green bay packers',
    'pittsburgh steelers', 'baltimore ravens',
    # Soccer Teams/Leagues (full names)
    'english premier league', 'la liga',
    'manchester united', 'liverpool fc',
    'real madrid', 'barcelona'
]

class GammaClient:
    """Client for interacting with Polymarket's Gamma API."""

    @staticmethod
    def is_sports_market(event: Dict[str, Any] | EventMarket) -> bool:
        """
        Check if an event is sports-related based on its title/question.
        
        Args:
            event (Dict[str, Any] | EventMarket): Event data from Gamma API or EventMarket model
            
        Returns:
            bool: True if the event is sports-related, False otherwise
        """
        # Handle both dict and EventMarket types
        if isinstance(event, EventMarket):
            question = event.question.lower() if event.question else ''
            description = event.description.lower() if event.description else ''
        else:
            question = event.get('question', '').lower()
            description = event.get('description', '').lower()
            
        logger.debug(f"Checking if market is sports-related - Question: {question}")
        logger.debug(f"Description: {description}")
        
        # Use global SPORTS_KEYWORDS list
        keywords = set(SPORTS_KEYWORDS)  # Convert to set for faster lookups
        logger.debug(f"Using {len(keywords)} sports-related keywords")
        
        # Check for strong indicators (league or team names)
        text = f"{question} {description}".lower()  # Ensure case-insensitive matching
        words = set(text.split())  # Split into words for partial matching
        logger.info(f"Checking text for sports keywords: {text}")
        logger.info(f"Words found in text: {words}")
        
        # Split keywords that contain spaces into separate terms
        expanded_keywords = set()
        for kw in keywords:
            if ' ' in kw:
                # For multi-word keywords, check if the entire phrase is in the text
                if kw.lower() in text:
                    logger.info(f"Found multi-word match: {kw}")
                    expanded_keywords.add(kw)
            else:
                # For single words, check if they appear as whole words
                word_pattern = f"\\b{kw.lower()}\\b"
                if any(word.lower() == kw.lower() for word in words):
                    logger.info(f"Found single-word match: {kw}")
                    expanded_keywords.add(kw)
        
        # Check for exact word matches
        matches = expanded_keywords
        
        logger.info(f"Found keyword matches: {matches}")
        
        # Temporarily reduce requirement to 1 match for testing
        if len(matches) >= 1:
            logger.info(f"Sports market found! Keywords: {matches}")
            logger.info(f"Question: {question}")
            return True
            
        logger.debug(f"No sports keywords found in market (or insufficient matches)")
        return False
    
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
                    
                    events = []
                    for event in events_data:
                        market = EventMarket.from_gamma_event(event)
                        logger.debug(f"Market {market.id} active status: {market.is_active}")
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
        try:
            logger.info("Fetching sports markets...")
            # Fetch all events first
            events = await self.fetch_events(closed=closed)
            logger.info(f"Fetched {len(events)} total events")
            
            # Filter sports events and convert to list for sorting
            sports_events = []
            for event in events:
                logger.debug(f"Processing event: {event.question}")
                if self.is_sports_market(event):
                    sports_events.append(event)
            
            # Sort by open interest (descending)
            sports_events.sort(
                key=lambda e: float(e.open_interest or 0), 
                reverse=True
            )
            
            logger.info(f"Found {len(sports_events)} sports markets")
            if sports_events:
                logger.info("Top sports markets:")
                for idx, event in enumerate(sports_events[:3], 1):
                    logger.info(f"{idx}. {event.question} (Open Interest: {event.open_interest})")
            return sports_events
            
        except Exception as e:
            logger.error(f"Error fetching sports markets: {str(e)}")
            logger.exception("Full traceback:")
            return []
