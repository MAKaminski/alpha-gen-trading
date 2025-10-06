# Alpha-Gen Debug Guide

This guide explains how to use the debug tools and OAuth2 setup for the Alpha-Gen trading bot.

## 🐛 Debug Commands

### Command Line Interface

```bash
# Show all available debug commands
python debug_cli.py help

# Run OAuth2 setup for Schwab API
python debug_cli.py oauth

# Start the trading bot
python debug_cli.py run

# View P&L reports
python debug_cli.py report

# Run with custom arguments
python debug_cli.py report --for-date 2024-01-15
```

### VS Code Debug Configurations

1. **Debug Alpha-Gen App** - Debug the main application
2. **Debug Alpha-Gen CLI** - Debug CLI commands
3. **Debug Alpha-Gen Report** - Debug reporting functionality
4. **Debug OAuth2 Setup** - Debug OAuth2 authentication

## 🔐 OAuth2 Setup

### Prerequisites

1. Ensure your `.env` file has valid Schwab API credentials:
   ```env
   SCHWAB_API_KEY=your_api_key
   SCHWAB_API_SECRET=your_api_secret
   SCHWAB_ACCOUNT_ID=your_account_id
   SCHWAB_CALLBACK_URL=http://localhost:8080/callback
   ```

2. Make sure your Schwab app is approved for production use.

### Running OAuth2 Setup

```bash
# Method 1: Using debug CLI
python debug_cli.py oauth

# Method 2: Direct setup
python setup_schwab_oauth.py

# Method 3: VS Code debugger
# Select "Debug OAuth2 Setup" configuration and run
```

### OAuth2 Flow

1. The setup script will open your browser
2. Login to your Schwab account
3. Authorize the application
4. The token will be automatically saved to `schwab_token.json`
5. The application will then use real Schwab API data

## 🚀 Running the Application

### Development Mode

```bash
# Start with mock data (no OAuth required)
python debug_app.py

# Start with real Schwab data (OAuth required)
python debug_cli.py run
```

### Production Mode

```bash
# Using the main CLI
python -m alphagen run
python -m alphagen report
```

## 🔧 Troubleshooting

### Common Issues

1. **Token Invalid Error**
   - Run `python debug_cli.py oauth` to get a fresh token
   - Check that your Schwab app is approved

2. **API Connection Issues**
   - Verify your API credentials in `.env`
   - Check your internet connection
   - Ensure your Schwab app has the correct permissions

3. **Debug Environment Issues**
   - Make sure you're in the virtual environment: `source .venv/bin/activate`
   - Check that all dependencies are installed: `pip install -e .`

### Logs

The application provides detailed logging:
- **INFO**: Normal operation messages
- **WARNING**: Non-critical issues (like expired tokens)
- **ERROR**: Critical issues that need attention

## 📁 File Structure

```
alpha-gen/
├── debug_app.py          # Main debug script
├── debug_cli.py          # CLI debug script with OAuth support
├── setup_schwab_oauth.py # OAuth2 setup script
├── .vscode/
│   └── launch.json       # VS Code debug configurations
└── src/alphagen/
    ├── schwab_oauth_client.py  # OAuth2 Schwab client
    └── ...               # Other application modules
```

## 🎯 Next Steps

1. **Setup OAuth2**: Run `python debug_cli.py oauth`
2. **Test Application**: Run `python debug_cli.py run`
3. **Monitor Logs**: Watch for any errors or warnings
4. **Deploy**: Follow the `deploy/README.md` for cloud deployment
