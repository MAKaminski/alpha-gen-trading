# Alpha-Gen

Alpha-Gen is a real-time trading automation service that consumes live equity and option data from Polygon, synchronizes Schwab positions, and orchestrates a VWAP/MA9 crossover strategy to short 0DTE QQQ options. The system persists each ETL stage as append-only tables and produces a daily P/L view for executed trades.

## Features

- Polygon websocket ingestion for QQQ session VWAP/MA9 and nearest-expiry option quotes (Tables 1 & 2).
- Schwab REST polling for account positions (Table 3).
- Normalization ETL aligning ticks into unified EST-timestamped slices (Table 4).
- Position calculator, signal engine, trade generator, and trade executor stages (Tables 5–8).
- Append-only SQLite persistence and daily P/L reporting.
- CLI for running the service and querying realized P/L.

## Project Layout

```
src/alphagen/
  app.py              # Orchestrator wiring all services
  cli.py              # Command-line entrypoints
  config.py           # Environment-driven configuration and constants
  core/               # Shared domain models & time utilities
  etl/                # Normalization and position stages
  polygon_stream.py   # Polygon websocket clients
  schwab_client.py    # Schwab REST wrapper (paper/live)
  signals.py          # VWAP/MA9 strategy logic
  trade_generator.py  # Converts signals into trade intents
  trade_manager.py    # Order lifecycle & exit triggers
  storage.py          # SQLModel tables & persistence helpers
  reports.py          # Daily P/L aggregation
```

Additional background and data flow diagrams are documented in `docs/architecture.md`.

## Directory Structure

This project follows a strict directory structure for maintainability and clarity:

```
alpha-gen/
├── src/                    # Source code
├── tests/                  # Test suite (unit, integration, e2e)
├── scripts/                # Executable scripts
│   ├── setup/             # Setup and configuration scripts
│   ├── debug/             # Debug and development scripts
│   └── testing/           # Test execution scripts
├── config/                 # Configuration files and tokens
├── docs/                   # Documentation
│   ├── setup/             # Setup guides
│   └── architecture/      # Technical documentation
├── deploy/                 # Deployment files (Docker, etc.)
├── data/                   # Runtime data files
└── charts/                 # Generated chart images
```

See [DIRECTORY_STRUCTURE.md](DIRECTORY_STRUCTURE.md) for detailed structure constraints and organization rules.

### New to the Project?

- **Overview & architecture**: `docs/architecture.md`
- **Role-based onboarding**: `docs/role_guide.md` (developers, traders, ops, AI assistants)
- **Strategy & constraints**: `AGENT.md`

## Requirements

- Python 3.11+
- Polygon.io API key with real-time equities and options entitlement.
- Schwab API credentials for the back-testing (paper) account.

Install dependencies via pip:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

Copy the example environment file to define your local secrets and overrides:

```bash
cp .env.example .env
```

Edit `.env` with your actual Polygon and Schwab credentials (keep it out of source control; `.env` is gitignored).

## Configuration

All configuration is supplied through environment variables (defaults in parentheses). Values in `.env` are loaded automatically when exporting via your shell or a process manager:

