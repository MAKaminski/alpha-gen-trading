# Setting Up Real Schwab Data

## Current Issue
The application is currently using mock data instead of real Schwab market data. To get real data, we need to complete the OAuth2 authentication flow.

## Step 1: Get Real Schwab Token

### Option A: Run OAuth Setup in Terminal (Recommended)
```bash
cd /Users/makaminski1337/Developer/alpha-gen
source .venv/bin/activate
python setup_real_schwab_auto.py
```

This will:
1. Open your browser to Schwab's OAuth page
2. Let you login and authorize the application
3. Automatically save the token to `schwab_token.json`

### Option B: Manual Token Setup
If the automatic setup doesn't work, you can manually get the token:

1. Go to: https://api.schwabapi.com/v1/oauth/authorize?response_type=code&client_id=Os3C2znHkqciGVi5IMHlq7NeXqbEenDfGrnj5sijzJfRCGhU&redirect_uri=https%3A%2F%2F127.0.0.1%3A8182%2F&state=manual

2. Login to your Schwab account
3. Authorize the application
4. Copy the full callback URL from your browser
5. Use the callback URL to get the token

## Step 2: Verify Real Data

After getting the real token, run:
```bash
python debug_cli.py run
```

You should see:
- Real position data from your Schwab account
- Real market data (if available)
- No more "mock data" messages

## Step 3: Enable Chart with Real Data

The chart will now show real market data:
```bash
export FEATURE_ENABLE_CHART=true
python debug_cli.py run
```

## Troubleshooting

### If OAuth fails:
1. Check your `.env` file has correct Schwab credentials
2. Ensure your Schwab app is approved for production
3. Try running the OAuth setup in a regular terminal (not VS Code debugger)

### If no data appears:
1. Check that the token file exists and is valid
2. Verify your Schwab account has the required permissions
3. Check the logs for specific error messages

## What You'll Get

With real data, you'll see:
- **Real account positions** from your Schwab account
- **Real market quotes** for QQQ and options
- **Live VWAP/MA9 calculations** based on real market data
- **Actual trading signals** when crossovers occur
- **Real trade execution** (if you enable live trading)

## Next Steps

Once you have real data:
1. Monitor the live chart for VWAP/MA9 crossovers
2. Watch for trading signals in the logs
3. Test with paper trading first
4. Enable live trading when ready
