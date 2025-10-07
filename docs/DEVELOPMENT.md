# Development Guide

## Quick Start

### Run Application
```bash
python3.11 scripts/run_app.py
```
Or: Press `F5` → "Run App"

### Run Tests
```bash
python3.11 scripts/run_tests.py
```
Or: Press `F5` → "Run Tests"

### Debug Tests
1. Open test file (e.g., `tests/unit/test_signals.py`)
2. Press `F5` → "Debug Current Test File"

## VS Code Debug Configurations

| Configuration | Use When |
|--------------|----------|
| **Run App** | Launch GUI application |
| **Run Tests** | Run full test suite with coverage |
| **Debug Current Test File** | Debug the open test file |
| **Debug Single Test** | Debug specific test (highlight name first) |
| **Refresh OAuth** | OAuth token expired |

## Testing

### Run All Tests
```bash
python3.11 scripts/run_tests.py
```

### Run Specific Tests
```bash
python3.11 scripts/run_tests_simple.py tests/unit/test_signals.py
```

### Test Organization
```
tests/
├── unit/           # Fast, isolated component tests
├── integration/    # Component interaction tests
├── e2e/           # End-to-end workflow tests
└── fixtures/      # Shared test data
```

### Current Status
- ✅ 321 tests passing
- ✅ 71.53% coverage (target: 30%)

## Git Workflow

### Daily Development
```bash
git checkout -b feature/your-feature
# Make changes
git add .
git commit -m "feat: your feature"
git push origin feature/your-feature
```

### Before Committing
1. Run tests: `python3.11 scripts/run_tests.py`
2. Check coverage is > 30%
3. Format code (auto-formats on save in VS Code)

See [GIT_WORKFLOW.md](GIT_WORKFLOW.md) for details.

## Project Structure

```
alpha-gen/
├── src/alphagen/          # Main application code
│   ├── app.py             # Main application
│   ├── gui/               # Debug GUI
│   ├── market_data/       # Market data streams
│   ├── core/              # Core events & utilities
│   ├── signals.py         # Signal generation
│   ├── trade_generator.py # Trade intent creation
│   └── trade_manager.py   # Position management
├── tests/                 # All tests
├── scripts/               # Utility scripts
├── frontend/              # Next.js frontend
├── backend/               # FastAPI backend
└── docs/                  # Documentation
```

## Key Components

### Signal Engine
Generates trading signals based on VWAP/MA crossovers.
- Source: `src/alphagen/signals.py`
- Tests: `tests/unit/test_signals*.py`

### Trade Generator
Converts signals to trade intents with risk parameters.
- Source: `src/alphagen/trade_generator.py`
- Tests: `tests/unit/test_trade_generator*.py`

### Trade Manager
Manages positions and exit conditions.
- Source: `src/alphagen/trade_manager.py`
- Tests: `tests/unit/test_trade_manager*.py`

### Debug GUI
Tkinter-based GUI for development and monitoring.
- Source: `src/alphagen/gui/debug_app.py`
- Launch: `python3.11 scripts/run_app.py`

## Code Conventions

- **Naming:** snake_case for methods/functions
- **Models:** Use Pydantic, not dataclasses
- **Logging:** Use structlog, minimal verbosity
- **Timestamps:** 12-hour AM/PM format
- **Time precision:** Truncate to seconds

## Common Tasks

### Add New Feature
1. Create feature branch
2. Write tests first (TDD)
3. Implement feature
4. Ensure coverage > 30%
5. Create PR

### Debug Issues
1. Add breakpoints in VS Code
2. Press `F5` → Select appropriate config
3. Step through code with debugger

### Update Dependencies
```bash
pip install new-package
pip freeze > backend/requirements.txt
```

## Performance

- **Log files:** Max 100KB
- **Test coverage:** Min 30%
- **API calls:** Use mock data in tests

## References

- [SETUP.md](SETUP.md) - Initial setup
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deploy to production
- [architecture.md](architecture.md) - System architecture
- [AGENT.md](AGENT.md) - AI agent documentation