| Setting | Variable | Notes |
|---------|----------|-------|
| Polygon API Key | `POLYGON_API_KEY` | Required for stream authentication |
| Equity ticker | `POLYGON_EQUITY_TICKER` (`QQQ`) | Underlying symbol |
| Options underlying | `POLYGON_OPTIONS_UNDERLYING` (`QQQ`) | OCC root |
| Stocks websocket URL | `POLYGON_STOCK_WS_URL` | Override if using mock |
| Options websocket URL | `POLYGON_OPTIONS_WS_URL` | Override if using mock (unused until Polygon re-enabled) |
| Polygon S3 Access Key | `POLYGON_S3_ACCESS_KEY` | Used for Polygon flat-file downloads |
| Polygon S3 Secret Key | `POLYGON_S3_SECRET_KEY` | Used for Polygon flat-file downloads |
| Polygon S3 Endpoint | `POLYGON_S3_ENDPOINT` (`https://files.polygon.io`) | Override for alternate storage |
| Schwab API Key | `SCHWAB_API_KEY` | OAuth bearer/token |
| Schwab API Secret | `SCHWAB_API_SECRET` | For refreshing tokens |
| Schwab Account ID | `SCHWAB_ACCOUNT_ID` | Paper account number |
| Schwab Base URL | `SCHWAB_BASE_URL` (`https://api.schwab.com`) | Sandbox vs live |
| Schwab Paper Flag | `SCHWAB_PAPER` (`true`) | Toggle live trading |
| Schwab Callback URL | `SCHWAB_CALLBACK_URL` | OAuth redirect target |
| Schwab Token Store | `SCHWAB_TOKEN_PATH` (`./schwab_token.json`) | Persist refreshed tokens |
| Database URL | `DATABASE_URL` (`sqlite+aiosqlite:///./alpha_gen.db`) | Append-only store |
| Risk Stop-Loss Multiple | `RISK_STOP_LOSS_MULTIPLE` (`2.0`) | Multiplier for stop price |
| Risk Take-Profit Multiple | `RISK_TAKE_PROFIT_MULTIPLE` (`0.5`) | Multiplier for take-profit |
| Risk Max Position Size | `RISK_MAX_POSITION_SIZE` (`25`) | Contracts per trade |
| Risk Trading Capital | `RISK_TRADING_CAPITAL` (`5000000`) | Capital guard for risk mgmt |
| Live Chart Toggle | `FEATURE_ENABLE_CHART` (`false`) | Enable matplotlib VWAP/MA9 chart |

The strategy constants are defined in `alphagen/config.py`:

- Market hours: 09:30–16:00 ET with ±30 minute buffer.
- All timestamps normalized to `America/New_York`.
- Trade cooldown: 30 seconds.
- Option contract multiplier: 100.
- Risk rules: stop-loss at 200% of entry credit, take-profit at 50%, default size 25 contracts (override via `RISK_MAX_POSITION_SIZE`).

## Usage

### Run the live service

```bash
export POLYGON_API_KEY=...
export SCHWAB_API_KEY=...
export SCHWAB_API_SECRET=...
export SCHWAB_ACCOUNT_ID=...

python -m alphagen.cli run
```

The service will:

- Connect to the Schwab market data stream (option quotes are polled for open positions until exit).
- Poll Schwab for position snapshots every 15 seconds.
- Persist each ETL output incrementally in SQLite (`alpha_gen.db`).
- Generate and execute trades when VWAP crosses MA9, subject to cooldown and exit rules.

### Inspect Daily P/L

```bash
python -m alphagen.cli report
python -m alphagen.cli report --for-date 2024-02-12
```

## Development Notes

- Persistence uses SQLModel + SQLite (async). Tables are append-only by design.
- Live chart uses matplotlib; requires an environment with a GUI/display backend.
- The orchestrator wires streaming callbacks through ETL stages without blocking the event loop.
- Trade exits are enforced on stop-loss/take-profit thresholds, market close buffer, and rollover when strategy reverses direction.
- All timestamps are stored in EST; conversion helpers live in `core/time_utils.py`.
- For integration testing, consider standing up mock Polygon/Schwab servers and overriding the websocket/REST URLs via environment variables.

## Next Steps

- Implement real authentication flows (token refresh) for Schwab APIs.
- Harden websocket reconnection and backpressure handling.
- Add integration/contract tests with mocked market data streams.
- Extend monitoring (metrics, alerting) and graceful shutdown on partial failures.
- Implement Schwab real-time market data streaming support.

## Deployment

See `deploy/README.md` for container-based deployment (Docker Compose or Fly.io). The included `Dockerfile` runs `python -m alphagen.cli run`, so you can build and run the service on a cloud VM and control it with standard container tooling.
