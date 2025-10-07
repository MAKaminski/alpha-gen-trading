# Setup Guide

## Quick Setup (5 minutes)

### 1. Install Dependencies
```bash
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..
```

### 2. Configure Schwab API
Create `config/schwab_token.json` by running:
```bash
python3.11 scripts/refresh_oauth.py
```

Follow the OAuth flow in your browser.

### 3. Run the Application
```bash
python3.11 scripts/run_app.py
```

Or use VS Code: Press `F5` → Select "Run App"

## Detailed Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- Schwab Developer Account

### 1. Schwab API Setup

#### Get API Credentials
1. Go to [Schwab Developer Portal](https://developer.schwab.com)
2. Create an app
3. Note your:
   - API Key (Client ID)
   - API Secret (Client Secret)
   - Account ID

#### Configure OAuth
```bash
# Run OAuth refresh script
python3.11 scripts/refresh_oauth.py
```

This creates `config/schwab_token.json`.

### 2. Google OAuth Setup (Frontend Only)

For frontend authentication:

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create OAuth 2.0 credentials
3. Add to `frontend/.env.local`:
   ```env
   GOOGLE_CLIENT_ID=your-client-id
   GOOGLE_CLIENT_SECRET=your-client-secret
   NEXTAUTH_URL=http://localhost:3000
   NEXTAUTH_SECRET=generate-random-secret
   ```

### 3. GitHub Setup (Optional)

For version control and CI/CD:

1. **Initialize repository:**
   ```bash
   git init
   git remote add origin your-repo-url
   ```

2. **GitHub Actions** automatically run tests on push

See [GIT_WORKFLOW.md](GIT_WORKFLOW.md) for best practices.

## Configuration Files

| File | Purpose |
|------|---------|
| `config/schwab_token.json` | OAuth token (auto-generated) |
| `backend/requirements.txt` | Python dependencies |
| `frontend/package.json` | Node dependencies |
| `pyproject.toml` | Python project config |
| `pytest.ini` | Test configuration |

## VS Code Setup

The project is pre-configured with:
- ✅ Launch configurations (`.vscode/launch.json`)
- ✅ Python settings (`.vscode/settings.json`)
- ✅ Environment variables

Just open the project and press `F5`!

## Troubleshooting

### "No module named 'alphagen'"
Ensure PYTHONPATH is set:
```bash
export PYTHONPATH=src:.
```

Or use the provided scripts which handle this automatically.

### "InvalidTokenError"
Refresh OAuth token:
```bash
python3.11 scripts/refresh_oauth.py
```

Or use VS Code: Press `F5` → "Refresh OAuth"

### Tests failing
Ensure mock data mode is enabled:
```bash
export ALPHAGEN_USE_MOCK_DATA=true
```

Or use:
```bash
python3.11 scripts/run_tests.py
```

## Next Steps

- **Run tests:** `python3.11 scripts/run_tests.py`
- **Start development:** See [DEVELOPMENT.md](DEVELOPMENT.md)
- **Deploy:** See [DEPLOYMENT.md](DEPLOYMENT.md)

