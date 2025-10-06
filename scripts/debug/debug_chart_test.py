#!/usr/bin/env python3
"""DEPRECATED: Debug test specifically for VS Code debugger.

This script is deprecated. Use the unified debug GUI instead:
    python -m alphagen debug
"""

import sys
from pathlib import Path

if __name__ == "__main__":
    print("⚠️  DEPRECATED: This debug script is no longer supported.")
    print("")
    print("🚀 Please use the unified debug GUI instead:")
    print("   python -m alphagen debug")
    print("")
    print("The new debug GUI provides:")
    print("  • Live data streaming controls")
    print("  • Real-time charting with VWAP vs MA9")
    print("  • OAuth setup integration")
    print("  • Console logging and export")
    print("  • All debugging features in one interface")
    print("")
    print("For VS Code debugging, use:")
    print("  '🐛 Debug Alpha-Gen (Unified GUI)' configuration")
    print("")
    print("Redirecting to unified debug GUI...")
    
    # Add src to Python path
    src_path = Path(__file__).parent.parent / "src"
    sys.path.insert(0, str(src_path))
    
    try:
        from alphagen.gui.debug_app import main as run_debug_gui
        run_debug_gui()
    except Exception as e:
        print(f"Failed to start debug GUI: {e}")
        print("Please run: python -m alphagen debug")
