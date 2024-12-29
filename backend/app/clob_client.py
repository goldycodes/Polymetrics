import aiohttp
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import HTTPException

# Configure logging
logger = logging.getLogger(__name__)

class ClobClient:
    """Client for interacting with Polymarket's CLOB API."""
    
    def __init__(self):
        self.base_url = "https://clob.polymarket.com"
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Create aiohttp session when entering context."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close aiohttp session when exiting context."""
        if self.session:
            await self.session.close()
            self.session = None

    async def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make a request to the CLOB API with error handling and logging.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Optional query parameters
            
        Returns:
            Dict containing the response data
            
        Raises:
            HTTPException: If the API request fails
        """
        if not self.session:
            raise RuntimeError("Client session not initialized. Use 'async with' context manager.")
            
        url = f"{self.base_url}/{endpoint}"
        headers = {"Accept": "application/json"}
        
        try:
            logger.debug(f"Making {method} request to {url} with params: {params}")
            async with self.session.request(method, url, params=params, headers=headers) as response:
                response_text = await response.text()
                
                if response.status != 200:
                    logger.error(f"API error: {response.status} - {response_text}")
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"CLOB API error: {response_text}"
                    )
                
                try:
                    data = await response.json()
                    logger.debug(f"Received response: {str(data)[:1000]}...")
                    return data
                except ValueError as e:
                    logger.error(f"Failed to parse JSON response: {str(e)}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Invalid JSON response from CLOB API: {str(e)}"
                    )
                    
        except aiohttp.ClientError as e:
            logger.error(f"Request failed: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail=f"Failed to connect to CLOB API: {str(e)}"
            )

    async def get_markets(
        self,
        page: int = 1,
        limit: int = 10,
        status: str = "active",
        category: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_direction: str = "desc"
    ) -> List[Dict[str, Any]]:
        """
        Get current markets from the CLOB API with filtering and sorting.
        
        Args:
            page: Page number for pagination
            limit: Number of markets per page
            status: Market status filter ('active', 'closed', etc.)
            category: Optional category filter (e.g., 'sports', 'crypto', etc.)
            sort_by: Optional field to sort by (e.g., 'volume')
            sort_direction: Sort direction ('asc' or 'desc')
            
        Returns:
            List of market data dictionaries
        """
        try:
            # Build query parameters
            params = {
                "page": page,
                "limit": limit
            }
            
            # Only include status if explicitly provided
            if status:
                params["status"] = status.lower()
            
            if category:
                params["category"] = category.lower()
                
            logger.debug(f"Requesting markets with params: {params}")
            response = await self._make_request("GET", "markets", params)
            raw_markets = response.get("data", [])
            logger.debug(f"Raw markets sample: {str(raw_markets[:2])}")
            
            logger.info(f"Retrieved {len(raw_markets)} markets from CLOB API")
            
            # Transform markets to match Market interface
            markets = []
            for market in raw_markets:
                try:
                    # Get trader information
                    trades_info = await self.get_market_trades(market["id"])
                    trader_count = trades_info.get("unique_traders", 0)
                    
                    transformed_market = {
                        "id": str(market.get("id", "")),
                        "question": market.get("question", ""),
                        "description": market.get("description"),
                        "volume": str(market.get("volume", "0")),
                        "open_interest": str(market.get("open_interest", "0")),
                        "tokens": [
                            {
                                "token_id": str(token.get("id", "")),
                                "name": token.get("name", ""),
                                "price": str(token.get("price", "0"))
                            }
                            for token in market.get("tokens", [])
                        ],
                        "is_active": market.get("status", "").lower() == "active",
                        "event_status": market.get("status", "unknown"),
                        "created_at": market.get("created_at", ""),
                        "expires_at": market.get("expires_at"),
                        "category": market.get("category", "other"),
                        "trader_count": trader_count
                    }
                    markets.append(transformed_market)
                except Exception as e:
                    logger.error(f"Error transforming market {market.get('id')}: {str(e)}")
                    continue
            
            # Apply sorting if requested
            if sort_by == "volume":
                markets.sort(
                    key=lambda x: float(x.get("volume", "0")),
                    reverse=(sort_direction == "desc")
                )
                
            return markets
            
        except Exception as e:
            logger.error(f"Error fetching markets: {str(e)}")
            raise

    async def get_market_history(
        self,
        market_id: str,
        resolution: str = "1D",
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Get historical data for a specific market.
        
        Args:
            market_id: Market identifier
            resolution: Time resolution for history data
            days: Number of days of history to fetch
            
        Returns:
            Dictionary containing market history data
        """
        try:
            params = {
                "resolution": resolution,
                "from": int((datetime.now() - timedelta(days=days)).timestamp()),
                "to": int(datetime.now().timestamp())
            }
            
            response = await self._make_request("GET", f"history/{market_id}", params)
            logger.info(f"Retrieved history data for market {market_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error fetching market history: {str(e)}")
            raise

    async def get_market_trades(
        self,
        market_id: str,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Get recent trades for a specific market.
        
        Args:
            market_id: Market identifier
            limit: Maximum number of trades to return
            
        Returns: 
            Dictionary containing market trades data
        """
        try: 
            params = {"limit": limit}
            
            response = await self._make_request("GET", f"trades/{market_id}", params)
            trades = response.get("data", [])
            
            # Calculate unique traders
            trader_addresses = set()
            for trade in trades:
                if "maker" in trade:
                    trader_addresses.add(trade["maker"])
                if "taker" in trade:
                    trader_addresses.add(trade["taker"])
                    
            logger.info(f"Retrieved {len(trades)} trades with {len(trader_addresses)} unique traders for market {market_id}")
            return {
                "trades": trades,
                "unique_traders": len(trader_addresses)
            }
            
        except Exception as e:
            logger.error(f"Error fetching market trades: {str(e)}")
            raise
