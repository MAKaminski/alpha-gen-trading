#!/usr/bin/env python3
"""Debug script for Alpha-Gen application."""

import asyncio
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from alphagen.app import main

if __name__ == "__main__":
    print("Starting Alpha-Gen in debug mode...")
    print(f"Python path: {sys.path[0]}")
    print(f"Working directory: {Path.cwd()}")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDebug session interrupted by user")
    except Exception as e:
        print(f"Debug session failed: {e}")
        import traceback
        traceback.print_exc()
