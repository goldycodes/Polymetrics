import aiohttp
import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import HTTPException

# Configure logging
logger = logging.getLogger(__name__)

class ClobClient:
    """Client for interacting with Polymarket's CLOB API."""
    
    def __init__(self):
        self.base_url = "https://clob.polymarket.com"
        self._session: Optional[aiohttp.ClientSession] = None
        self._last_request_time = 0
        self._cache = {}
        self._cache_ttl = 300  # Cache TTL in seconds (5 minutes)
        self._min_request_interval = 5  # Minimum seconds between requests
        logger.debug(f"Initialized ClobClient with base URL: {self.base_url}")

    @property
    def session(self) -> aiohttp.ClientSession:
        """Get or create the client session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=30)  # 30 second timeout
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def __aenter__(self):
        """Create aiohttp session when entering context."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close aiohttp session when exiting context."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, retries: int = 3) -> Dict:
        """
        Make a request to the Polymarket API with error handling, rate limiting protection, and retries.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            params: Optional query parameters
            retries: Number of retry attempts for rate-limited requests
            
        Returns:
            Dict containing the response data
            
        Raises:
            HTTPException: If the API request fails after all retries
        """
        url = f"{self.base_url}/{endpoint}"
        headers = {
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Origin": "https://polymarket.com",
            "Referer": "https://polymarket.com/",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "Pragma": "no-cache",
            "DNT": "1",
            "Sec-Ch-Ua": "\"Not_A Brand\";v=\"8\", \"Chromium\";v=\"120\", \"Google Chrome\";v=\"120\"",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "\"macOS\""
        }
        
        for attempt in range(retries):
            try:
                # Implement rate limiting and caching with TTL
                cache_key = f"{method}:{url}:{str(params)}"
                current_time = time.time()
                
                # Check cache with TTL
                if cache_key in self._cache:
                    cache_entry = self._cache[cache_key]
                    if current_time - cache_entry['timestamp'] < self._cache_ttl:
                        logger.debug(f"Returning cached response for {cache_key}")
                        return cache_entry['data']
                    else:
                        logger.debug(f"Cache expired for {cache_key}")
                        del self._cache[cache_key]

                # Add delay between retries with increased backoff
                if attempt > 0:
                    delay = min(120, 30 * (2 ** attempt))  # Exponential backoff capped at 120s
                    logger.info(f"Retry attempt {attempt + 1}/{retries}, waiting {delay} seconds...")
                    await asyncio.sleep(delay)
                
                # Ensure minimum delay between requests
                current_time = time.time()
                time_since_last = current_time - self._last_request_time
                if time_since_last < self._min_request_interval:
                    await asyncio.sleep(self._min_request_interval - time_since_last)
                self._last_request_time = time.time()
                
                logger.debug(f"Making {method} request to {url} with params: {params}")
                async with self.session.request(method, url, params=params, headers=headers) as response:
                    response_text = await response.text()
                    logger.debug(f"Raw response text: {response_text[:1000]}...")
                    
                    if response.status == 429 or 'cloudflare' in response_text.lower():  # Rate limited or Cloudflare block
                        if attempt < retries - 1:
                            logger.warning(f"Rate limit or Cloudflare block detected (attempt {attempt + 1}/{retries})")
                            continue  # Try again with backoff
                        else:
                            logger.error("Rate limit exceeded and max retries reached")
                            raise HTTPException(
                                status_code=429,
                                detail="Rate limit exceeded or Cloudflare protection active. Please try again later."
                            )
                    
                    if response.status != 200:
                        logger.error(f"API error: {response.status} - {response_text}")
                        raise HTTPException(
                            status_code=response.status,
                            detail=f"CLOB API error: {response_text}"
                        )
                    
                    try:
                        data = await response.json()
                        logger.debug(f"Parsed JSON response: {str(data)[:1000]}...")
                        # Cache successful responses with timestamp
                        self._cache[cache_key] = {
                            'data': data,
                            'timestamp': time.time()
                        }
                        return data
                    except ValueError as e:
                        logger.error(f"Failed to parse JSON response: {str(e)}")
                        raise HTTPException(
                            status_code=500,
                            detail=f"Invalid JSON response from CLOB API: {str(e)}"
                        )
                        
            except aiohttp.ClientError as e:
                logger.error(f"Request failed: {str(e)}")
                if attempt == retries - 1:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to connect to CLOB API: {str(e)}"
                    )
                    
            return {}  # Return empty dict if all retries failed

    async def get_markets(self) -> List[Dict[str, Any]]:
        """
        Get current active markets from the CLOB API.
        Returns basic market info for MVP version.
        """
        try:
            response = await self._make_request("GET", "markets")
            markets = []
            
            if isinstance(response, dict):
                markets = response.get("markets", [])
            elif isinstance(response, list):
                markets = response
                
            logger.info(f"Found {len(markets)} markets in response")
            
            current_time = int(datetime.now().timestamp())
            transformed_markets = []
            
            for market in markets:
                if not isinstance(market, dict):
                    continue
                    
                # Basic validation
                if not market.get("condition_id") or not market.get("question"):
                    continue
                    
                # Check if market is active and not expired
                expires_at = market.get("expires_at")
                if expires_at and int(expires_at) < current_time:
                    continue
                    
                transformed_market = {
                    "id": str(market["condition_id"]),
                    "question": market["question"],
                    "volume": market.get("volume", "0"),
                    "open_interest": market.get("open_interest", "0"),
                    "trader_count": market.get("trader_count", 0)
                }
                transformed_markets.append(transformed_market)
                logger.debug(f"Added market: {transformed_market['question']}")
                
            return transformed_markets
            
        except Exception as e:
            logger.error(f"Error fetching markets: {str(e)}")
            return []

    async def get_market_history(
        self,
        market_id: str,
        resolution: str = "1D",
        days: int = 1
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
            # First try to get current market data which includes open interest
            try:
                market_data = await self._make_request("GET", f"markets/{market_id}")
                if isinstance(market_data, dict):
                    open_interest = market_data.get("open_interest")
                    if open_interest is not None:
                        return {"open_interest": open_interest}
            except Exception as e:
                logger.warning(f"Failed to get current market data, falling back to history: {e}")
            
            # Fall back to historical data if needed
            params = {
                "resolution": resolution,
                "from": int((datetime.now() - timedelta(days=days)).timestamp()),
                "to": int(datetime.now().timestamp())
            }
            
            response = await self._make_request("GET", f"markets/{market_id}/history", params)
            logger.debug(f"History response for market {market_id}: {str(response)[:1000]}...")
            
            if isinstance(response, dict):
                return {"open_interest": response.get("open_interest", 0)}
            elif isinstance(response, list) and response:
                # Get the most recent data point
                latest = response[-1]
                return {"open_interest": latest.get("open_interest", 0)}
            
            logger.warning(f"No valid history data for market {market_id}")
            return {"open_interest": 0}
            
        except Exception as e:
            logger.error(f"Error fetching market history: {str(e)}")
            return {"open_interest": 0}

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
            
            response = await self._make_request("GET", f"markets/{market_id}/trades", params)
            trades = []
            
            # Handle different response formats
            if isinstance(response, dict):
                trades = response.get("trades", [])
            elif isinstance(response, list):
                trades = response
                
            logger.debug(f"Trades response for market {market_id}: {str(trades)[:1000]}...")
            
            # Calculate unique traders and volume
            trader_addresses = set()
            total_volume = 0
            for trade in trades:
                if isinstance(trade, dict):
                    # Add trader addresses
                    if "user_wallet" in trade:
                        trader_addresses.add(trade["user_wallet"])
                    if "maker" in trade:
                        trader_addresses.add(trade["maker"])
                    # Add volume
                    if "amount" in trade:
                        try:
                            total_volume += float(trade["amount"])
                        except (ValueError, TypeError):
                            pass
                    if "taker" in trade:
                        trader_addresses.add(trade["taker"])
                        
                    # Calculate volume
                    amount = float(trade.get("amount", 0))
                    total_volume += amount
                    
            logger.info(f"Retrieved {len(trades)} trades with {len(trader_addresses)} unique traders for market {market_id}")
            return {
                "trades": trades,
                "unique_traders": len(trader_addresses),
                "volume": str(total_volume)
            }
            
        except Exception as e:
            logger.error(f"Error fetching market trades: {str(e)}")
            return {"trades": [], "unique_traders": 0, "volume": "0"}
