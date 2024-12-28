import asyncio
import logging
from app.polymarket_client import PolymarketClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enable debug logging for the API client
logging.getLogger('app.polymarket_client').setLevel(logging.DEBUG)

async def test_client():
    async with PolymarketClient() as client:
        try:
            # Test fetching markets
            logger.info("Fetching markets...")
            markets = await client.get_markets()
            logger.info(f"\nMarkets test:")
            logger.info(f"Found {len(markets)} markets")
            if markets:
                logger.info(f"Sample market data: {markets[0]}")
            
            # Test fetching market details
            if markets and isinstance(markets[0], dict) and 'marketId' in markets[0]:
                market_id = markets[0]['marketId']
                logger.info(f"\nMarket details test for {market_id}:")
                market_info = await client.get_market_info(market_id)
                logger.info(f"Market info: {market_info}")
                
        except Exception as e:
            logger.error(f"Error during testing: {str(e)}")
            raise

if __name__ == '__main__':
    asyncio.run(test_client())
