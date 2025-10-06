import asyncio
import json
from datetime import datetime
from typing import Callable, Optional
import sys
import os

# Add the parent directory to the path to import alphagen modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

class SchwabWebSocketService:
    """WebSocket service for Schwab market data streaming."""
    
    def __init__(self, broadcast_callback: Callable[[str], None]):
        self.broadcast_callback = broadcast_callback
        self.is_running = False
        self.task: Optional[asyncio.Task] = None
        
    async def start(self):
        """Start the market data streaming service."""
        if self.is_running:
            return
            
        self.is_running = True
        self.task = asyncio.create_task(self._stream_data())
        print("Schwab WebSocket service started")
        
    async def stop(self):
        """Stop the market data streaming service."""
        self.is_running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        print("Schwab WebSocket service stopped")
        
    async def _stream_data(self):
        """Main data streaming loop."""
        while self.is_running:
            try:
                # Simulate market data
                await self._simulate_market_data()
                await asyncio.sleep(1)  # Update every second
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in market data streaming: {e}")
                await asyncio.sleep(5)  # Wait before retrying
                
    async def _simulate_market_data(self):
        """Simulate market data for testing."""
        import random
        
        # Simulate QQQ price movement
        base_price = 400.0
        price_change = random.uniform(-2.0, 2.0)
        current_price = base_price + price_change
        
        # Create mock equity tick
        equity_tick = {
            "type": "equity_tick",
            "data": {
                "symbol": "QQQ",
                "price": round(current_price, 2),
                "timestamp": datetime.now().isoformat(),
                "volume": random.randint(1000, 10000)
            }
        }
        
        # Create mock normalized tick for chart
        normalized_tick = {
            "type": "normalized_tick",
            "data": {
                "timestamp": datetime.now().isoformat(),
                "equity": {
                    "session_vwap": round(current_price + random.uniform(-1, 1), 2),
                    "ma9": round(current_price + random.uniform(-0.5, 0.5), 2)
                }
            }
        }
        
        # Create mock log message
        log_message = {
            "type": "log",
            "data": {
                "level": "info",
                "message": f"Equity: QQQ = ${current_price:.2f}"
            }
        }
        
        # Broadcast all messages
        await self.broadcast_callback(json.dumps(equity_tick))
        await self.broadcast_callback(json.dumps(normalized_tick))
        await self.broadcast_callback(json.dumps(log_message))
