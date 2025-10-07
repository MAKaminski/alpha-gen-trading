import asyncio
import json
import threading
import time
from datetime import datetime
from typing import Callable, Optional
import sys
import os
from queue import Queue, Empty

# Add the parent directory to the path to import alphagen modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

class DataBridge:
    """Bridge between AlphaGen app and FastAPI WebSocket service."""

    def __init__(self):
        self.data_queue = Queue()
        self.alphagen_process = None
        self.alphagen_thread = None

    def start_alphagen_app(self):
        """Start the AlphaGen app in a separate thread."""
        if self.alphagen_thread and self.alphagen_thread.is_alive():
            return

        def run_alphagen():
            try:
                # Import and run the AlphaGen app
                from alphagen.app import AlphaGenApp
                import asyncio

                async def run_app():
                    app = AlphaGenApp()
                    await app.run()

                # Run the async app in a new event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(run_app())

            except Exception as e:
                print(f"Error running AlphaGen app: {e}")

        self.alphagen_thread = threading.Thread(target=run_alphagen, daemon=True)
        self.alphagen_thread.start()
        print("AlphaGen app started in background thread")

    def send_data_to_websocket(self, data):
        """Send data to WebSocket clients."""
        print(f"📨 DataBridge: Sending data to WebSocket: {data[:100]}...")
        self.data_queue.put(data)

    def get_data_for_websocket(self, timeout=1.0):
        """Get data from the bridge for WebSocket broadcasting."""
        try:
            return self.data_queue.get(timeout=timeout)
        except Empty:
            return None

# Global data bridge instance
data_bridge = DataBridge()

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

        # Start the AlphaGen app if not already running
        data_bridge.start_alphagen_app()

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
                # Get data from the AlphaGen app via the bridge
                data = data_bridge.get_data_for_websocket(timeout=1.0)
                if data:
                    print(f"📡 WebSocket service received data: {data[:100]}...")
                    await self.broadcast_callback(data)

                # Also simulate some market data if no real data is coming
                if not data:
                    await self._simulate_market_data()
                    await asyncio.sleep(1)

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

        # Broadcast the message
        await self.broadcast_callback(json.dumps(normalized_tick))
