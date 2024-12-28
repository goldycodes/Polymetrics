import asyncio
import websockets
import json
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def connect_websocket():
    uri = "wss://ws-subscriptions-clob.polymarket.com/ws"
    market_id = "0x5Ce0c9cd0f79b711Bdaa8287B0e8540C02D824c5"  # Biden nomination market
    
    async with websockets.connect(uri) as websocket:
        # Subscribe to market updates
        subscribe_msg = {
            "type": "subscribe",
            "channel": "markets",
            "market": market_id
        }
        
        logger.info("Subscribing to market updates...")
        await websocket.send(json.dumps(subscribe_msg))
        
        # Subscribe to trades
        trades_msg = {
            "type": "subscribe",
            "channel": "trades",
            "market": market_id
        }
        
        logger.info("Subscribing to trades...")
        await websocket.send(json.dumps(trades_msg))
        
        try:
            # Listen for messages for 30 seconds
            start_time = datetime.now()
            while (datetime.now() - start_time) < timedelta(seconds=30):
                response = await websocket.recv()
                logger.info(f"Received: {response}")
                
                try:
                    data = json.loads(response)
                    if "type" in data:
                        if data["type"] == "trade":
                            logger.info("Trade data received!")
                            logger.info(f"Trade details: {json.dumps(data, indent=2)}")
                        elif data["type"] == "market":
                            logger.info("Market update received!")
                            logger.info(f"Market details: {json.dumps(data, indent=2)}")
                except json.JSONDecodeError:
                    logger.error("Failed to parse response as JSON")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.error("WebSocket connection closed")

if __name__ == "__main__":
    asyncio.run(connect_websocket())
