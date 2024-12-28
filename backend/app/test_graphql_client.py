import asyncio
import logging
from datetime import datetime, timezone
from .polymarket_graphql import PolymarketGraphQLClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import pytest

@pytest.mark.asyncio
async def test_graphql_client():
    async with PolymarketGraphQLClient() as client:
        try:
            # Test fetching current markets
            logger.info("Fetching current markets...")
            markets = await client.fetch_current_markets()
            logger.info(f"\nMarkets test:")
            logger.info(f"Found {len(markets)} markets")
            
            if markets:
                sample_market = markets[0]
                logger.info(f"Sample market data: {sample_market}")
                
                # Test fetching market details
                if 'id' in sample_market:
                    market_id = sample_market['id']
                    
                    # Get open interest
                    logger.info(f"\nFetching open interest for market {market_id}...")
                    oi = await client.get_market_open_interest(market_id)
                    logger.info(f"Open interest: {oi}")
                    
                    # Get traders
                    logger.info(f"\nFetching traders for market {market_id}...")
                    traders = await client.get_market_traders(market_id)
                    logger.info(f"Found {len(traders)} unique traders")
                    
                    # Get historical data
                    week_ago = int((datetime.now(timezone.utc).timestamp() - (7 * 24 * 60 * 60)) * 1000)
                    logger.info(f"\nFetching historical data for market {market_id}...")
                    history = await client.get_historical_open_interest(market_id, week_ago)
                    logger.info(f"Found {len(history)} historical data points")
                    
        except Exception as e:
            logger.error(f"Error during testing: {str(e)}")
            raise

if __name__ == '__main__':
    asyncio.run(test_graphql_client())
