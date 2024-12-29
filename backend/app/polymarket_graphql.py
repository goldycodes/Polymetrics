import logging
from typing import Dict, List, Optional
import aiohttp
from datetime import datetime, timezone
from .config import settings

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PolymarketGraphQLClient:
    """Client for interacting with Polymarket's GraphQL APIs"""
    
    CLOB_API_URL = "https://clob.polymarket.com"
    WSS_API_URL = "wss://ws-subscriptions-clob.polymarket.com/ws/"
    
    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        self._session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()
            
    async def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, data: Optional[Dict] = None) -> Dict:
        """Make a request to the CLOB API"""
        if not self._session:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")
            
        try:
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            
            url = f"{self.CLOB_API_URL}/{endpoint}"
            async with self._session.request(
                method,
                url,
                params=params,
                json=data,
                headers=headers,
                timeout=settings.request_timeout
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"CLOB API request failed: {response.status}\nResponse: {error_text}\nEndpoint: {endpoint}")
                    raise Exception(f"Request failed with status {response.status}: {error_text}")
                    
                return await response.json()
        except Exception as e:
            logger.error(f"Error making CLOB API request: {str(e)}")
            raise
            
    async def fetch_current_markets(self) -> List[Dict]:
        """Fetch current and active markets using CLOB API"""
        if not self._session:
            self._session = aiohttp.ClientSession()
            
        try:
            async with self._session.get(f"{self.CLOB_API_URL}/markets") as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"CLOB API request failed: {response.status}\nResponse: {error_text}")
                    return []
                    
                markets_data = await response.json()
                active_markets = []
                
                for market in markets_data:
                    market_data = {
                        "id": market.get("marketId"),
                        "question": market.get("question"),
                        "outcomes": market.get("outcomes", []),
                        "volume": market.get("volume", "0"),
                        "prices": market.get("prices", []),
                        "created": market.get("createdAt"),
                        "lastActive": market.get("updatedAt"),
                        "active": market.get("active", False),
                        "closed": not market.get("active", False)
                    }
                    active_markets.append(market_data)
                
                return active_markets
        except Exception as e:
            logger.error(f"Error fetching current markets from CLOB API: {str(e)}")
            return []
            
    async def get_market_open_interest(self, market_id: str) -> Optional[float]:
        """Fetch open interest for a specific market using CLOB API"""
        try:
            data = await self._make_request("GET", f"markets/{market_id}/orderbook")
            if not data:
                return None
            
            # Calculate open interest from order book
            bids = data.get("bids", [])
            asks = data.get("asks", [])
            
            total_bids = sum(float(order["size"]) for order in bids)
            total_asks = sum(float(order["size"]) for order in asks)
            
            return min(total_bids, total_asks)
        except Exception as e:
            logger.error(f"Error fetching market open interest: {str(e)}")
            return None
            
    async def get_market_traders(self, market_id: str) -> List[str]:
        """Fetch unique traders for a specific market using CLOB API"""
        try:
            data = await self._make_request("GET", f"markets/{market_id}/trades")
            if not data:
                return []
            
            # Extract unique trader addresses from trades
            traders = {trade.get("trader") for trade in data if trade.get("trader")}
            return list(traders)
        except Exception as e:
            logger.error(f"Error fetching market traders: {str(e)}")
            return []
            
    async def get_historical_open_interest(self, market_id: str, start_time: int) -> List[Dict]:
        """Fetch historical open interest data for charting using CLOB API"""
        try:
            params = {"from": start_time}
            data = await self._make_request("GET", f"markets/{market_id}/trades", params=params)
            if not data:
                return []
            
            # Transform trade data into time series
            time_series = []
            for trade in data:
                time_series.append({
                    "timestamp": trade.get("timestamp"),
                    "amount": trade.get("size"),
                    "price": trade.get("price")
                })
            
            return sorted(time_series, key=lambda x: x["timestamp"])
        except Exception as e:
            logger.error(f"Error fetching historical open interest: {str(e)}")
            return []
