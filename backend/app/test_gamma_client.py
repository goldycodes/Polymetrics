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
