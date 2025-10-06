#!/usr/bin/env python3
"""Setup script for Schwab OAuth2 authentication."""

import asyncio
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from alphagen.config import load_app_config
from schwab.auth import client_from_login_flow


async def setup_oauth():
    """Set up OAuth2 authentication with Schwab."""
    print("Setting up Schwab OAuth2 authentication...")
    
    try:
        config = load_app_config()
        schwab_config = config.schwab
        
        print(f"API Key: {schwab_config.api_key[:10]}...")
        print(f"Account ID: {schwab_config.account_id}")
        print(f"Callback URL: {schwab_config.callback_url}")
        
        if not schwab_config.callback_url:
            print("❌ CALLBACK_URL not set in environment variables")
            print("Please set SCHWAB_CALLBACK_URL in your .env file")
            return False
            
        # Start OAuth2 flow
        print("\n🔐 Starting OAuth2 authentication flow...")
        print("This will open a browser window for authentication.")
        print("After authentication, you'll be redirected to the callback URL.")
        print("Copy the full callback URL and paste it here when prompted.")
        
        client = client_from_login_flow(
            api_key=schwab_config.api_key,
            app_secret=schwab_config.api_secret,
            callback_url=schwab_config.callback_url,
            token_path=schwab_config.token_path,
            interactive=False
        )
        
        print("✅ OAuth2 authentication successful!")
        print(f"Token saved to: {schwab_config.token_path}")
        
        # Test the client
        print("\n🧪 Testing API connection...")
        try:
            accounts = client.get_account_numbers()
            if hasattr(accounts, 'json'):
                accounts_data = accounts.json()
                print(f"Found {len(accounts_data)} accounts: {accounts_data}")
            else:
                print(f"Account response: {accounts}")
        except Exception as e:
            print(f"Account test failed: {e}")
            print("OAuth2 setup completed successfully despite account test failure")
        
        return True
        
    except Exception as e:
        print(f"❌ OAuth2 setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(setup_oauth())
    sys.exit(0 if success else 1)
