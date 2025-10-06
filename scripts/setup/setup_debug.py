#!/usr/bin/env python3
"""Setup script for debugging Alpha-Gen."""

import os
import sys
from pathlib import Path

def setup_debug_environment():
    """Set up environment variables for debugging."""
    
    # Set default environment variables for debugging
    debug_env = {
        "MARKET_DATA_SOURCE": "schwab",
        "SCHWAB_PAPER": "true",
        "DATABASE_URL": "sqlite+aiosqlite:///./alpha_gen_debug.db",
        "RISK_STOP_LOSS_MULTIPLE": "2.0",
        "RISK_TAKE_PROFIT_MULTIPLE": "0.5",
        "RISK_MAX_POSITION_SIZE": "25",
        "RISK_TRADING_CAPITAL": "5000000.0",
    }
    
    print("Setting up debug environment...")
    for key, value in debug_env.items():
        os.environ[key] = value
        print(f"  {key}={value}")
    
    print("\nDebug environment ready!")
    print("Note: You'll need to set SCHWAB_API_KEY, SCHWAB_API_SECRET, and SCHWAB_ACCOUNT_ID")
    print("for the application to work with real data.")

if __name__ == "__main__":
    setup_debug_environment()
