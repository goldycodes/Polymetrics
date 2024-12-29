from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from enum import Enum
import aiohttp
import logging

class SortDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"

class MarketCategory(str, Enum):
    SPORTS = "sports"
    CRYPTO = "crypto"
    POLITICS = "politics"
    ENTERTAINMENT = "entertainment"
    OTHER = "other"

class SortBy(str, Enum):
    VOLUME = "volume"
    CREATED_AT = "created_at"

from .polymarket_graphql import PolymarketGraphQLClient
from .gamma_client import GammaClient
from .clob_client import ClobClient
from .models import EventMarket

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize clients
polymarket_client = PolymarketGraphQLClient()
gamma_client = GammaClient()
clob_client = ClobClient()

app = FastAPI()

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/gamma/markets", response_model=List[EventMarket])
async def get_gamma_markets(current_only: bool = True):
    """
    Get markets from Gamma API.
    
    Args:
        current_only (bool): If True, return only current (non-closed) markets. Defaults to True.
        
    Returns:
        List[EventMarket]: List of markets with their details
    """
    try:
        events = await gamma_client.fetch_events(closed=not current_only)
        return events
    except Exception as e:
        logger.error(f"Error in get_gamma_markets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/markets")
async def get_markets():
    """Get all active markets from Polymarket."""
    try:
        async with polymarket_client as client:
            markets = await client.fetch_current_markets()
            if not markets:
                return []
            return markets
    except Exception as e:
        logger.error(f"Error in get_markets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/markets/{market_id}/orders")
async def get_market_orders(market_id: str):
    """Get order book data for a specific market."""
    try:
        async with polymarket_client as client:
            orders = await client.get_market_open_interest(market_id)
            if orders is None:
                return {}
            return {"open_interest": orders}
    except Exception as e:
        logger.error(f"Error in get_market_orders: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/clob/markets")
async def get_clob_markets(
    page: int = 1,
    limit: int = 10,
    status: str = "active",
    category: Optional[MarketCategory] = None,
    sort_by: Optional[SortBy] = None,
    sort_direction: SortDirection = SortDirection.DESC
):
    """
    Get markets from CLOB API with pagination, filtering, and sorting.
    
    Args:
        page: Page number for pagination
        limit: Number of items per page
        status: Market status filter ('active', 'closed', etc.)
        category: Optional category filter
        sort_by: Optional field to sort by
        sort_direction: Sort direction (asc/desc)
    """
    try:
        async with clob_client as client:
            markets = await client.get_markets(
                page=page,
                limit=limit,
                status=status,
                category=category.value if category else None,
                sort_by=sort_by.value if sort_by else None,
                sort_direction=sort_direction.value
            )
            return markets
    except Exception as e:
        logger.error(f"Error in get_clob_markets: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/clob/markets/{market_id}/history")
async def get_clob_market_history(
    market_id: str,
    resolution: str = "1D",
    days: int = 7
):
    """Get historical data for a specific CLOB market."""
    try:
        async with clob_client as client:
            history = await client.get_market_history(
                market_id=market_id,
                resolution=resolution,
                days=days
            )
            return history
    except Exception as e:
        logger.error(f"Error in get_clob_market_history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/clob/markets/{market_id}/trades")
async def get_clob_market_trades(
    market_id: str,
    limit: int = 100
):
    """Get recent trades for a specific CLOB market."""
    try:
        async with clob_client as client:
            trades = await client.get_market_trades(
                market_id=market_id,
                limit=limit
            )
            return trades
    except Exception as e:
        logger.error(f"Error in get_clob_market_trades: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
