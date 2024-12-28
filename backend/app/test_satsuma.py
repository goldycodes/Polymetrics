import aiohttp
import asyncio
import json
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SATSUMA_URL = "https://subgraph.satsuma-prod.com/f5c1a7dd3ab7/polymarket/matic-markets/api"

async def test_graphql_endpoint():
    # Query for current and live markets with volume, open interest, and traders
    query = """
    query {
      fixedProductMarketMakers(
        where: {
          active: true
        },
        orderBy: creationTimestamp,
        orderDirection: desc,
        first: 10
      ) {
        id
        creationTimestamp
        lastActiveDay
        collateralVolume
        scaledCollateralVolume
        outcomeTokenPrices
        tradesQuantity
        conditions {
          id
          question
        }
        liquidityParameter
        outcomeTokenAmounts
      }
    }
    """
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                SATSUMA_URL,
                json={"query": query},
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Origin": "https://polymarket.com"
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info("GraphQL Response:")
                    logger.info(json.dumps(data, indent=2))
                    
                    if "data" in data and "fixedProductMarketMakers" in data["data"]:
                        markets = data["data"]["fixedProductMarketMakers"]
                        logger.info(f"\nFound {len(markets)} active markets")
                        
                        for market in markets:
                            logger.info(f"\nMarket: {market['conditions'][0]['question']}")
                            logger.info(f"Volume: {market['collateralVolume']}")
                            logger.info(f"Trades Count: {market['tradesQuantity']}")
                            
                            # Calculate open interest from outcome token amounts
                            token_amounts = [float(amount) for amount in market['outcomeTokenAmounts']]
                            open_interest = min(token_amounts) if token_amounts else 0
                            logger.info(f"Open Interest: {open_interest}")
                            
                            # Show current prices
                            prices = market['outcomeTokenPrices']
                            logger.info(f"Current Prices: {prices}")
                    else:
                        logger.error("No market data in response")
                else:
                    logger.error(f"Error: {response.status} - {await response.text()}")
                    
                # Test historical data query
                historical_query = """
                query {
                  fixedProductMarketMakerDayData(
                    first: 7,
                    orderBy: date,
                    orderDirection: desc
                  ) {
                    date
                    volume
                    outcomeTokenPrices
                    outcomeTokenAmounts
                  }
                }
                """
                
                async with session.post(
                    SATSUMA_URL,
                    json={"query": historical_query},
                    headers={
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                        "Origin": "https://polymarket.com"
                    }
                ) as hist_response:
                    if hist_response.status == 200:
                        hist_data = await hist_response.json()
                        logger.info("\n=== Historical Data ===")
                        logger.info(json.dumps(hist_data, indent=2))
                    else:
                        logger.error(f"Error fetching historical data: {response.status} - {await response.text()}")
                    
        except Exception as e:
            logger.error(f"Error querying GraphQL endpoint: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_graphql_endpoint())
