#!/usr/bin/env python3
"""Test the data flow from market data to chart."""

import sys
import asyncio
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from alphagen.market_data import create_market_data_provider
from alphagen.visualization.file_chart import FileChart
from alphagen.core.events import NormalizedTick, EquityTick, OptionQuote
from alphagen.core.time_utils import now_est
from datetime import datetime, timezone

async def test_data_flow():
    print("🧪 Testing data flow from market data to chart...")
    
    # Create chart
    chart = FileChart()
    chart.start()
    
    # Create market data provider
    market_data = create_market_data_provider()
    
    # Set up callbacks
    async def on_equity_tick(tick: EquityTick):
        print(f"📊 Equity tick: {tick.symbol} @ {tick.price:.2f}, VWAP: {tick.session_vwap:.2f}, MA9: {tick.ma9:.2f}")
    
    async def on_option_quote(quote: OptionQuote):
        print(f"📈 Option quote: {quote.option_symbol} @ {quote.bid:.2f}/{quote.ask:.2f}")
    
    async def on_error(exc: Exception):
        print(f"❌ Error: {exc}")
    
    from alphagen.market_data.base import StreamCallbacks
    callbacks = StreamCallbacks(
        on_equity_tick=on_equity_tick,
        on_option_quote=on_option_quote,
        on_error=on_error,
    )
    
    # Start market data
    await market_data.start(callbacks)
    print("✅ Market data started")
    
    # Wait for some data
    print("⏳ Waiting for market data...")
    await asyncio.sleep(10)
    
    # Stop everything
    await market_data.stop()
    chart.stop()
    
    print("✅ Test completed")
    print("Check if charts/ directory was created with chart files")

if __name__ == "__main__":
    asyncio.run(test_data_flow())
