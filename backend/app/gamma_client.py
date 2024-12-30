import aiohttp
import logging
from typing import List, Dict, Any, Optional
from app.models import EventMarket

logger = logging.getLogger(__name__)

SPORTS_KEYWORDS = [
    # Leagues
    'nfl', 'nba', 'mlb', 'nhl', 'ncaa', 'ufc',
    # Sports
    'soccer', 'football', 'basketball', 'baseball',
    'tennis', 'hockey', 'mma', 'boxing', 'rugby',
    # General terms
    'championship', 'league', 'team', 'match',
    'game', 'tournament', 'sports', 'playoff',
    'finals', 'super bowl', 'world cup', 'score',
    # NBA Teams
    'lakers', 'warriors', 'celtics', 'bulls', 'nets',
    'knicks', 'heat', 'suns', 'mavericks', 'clippers',
    # NFL Teams
    'patriots', 'cowboys', 'eagles', 'chiefs', '49ers',
    'packers', 'steelers', 'ravens', 'broncos', 'raiders',
    # Soccer Teams/Leagues
    'premier league', 'la liga', 'bundesliga',
    'manchester united', 'liverpool', 'arsenal',
    'real madrid', 'barcelona', 'bayern',
    # Betting terms
    'win', 'points', 'score', 'odds', 'spread',
    'moneyline', 'over/under', 'prop', 'parlay'
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
        
        # Group keywords by category
        league_keywords = {'nfl', 'nba', 'mlb', 'nhl', 'ncaa', 'ufc', 'premier league', 'la liga', 'bundesliga'}
        team_keywords = {
            'lakers', 'warriors', 'celtics', 'bulls', 'nets', 'knicks', 'heat', 'suns', 'mavericks', 'clippers',
            'patriots', 'cowboys', 'eagles', 'chiefs', '49ers', 'packers', 'steelers', 'ravens', 'broncos', 'raiders',
            'manchester united', 'liverpool', 'arsenal', 'real madrid', 'barcelona', 'bayern'
        }
        sport_keywords = {'soccer', 'football', 'basketball', 'baseball', 'tennis', 'hockey', 'mma', 'boxing', 'rugby'}
        
        # Check for strong indicators (league or team names)
        text = f"{question} {description}".lower()  # Ensure case-insensitive matching
        logger.debug(f"Checking text for sports keywords: {text}")
        
        league_matches = {kw for kw in league_keywords if kw in text}
        team_matches = {kw for kw in team_keywords if kw in text}  # Fixed: was using team_matches instead of team_keywords
        sport_matches = {kw for kw in sport_keywords if kw in text}
        
        logger.debug(f"Found league matches: {league_matches}")
        logger.debug(f"Found team matches: {team_matches}")
        logger.debug(f"Found sport matches: {sport_matches}")
        
        # If we find a league or team name, it's definitely a sports market
        if league_matches or team_matches:
            logger.info(f"Sports market found! League keywords: {league_matches}, Team keywords: {team_matches}")
            logger.info(f"Question: {question}")
            return True
            
        # If we find a sport name and some context, it's probably a sports market
        if sport_matches and any(kw in text for kw in ['match', 'game', 'score', 'win', 'championship', 'tournament']):
            logger.info(f"Sports market found! Sport keywords: {sport_matches}")
            logger.info(f"Question: {question}")
            return True
            
        logger.debug(f"No sports keywords found in market")
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
