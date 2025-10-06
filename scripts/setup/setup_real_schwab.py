#!/usr/bin/env python3
"""Setup real Schwab OAuth2 authentication."""

import sys
import webbrowser
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from alphagen.config import load_app_config
from schwab.auth import client_from_login_flow

def main():
    print("🔐 Setting up real Schwab OAuth2 authentication...")
    
    try:
        config = load_app_config()
        schwab_config = config.schwab
        
        print(f"API Key: {schwab_config.api_key[:10]}...")
        print(f"Account ID: {schwab_config.account_id}")
        print(f"Callback URL: {schwab_config.callback_url}")
        
        print("\n🌐 This will open your browser for Schwab authentication...")
        print("1. Login to your Schwab account")
        print("2. Authorize the application")
        print("3. You'll be redirected to a callback URL")
        print("4. The token will be automatically saved")
        
        input("\nPress Enter to continue...")
        
        # Use the interactive login flow
        client = client_from_login_flow(
            api_key=schwab_config.api_key,
            app_secret=schwab_config.api_secret,
            callback_url=schwab_config.callback_url,
            token_path=schwab_config.token_path,
            interactive=True  # This will open the browser
        )
        
        print("✅ OAuth2 authentication successful!")
        print(f"Token saved to: {schwab_config.token_path}")
        
        # Test the client
        print("\n🧪 Testing API connection...")
        accounts = client.get_account_numbers()
        print(f"Found {len(accounts)} accounts: {accounts}")
        
        # Test getting account info
        account_info = client.get_account(schwab_config.account_id)
        print(f"Account info keys: {list(account_info.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ OAuth2 setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
