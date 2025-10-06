#!/usr/bin/env python3
"""Test the simple chart directly."""

import sys
import time
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from alphagen.visualization.simple_chart import SimpleChart
from alphagen.core.events import NormalizedTick, EquityTick, OptionQuote
from alphagen.core.time_utils import now_est
from datetime import datetime, timezone

def test_simple_chart():
    print("🧪 Testing simple chart...")
    
    # Create chart instance
    chart = SimpleChart()
    
    # Start the chart
    chart.start()
    print("✅ Chart started - look for the matplotlib window!")
    
    # Generate some test data
    for i in range(20):
        current_time = now_est()
        base_price = 400.0 + i * 0.5  # Varying price
        
        # Create mock equity tick
        equity_tick = EquityTick(
            symbol="QQQ",
            price=base_price,
            session_vwap=base_price * 0.99,  # VWAP slightly below price
            ma9=base_price * 1.01,  # MA9 slightly above price
            as_of=current_time,
        )
        
        # Create mock option quote
        option_quote = OptionQuote(
            option_symbol="QQQ241220C00400000",
            strike=400.0,
            bid=5.50 + i * 0.1,
            ask=5.75 + i * 0.1,
            expiry=datetime.now(timezone.utc).replace(hour=16, minute=0, second=0, microsecond=0),
            as_of=current_time,
        )
        
        # Create normalized tick
        normalized_tick = NormalizedTick(
            as_of=current_time,
            equity=equity_tick,
            option=option_quote,
        )
        
        # Send to chart
        chart.handle_tick(normalized_tick)
        print(f"📊 Sent tick {i+1}: Price={base_price:.2f}, VWAP={equity_tick.session_vwap:.2f}, MA9={equity_tick.ma9:.2f}")
        
        # Wait a bit between ticks
        time.sleep(0.5)
    
    print("✅ Test data sent to chart")
    print("📈 Chart should be visible now!")
    print("The window should show:")
    print("  - Green line (VWAP)")
    print("  - Blue line (MA9)")
    print("  - Real-time updates")
    print("\nPress Enter to close the chart...")
    input()
    
    # Stop the chart
    chart.stop()
    print("✅ Chart stopped")

if __name__ == "__main__":
    test_simple_chart()
