import pytest
from app.gamma_client import GammaClient
from app.models import EventMarket, MarketToken
import aiohttp
from unittest.mock import patch, MagicMock

SAMPLE_EVENT = {
    "id": "test-event-1",
    "title": "Will X happen?",
    "description": "Test description",
    "volume": "1000",
    "liquidity": "500",
    "status": "open",
    "created_at": "2024-01-01T00:00:00Z",
    "expires_at": "2024-12-31T23:59:59Z",
    "outcomes": [
        {
            "id": "token-1",
            "title": "Yes",
            "probability": "0.75"
        },
        {
            "id": "token-2",
            "title": "No",
            "probability": "0.25"
        }
    ]
}

@pytest.mark.asyncio
async def test_fetch_events():
    client = GammaClient()
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status = 200
        async def mock_json():
            return [SAMPLE_EVENT]
        mock_response.json = mock_json
        mock_get.return_value.__aenter__.return_value = mock_response
        
        events = await client.fetch_events()
        assert isinstance(events, list)
        assert len(events) == 1
        event = events[0]
        assert isinstance(event, EventMarket)
        assert event.id == "test-event-1"
        assert event.question == "Will X happen?"
        assert event.volume == "1000"
        assert event.open_interest == "500"
        assert len(event.tokens) == 2
        assert isinstance(event.tokens[0], MarketToken)
        assert event.tokens[0].token_id == "token-1"
        assert event.tokens[0].price == "0.75"

@pytest.mark.asyncio
async def test_fetch_events_closed_param():
    client = GammaClient()
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status = 200
        async def mock_json():
            return [SAMPLE_EVENT]
        mock_response.json = mock_json
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Test with closed=True
        events = await client.fetch_events(closed=True)
        assert isinstance(events, list)
        assert len(events) == 1
        assert all(isinstance(event, EventMarket) for event in events)
        
        # Test with closed=False
        events = await client.fetch_events(closed=False)
        assert isinstance(events, list)
        assert len(events) == 1
        assert all(isinstance(event, EventMarket) for event in events)

@pytest.mark.asyncio
async def test_fetch_event_by_id():
    client = GammaClient()
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status = 200
        async def mock_json():
            return SAMPLE_EVENT
        mock_response.json = mock_json
        mock_get.return_value.__aenter__.return_value = mock_response
        
        event = await client.fetch_event_by_id("test-event-1")
        assert event is not None
        assert isinstance(event, EventMarket)
        assert event.id == "test-event-1"
        assert event.question == "Will X happen?"
        assert len(event.tokens) == 2
        assert event.tokens[0].price == "0.75"

@pytest.mark.asyncio
async def test_fetch_nonexistent_event():
    client = GammaClient()
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status = 422
        mock_get.return_value.__aenter__.return_value = mock_response
        
        event = await client.fetch_event_by_id('nonexistent-id')
        assert event is None

SAMPLE_SPORTS_EVENTS = [
    {
        "id": "nfl-event-1",
        "title": "NFL Super Bowl 2025: Which team will win?",
        "description": "Test NFL description",
        "volume": "10000",
        "liquidity": "5000",
        "status": "open",
        "created_at": "2024-01-01T00:00:00Z",
        "expires_at": "2025-02-15T23:59:59Z",
        "outcomes": [
            {"id": "token-1", "title": "Team A", "probability": "0.60"},
            {"id": "token-2", "title": "Team B", "probability": "0.40"}
        ]
    },
    {
        "id": "nba-event-1",
        "title": "NBA Finals 2024",
        "description": "Test NBA description",
        "volume": "8000",
        "liquidity": "4000",
        "status": "open",
        "created_at": "2024-01-01T00:00:00Z",
        "expires_at": "2024-06-30T23:59:59Z",
        "outcomes": [
            {"id": "token-3", "title": "Team C", "probability": "0.55"},
            {"id": "token-4", "title": "Team D", "probability": "0.45"}
        ]
    },
    {
        "id": "non-sports-event",
        "title": "Random Political Event",
        "description": "Non-sports event",
        "volume": "12000",
        "liquidity": "6000",
        "status": "open",
        "created_at": "2024-01-01T00:00:00Z",
        "expires_at": "2024-12-31T23:59:59Z",
        "outcomes": [
            {"id": "token-5", "title": "Yes", "probability": "0.70"},
            {"id": "token-6", "title": "No", "probability": "0.30"}
        ]
    }
]

@pytest.mark.asyncio
async def test_fetch_sports_markets():
    """Test fetching and filtering of sports markets."""
    client = GammaClient()
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status = 200
        async def mock_json():
            return SAMPLE_SPORTS_EVENTS
        mock_response.json = mock_json
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Fetch sports markets
        sports_markets = await client.fetch_sports_markets()
        
        # Basic validation
        assert sports_markets is not None
        assert isinstance(sports_markets, list)
        assert len(sports_markets) == 2  # Should only get NFL and NBA events
        
        # Verify all returned markets are sports-related
        for market in sports_markets:
            assert isinstance(market, EventMarket)
            question = market.question.lower()
            assert any(keyword in question for keyword in [
                'nfl', 'nba', 'mlb', 'nhl', 'soccer', 'football',
                'basketball', 'baseball', 'tennis', 'hockey',
                'sports', 'team', 'league', 'playoff'
            ]), f"Market {market.id} does not appear to be sports-related"
        
        # Verify sorting by open interest (descending)
        for i in range(len(sports_markets) - 1):
            current_interest = float(sports_markets[i].open_interest or 0)
            next_interest = float(sports_markets[i + 1].open_interest or 0)
            assert current_interest >= next_interest, "Markets not properly sorted by open interest"

@pytest.mark.asyncio
async def test_fetch_sports_markets_empty():
    """Test handling of no sports markets found."""
    client = GammaClient()
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status = 200
        async def mock_json():
            return [SAMPLE_EVENT]  # Use non-sports event from original tests
        mock_response.json = mock_json
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Fetch sports markets when none exist
        sports_markets = await client.fetch_sports_markets()
        
        # Verify empty list handling
        assert sports_markets is not None
        assert isinstance(sports_markets, list)
        assert len(sports_markets) == 0
