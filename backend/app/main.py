from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import aiohttp
import logging

from .polymarket_graphql import PolymarketGraphQLClient
from .gamma_client import GammaClient
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
