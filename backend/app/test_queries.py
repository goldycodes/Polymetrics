import asyncio
import time
import logging
from app.polymarket_client import PolymarketClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_queries():
    client = PolymarketClient()
    
    # Test fetching current markets
    logger.info('Fetching current markets...')
    markets = await client.get_markets()
    logger.info(f'Found {len(markets)} markets')
    
    if markets:
        market = markets[0]
        market_id = market['id']
        logger.info(f'\nTesting market {market_id}:')
        
        # Test market orders to get historical data
        orders = await client.get_market_orders(market_id)
        logger.info(f'Market Orders: {len(orders.get("data", []))}')
        
        # Print detailed market info
        logger.info('\nMarket Details:')
        logger.info(f'Question: {market["question"]}')
        logger.info(f'Volume: {market["volume"]}')
        logger.info(f'Open Interest: {market["open_interest"]}')
        logger.info(f'Trader Count: {market["trader_count"]}')
        logger.info(f'End Date: {market["end_date"]}')
        logger.info('\nOutcomes:')
        for outcome in market["outcomes"]:
            logger.info(f'- {outcome["outcome"]}: {outcome["price"]}')

if __name__ == '__main__':
    asyncio.run(test_queries())
