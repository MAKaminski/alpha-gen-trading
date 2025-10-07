# VS Code Launch Configurations

## Available Configurations (3)

### 1. Run App
**Purpose:** Launch the Debug GUI application

**How to use:**
1. Press `F5`
2. Select "Run App"
3. GUI window opens with live market data

**What it does:**
- Launches `scripts/run_app.py`
- Opens Tkinter GUI
- Streams live market data
- Shows charts and console

**Environment:**
- `ALPHAGEN_USE_MOCK_DATA=true` - Uses mock data if no OAuth token
- `PYTHONPATH` - Auto-configured

---

### 2. Run Tests
**Purpose:** Run full test suite with coverage

**How to use:**
1. Press `F5`
2. Select "Run Tests"
3. Watch tests run in terminal

**What it does:**
- Runs all 321 tests
- Generates coverage report
- Shows results in terminal

**Expected output:**
```
321 passed, 1 skipped
Coverage: 71.53%
```

---

### 3. Refresh OAuth
**Purpose:** Refresh Schwab OAuth token

**How to use:**
1. Press `F5`
2. Select "Refresh OAuth"
3. Follow OAuth flow in browser

**What it does:**
- Opens OAuth flow
- Waits for callback
- Saves token to `config/schwab_token.json`

**When to use:**
- Before first run
- When you see `InvalidTokenError`
- Token expires (every few days)

---

## Configuration Details

All configurations use:
- **Python:** From `settings.json` (`/opt/homebrew/opt/python@3.11/bin/python3.11`)
- **Working Directory:** Project root
- **Console:** Integrated Terminal
- **PYTHONPATH:** `src:.` (auto-set)

## Troubleshooting

### "Run App" or "Run Tests" won't launch
**Check:**
1. Python interpreter selected: `Cmd+Shift+P` → "Python: Select Interpreter"
2. Should show: `/opt/homebrew/opt/python@3.11/bin/python3.11`

### "Module not found" errors
**Solution:**
- PYTHONPATH is set automatically in launch configs
- No manual action needed

### Tests timeout
**Solution:**
- Normal for "Run App" (runs until closed)
- For tests, check if they're actually passing (they should complete in ~6 seconds)

## Testing the Configurations

### Test Run Tests
```bash
cd /Users/makaminski1337/Developer/alpha-gen
PYTHONPATH=src:. ALPHAGEN_USE_MOCK_DATA=true python3.11 scripts/run_tests.py
# Should complete with exit code 0
```

### Test Run App
```bash
cd /Users/makaminski1337/Developer/alpha-gen
PYTHONPATH=src:. ALPHAGEN_USE_MOCK_DATA=true python3.11 scripts/run_app.py
# Should launch GUI (Ctrl+C to exit)
```

### Test Refresh OAuth
```bash
cd /Users/makaminski1337/Developer/alpha-gen
PYTHONPATH=src:. python3.11 scripts/refresh_oauth.py
# Should open browser for OAuth flow
```

## Status

✅ All 3 configurations tested and working
✅ Simplified to essential configs only
✅ No duplicate functionality

