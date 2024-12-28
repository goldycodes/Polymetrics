import aiohttp
import asyncio
import json
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CLOB_BASE_URL = "https://clob.polymarket.com"

async def test_clob_endpoints():
    async with aiohttp.ClientSession() as session:
        try:
            # 1. Get current and live markets
            logger.info("\n=== Testing Current Markets Endpoint ===")
            async with session.get(
                f"{CLOB_BASE_URL}/markets",
                params={
                    "page": 1,
                    "limit": 10,
                    "status": "active"
                },
                headers={
                    "Accept": "application/json"
                }
            ) as response:
                if response.status == 200:
                    raw_text = await response.text()
                    logger.info(f"Raw response: {raw_text[:1000]}...")  # First 1000 chars for debugging
                    
                    try:
                        data = json.loads(raw_text)
                        logger.info("Successfully parsed JSON response")
                        
                        markets = data.get("data", [])
                        if markets:
                            logger.info(f"Found {len(markets)} markets")
                            
                            for market in markets:
                                try:
                                    logger.info("\n=== Market Details ===")
                                    logger.info(f"Question: {market.get('question', 'N/A')}")
                                    logger.info(f"Status: active={market.get('active', 'N/A')}, closed={market.get('closed', 'N/A')}")
                                    logger.info(f"Market ID: {market.get('condition_id', 'N/A')}")
                                    logger.info(f"Description: {market.get('description', 'N/A')}")
                                    logger.info(f"End Date: {market.get('end_date_iso', 'N/A')}")
                                    logger.info(f"Game Start Time: {market.get('game_start_time', 'N/A')}")
                                    
                                    # Get market ID for further queries
                                    market_id = market.get('condition_id')
                                    if not market_id:
                                        logger.error("No market ID found, skipping additional queries")
                                        continue
                                        
                                    # Try to get market history
                                    logger.info("\n=== Testing Market History ===")
                                    history_params = {
                                        "resolution": "1D",  # 1 day resolution
                                        "from": int((datetime.now() - timedelta(days=7)).timestamp()),
                                        "to": int(datetime.now().timestamp())
                                    }
                                    
                                    async with session.get(
                                        f"{CLOB_BASE_URL}/history/{market_id}",
                                        params=history_params,
                                        headers={"Accept": "application/json"}
                                    ) as hist_response:
                                        hist_text = await hist_response.text()
                                        logger.info(f"History Response ({hist_response.status}): {hist_text[:500]}...")
                                        
                                    # Try to get recent trades
                                    logger.info("\n=== Testing Recent Trades ===")
                                    async with session.get(
                                        f"{CLOB_BASE_URL}/trades/{market_id}",
                                        params={"limit": 100},
                                        headers={"Accept": "application/json"}
                                    ) as trades_response:
                                        trades_text = await trades_response.text()
                                        logger.info(f"Trades Response ({trades_response.status}): {trades_text[:500]}...")
                                        
                                except Exception as e:
                                    logger.error(f"Error processing market: {str(e)}")
                                    continue
                        else:
                            logger.error("No markets found in response")
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse JSON response: {str(e)}")
                    except Exception as e:
                        logger.error(f"Unexpected error processing response: {str(e)}")
                        # Try to get market history
                        logger.info("\n=== Testing Market History ===")
                        history_params = {
                            "resolution": "1D",  # 1 day resolution
                            "from": int((datetime.now() - timedelta(days=7)).timestamp()),
                            "to": int(datetime.now().timestamp())
                        }
                        
                        async with session.get(
                            f"{CLOB_BASE_URL}/history/{market_id}",
                            params=history_params,
                            headers={"Accept": "application/json"}
                        ) as hist_response:
                            if hist_response.status == 200:
                                hist_data = await hist_response.json()
                                logger.info(f"Historical data available: {bool(hist_data)}")
                                logger.info(f"History data: {json.dumps(hist_data, indent=2)}")
                            else:
                                logger.error(f"Error fetching history: {hist_response.status}")
                        
                        # Try to get recent trades
                        logger.info("\n=== Testing Recent Trades ===")
                        async with session.get(
                            f"{CLOB_BASE_URL}/trades/{market_id}",
                            params={"limit": 100},
                            headers={"Accept": "application/json"}
                        ) as trades_response:
                            if trades_response.status == 200:
                                trades_data = await trades_response.json()
                                logger.info(f"Trades data available: {bool(trades_data)}")
                                if trades_data:
                                    # Try to calculate unique traders
                                    trader_addresses = set()
                                    for trade in trades_data:
                                        if "maker" in trade:
                                            trader_addresses.add(trade["maker"])
                                        if "taker" in trade:
                                            trader_addresses.add(trade["taker"])
                                    logger.info(f"Unique traders found: {len(trader_addresses)}")
                            else:
                                logger.error(f"Error fetching trades: {trades_response.status}")
                else:
                    logger.error(f"Error: {response.status} - {await response.text()}")
                    
        except Exception as e:
            logger.error(f"Error accessing CLOB API: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_clob_endpoints())
