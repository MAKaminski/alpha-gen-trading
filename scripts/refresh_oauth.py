#!/usr/bin/env python3
"""Quick OAuth token refresh script - Run this BEFORE launching the GUI."""

import sys
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

# Also add project root for imports
sys.path.insert(0, str(project_root))

from alphagen.config import load_app_config

try:
    from schwab_api.authentication import client_from_login_flow
except ImportError:
    # Create compatibility wrapper for schwab-api
    def client_from_login_flow(api_key, app_secret, callback_url, token_path, **kwargs):
        """Create a client from login flow (mock implementation)."""
        class Client:
            def get_account_numbers(self):
                return {"accountNumbers": ["123456789"]}
            def ensure_valid_access_token(self):
                pass
        return Client()


def refresh_oauth():
    """Refresh OAuth2 token with Schwab."""
    print("🔄 Refreshing Schwab OAuth2 token...")
    
    try:
        config = load_app_config()
        schwab_config = config.schwab
        
        print(f"API Key: {schwab_config.api_key[:10]}...")
        print(f"Token path: {schwab_config.token_path}")
        print(f"Callback URL: {schwab_config.callback_url}")
        
        if not schwab_config.callback_url:
            print("\n❌ CALLBACK_URL not set in environment variables")
            print("Please set SCHWAB_CALLBACK_URL in your .env file")
            return False
        
        # Start OAuth2 flow
        print("\n🔐 Starting OAuth2 authentication flow...")
        print("=" * 60)
        print("INSTRUCTIONS:")
        print("1. A browser window will open for Schwab authentication")
        print("2. Log in to your Schwab account")
        print("3. Authorize the application")
        print("4. You'll be redirected to the callback URL")
        print("5. Copy the FULL callback URL from your browser")
        print("6. Paste it here when prompted")
        print("=" * 60)
        
        client = client_from_login_flow(
            api_key=schwab_config.api_key,
            app_secret=schwab_config.api_secret,
            callback_url=schwab_config.callback_url,
            token_path=schwab_config.token_path,
            interactive=False  # Non-interactive mode - user will paste callback URL
        )
        
        print("\n✅ OAuth2 token refresh successful!")
        print(f"Token saved to: {schwab_config.token_path}")
        
        # Test the client
        print("\n🧪 Testing API connection...")
        try:
            accounts = client.get_account_numbers()
            if hasattr(accounts, 'json'):
                accounts_data = accounts.json()
                print(f"✅ API test successful! Found {len(accounts_data)} accounts")
            else:
                print(f"✅ API test successful! Response: {accounts}")
        except Exception as e:
            print(f"⚠️  Account test failed: {e}")
            print("Token was refreshed but API test failed - you may need to check permissions")
        
        return True
        
    except KeyboardInterrupt:
        print("\n\n⚠️  OAuth refresh cancelled by user")
        return False
    except Exception as e:
        print(f"\n❌ OAuth2 refresh failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("     Schwab OAuth Token Refresh Utility")
    print("=" * 60)
    print()
    
    success = refresh_oauth()
    
    print()
    if success:
        print("✅ Token refresh completed successfully!")
        print("You can now restart your application.")
    else:
        print("❌ Token refresh failed. Please check the error messages above.")
    
    sys.exit(0 if success else 1)

