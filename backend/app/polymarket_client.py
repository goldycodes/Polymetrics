import aiohttp
import json
import time
from typing import List, Dict, Any
import logging
from fastapi import HTTPException
from datetime import datetime, timezone, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PolymarketClient:
    """Client for interacting with Polymarket's public APIs."""
    
    GRAPHQL_URL = "https://subgraph.satsuma-prod.com/f5c1a7dd3ab7/polymarket/matic-markets/api"
    SATSUMA_URL = "https://subgraph.satsuma-prod.com/f5c1a7dd3ab7/polymarket/matic-markets/api"
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def get_markets(self) -> List[Dict[str, Any]]:
        """Fetch all current and live markets from Polymarket using GraphQL."""
        query = """
        query {
            fixedProductMarketMakers(first: 100, orderBy: creationTimestamp, orderDirection: desc) {
                id
                creationTimestamp
                lastActiveDay
                collateralVolume
                scaledCollateralVolume
                outcomeTokenPrices
                tradesQuantity
                condition {
                    id
                    question
                    resolutionTimestamp
                    resolved
                }
            }
        }
        """
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.SATSUMA_URL,
                    json={"query": query},
                    headers={
                        "Content-Type": "application/json",
                        "User-Agent": "PolymarketDashboard/1.0"
                    },
                    timeout=30
                ) as response:
                    if response.status != 200:
                        logger.error(f"GraphQL request failed: {response.status}")
                        return []

                    data = await response.json()
                    logger.info(f"Fetching markets via GraphQL")
                    logger.debug(f"GraphQL Response: {json.dumps(data)[:1000]}")

                    if "data" not in data or "fixedProductMarketMakers" not in data["data"]:
                        logger.error("Invalid GraphQL response format")
                        return []

                    markets = []
                    now = datetime.now(timezone.utc)

                    for market in data["data"]["fixedProductMarketMakers"]:
                        try:
                            if not market["condition"]:
                                continue

                            condition = market["condition"]
                            end_time = datetime.fromtimestamp(int(condition["resolutionTimestamp"]), timezone.utc)

                            # Only include markets that:
                            # 1. Are not resolved
                            # 2. Have not ended
                            if not condition["resolved"] and end_time > now:
                                transformed_market = {
                                    "id": market["id"],
                                    "question": condition["question"],
                                    "description": "",  # Not available in GraphQL
                                    "end_date": end_time.isoformat(),
                                    "volume": float(market["scaledCollateralVolume"]),
                                    "open_interest": float(market["collateralVolume"]),
                                    "trader_count": int(market["tradesQuantity"]),
                                    "outcomes": [
                                        {"price": float(price)} 
                                        for price in market["outcomeTokenPrices"]
                                    ],
                                    "status": "active" if not condition["resolved"] else "resolved",
                                    "active": True,
                                    "accepting_orders": True
                                }
                                markets.append(transformed_market)
                        except Exception as e:
                            logger.error(f"Error processing market: {e}")
                            continue

                    logger.info(f"Found {len(markets)} active markets")
                    return markets

        except Exception as e:
            logger.error(f"Error in get_markets: {e}")
            return []
            


    async def get_market_orders(self, market_id: str) -> Dict[str, Any]:
        """Fetch order book data for a specific market using GraphQL."""
        query = """
        query($marketId: String!) {
            fixedProductMarketMaker(id: $marketId) {
                id
                collateralVolume
                scaledCollateralVolume
                outcomeTokenPrices
                tradesQuantity
                condition {
                    id
                    question
                    resolutionTimestamp
                    resolved
                }
            }
        }
        """
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.SATSUMA_URL,
                    json={
                        "query": query,
                        "variables": {"marketId": market_id}
                    },
                    headers={
                        "Content-Type": "application/json",
                        "User-Agent": "PolymarketDashboard/1.0"
                    },
                    timeout=30
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise HTTPException(
                            status_code=response.status,
                            detail=f"Error from Polymarket API: {error_text}"
                        )
                        
                    data = await response.json()
                    if "data" not in data or "fixedProductMarketMaker" not in data["data"]:
                        raise HTTPException(
                            status_code=404,
                            detail="Market not found"
                        )
                        
                    market = data["data"]["fixedProductMarketMaker"]
                    return {
                        "id": market["id"],
                        "volume": float(market["scaledCollateralVolume"]),
                        "open_interest": float(market["collateralVolume"]),
                        "trader_count": int(market["tradesQuantity"]),
                        "prices": market["outcomeTokenPrices"]
                    }
                    
        except Exception as e:
            logger.error(f"Error fetching market orders: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error fetching market orders: {str(e)}"
            )

polymarket = PolymarketClient()
