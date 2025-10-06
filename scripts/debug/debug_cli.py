#!/usr/bin/env python3
"""Debug script for Alpha-Gen CLI."""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from alphagen.cli import cli

def run_oauth_setup():
    """Run OAuth2 setup for Schwab API."""
    print("🔐 Starting Schwab OAuth2 Setup...")
    try:
        import subprocess
        result = subprocess.run([
            sys.executable, "setup_schwab_oauth.py"
        ], capture_output=False, text=True)
        
        if result.returncode == 0:
            print("✅ OAuth2 setup completed successfully!")
        else:
            print(f"❌ OAuth2 setup failed with return code: {result.returncode}")
            
    except Exception as e:
        print(f"❌ OAuth2 setup failed: {e}")

def show_help():
    """Show available debug commands."""
    print("🐛 Alpha-Gen Debug Commands:")
    print()
    print("Available commands:")
    print("  python debug_cli.py              - Run the main application")
    print("  python debug_cli.py oauth        - Run OAuth2 setup for Schwab API")
    print("  python debug_cli.py run          - Start the real-time service")
    print("  python debug_cli.py report       - Display daily P/L summary")
    print("  python debug_cli.py help         - Show this help message")
    print()
    print("VS Code Debug Configurations:")
    print("  - Debug Alpha-Gen App           - Debug main application")
    print("  - Debug Alpha-Gen CLI           - Debug CLI commands")
    print("  - Debug Alpha-Gen Report        - Debug reporting")
    print("  - Debug OAuth2 Setup            - Debug OAuth2 authentication")
    print()
    print("Examples:")
    print("  python debug_cli.py oauth        # Setup Schwab OAuth2")
    print("  python debug_cli.py run          # Start trading bot")
    print("  python debug_cli.py report       # View P&L report")

if __name__ == "__main__":
    print("Starting Alpha-Gen CLI in debug mode...")
    print(f"Python path: {sys.path[0]}")
    print(f"Working directory: {Path.cwd()}")
    
    # Check for special debug commands
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "oauth":
            run_oauth_setup()
        elif command == "help":
            show_help()
        else:
            # Pass through to CLI
            args = sys.argv[1:]
            try:
                cli(args)
            except Exception as e:
                print(f"CLI debug session failed: {e}")
                import traceback
                traceback.print_exc()
    else:
        # Default: run the main application
        try:
            cli(["run"])
        except Exception as e:
            print(f"CLI debug session failed: {e}")
            import traceback
            traceback.print_exc()
