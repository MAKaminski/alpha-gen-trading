# Alpha-Gen Architecture

## Overview
Alpha-Gen is a real-time trading automation service that consumes live equity and option data, synchronizes Schwab position state, derives trade signals, and submits orders according to a predefined strategy. The platform is built around append-only persistence, deterministic ETL stages, and time-boxed execution within U.S. market hours for the QQQ ETF. Polygon websocket ingestion remains available but is currently disabled in favour of Schwab-driven quote polling.

```
              ┌─▶ [Table 4] Normalized Tick Store ─▶ [Table 5] Position State ─▶ [Table 6] Signals ─▶ [Table 7] Trades ─▶ Schwab Trading API
Market Data ──┤                                                           │
 (Polygon† /  └───────────────────────────────────────────────────────────┘
  Schwab)                 ▲                               │
                          │                               ▼
                 OptionMonitor (live quote polling) ──▶ Exit Rules

† Polygon streaming is currently stubbed; Schwab REST polling supplies production quotes.
```

## Key Services

- **Scheduler**: Governs market-session windows, holiday/calendar checks, and trade-cooldown enforcement so the loop sleeps outside 09:00–16:30 ET.
- **Market Data Providers**: Factory chooses between Polygon websockets (disabled) and Schwab REST polling. The active Schwab provider retrieves minute VWAP/SMA data and option quotes.
- **Option Monitor**: Polls Schwab for bid/ask/last on every open option position until exit, ensuring stop-loss / take-profit triggers remain informed.
- **Schwab Position Client**: Periodically polls account positions and balances (Table 3) to reconcile broker state with internal trade intents.
- **Normalizer ETL**: Coalesces asynchronous ticks into uniform EST-aligned slices (Table 4) and hands them to downstream stages.
- **Position Calculator**: Merges Schwab snapshots with executed trades to emit current position state (Table 5).
- **Signal Engine**: Detects VWAP/MA9 inversion, applies the 30-second cooldown, and emits structured trade signals (Table 6).
- **Trade Generator & Executor**: Transforms signals into trade intents with stop-loss / take-profit brackets, submits orders to Schwab, tracks fills, and enforces the single-position rule.
- **Storage**: SQLite + SQLModel append-only tables for each ETL output and daily P/L materialised views, all timestamps stored in `America/New_York`.
- **Visualization & Ops**: Optional matplotlib live chart, structured logging via `structlog`, Docker/Docker Compose/Fly.io artefacts for inexpensive deployment and monitoring.

## Data Tables

| Table | Description | Key Fields | Source |
|-------|-------------|------------|--------|
| Table 1 | Raw equity stream | `est_timestamp`, `price`, `session_vwap`, `ma9` | Schwab quote polling (1-min) |
| Table 2 | Raw option quotes | `est_timestamp`, `option_symbol`, `strike`, `bid`, `ask`, `last` | Option Monitor |
| Table 3 | Positions snapshot | `est_timestamp`, `symbol`, `quantity`, `avg_price` | Schwab REST |
| Table 4 | Normalized tick | `period_start`, `vwap`, `ma9`, `option_quotes[]` | ETL (Normalizer) |
| Table 5 | Position state | `est_timestamp`, `symbol`, `net_quantity`, `avg_price`, `unrealized_pnl` | ETL (Position Calculator) |
| Table 6 | Signals | `est_timestamp`, `signal_type`, `option_symbol`, `rationale`, `cooldown_until` | Signal Engine |
| Table 7 | Trade intents | `est_timestamp`, `action`, `qty`, `limit_price`, `stop_loss`, `take_profit` | Trade Generator |
| Table 8 | Executions | `est_timestamp`, `order_id`, `status`, `fill_price`, `pnl_contrib` | Schwab REST |
| Daily P/L | Aggregated P/L | `trade_date`, `realized_pnl`, `fees` | Derived from Table 8 |

## Scheduling & Constraints

- Effective trading window: 09:00–16:30 ET (09:30 open, 16:00 close, ±30 minute buffer).
- U.S. federal market holidays filtered via the `holidays` library.
- All timestamps normalized to `America/New_York`.
- Trade signal cooldown: 30 seconds between successive signals.
- Single-position rule: at most one open option position; additional signals are dropped until the position is closed.

## Strategy Implementation

1. Pull minute VWAP and SMA9 data for QQQ.
2. Detect crossover points and emit short-to-open signals on the nearest 0DTE option strike.
3. Generate trades with embedded stop-loss (200% credit) and take-profit (50% credit).
4. Poll Schwab for live bid/ask/last on the active option; close the trade on stop-loss, take-profit, reverse crossover, or market close + buffer.
5. Persist every tick, signal, intent, and execution for auditability and reporting.

## Technology Stack

- Python 3.11+
- `asyncio`, `httpx`, `websockets` (Polygon stub)
- `pydantic` / `pydantic-settings` for config
- `sqlmodel` + SQLite for storage
- `structlog` for structured logging
- `matplotlib` for live visualization
- Docker / Docker Compose / Fly.io manifests for deployment

## Open Integration Questions

- Replace Schwab REST polling with official streaming once available.
- Harden Schwab OAuth token refresh and storage (`SCHWAB_TOKEN_PATH`).
- Introduce retry/backoff and circuit breakers for Schwab endpoints.
- Support multi-position management and commission modelling.
- Expose HTTP health endpoints for managed platforms (Fly.io checks, Prometheus scraping).

## Test Coverage & Quality

### Current Test Coverage: 47% (843/1803 statements)

#### Well-Tested Components (80%+ coverage)
- **Time Utils** (100%): Market hours, holiday handling, time conversion
- **Core Events** (99%): Data models and event structures
- **Configuration** (99%): Environment and settings management
- **Storage Layer** (99%): Database persistence and models
- **Signal Engine** (87%): VWAP/MA9 crossover detection
- **Trade Manager** (87%): Order lifecycle and position tracking

#### Good Progress Components (50-80% coverage)
- **CLI Interface** (64%): Command-line interface
- **Market Data Factory** (56%): Provider selection logic
- **Schwab OAuth Client** (55%): Authentication flow
- **App Orchestrator** (53%): Main application coordination
- **Trade Generator** (53%): Signal to trade conversion

#### Remaining Gaps (<50% coverage)
- **Market Data Stream** (28%): Data ingestion and normalization
- **Option Monitor** (28%): Real-time position monitoring
- **Schwab Client** (32%): API interactions
- **Reports** (29%): P&L aggregation

#### Test Architecture
- **Unit Tests**: 10 files covering core components
- **Integration Tests**: 2 files covering component interactions
- **E2E Tests**: 1 file covering complete trading workflows

For detailed test coverage analysis, see `docs/TEST_COVERAGE_VISUALIZATION.md`.

## Next Steps

1. **Critical**: Improve tests for Market Data Stream, Option Monitor, Schwab Client, and Reports
2. Implement Schwab streaming client and reconnection logic.
3. Add integration tests using mocked Schwab/Polygon services.
4. Wire structured metrics/alerts (Prometheus, Grafana, Slack webhooks).
5. Benchmark option polling cadence vs. rate limits; tune for production latency.
6. Extend deployment automation (GitHub Actions → Fly.io / container registry).
