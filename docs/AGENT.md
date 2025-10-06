# High Level Requirements

1) [TABLE 1, API 1] Polygon stream real-time Equity Data - Session VWAP, MA9, timestamp
2) [TABLE 2, API 2] Polygon stream real-time Nearest Expiry 0DTE Options Data, Strike, Bid, Ask, timestamp
3) [TABLE 3, API 3] Schwab retrieve Current Position
4) [TABLE 4, ETL 1] Normalize to a single period/tick, Append Only
5) [TABLE 5, ETL 2] Calculcate Current Position
6) [TABLE 6, ETL 3] Calculcate Signal Generation
7) [TABLE 7, ETL 4] Generate Trade
8) [TABLE 8, API 4] Submit Trade

# Constraints

1. [CONSTANT 1] EST Market Hours
2. [CONSTANT 2] 30 Min Buffer on Front and Back
3. [INDEX 1] Adjust for Holidays
4. [CONFIG 1] All timestamps should be saved in EST NOT UTC
5. [CONFIG 2] Equity & Option Chain data should be for ticker QQQ
6. [CONSTANT 3] Trade Signal Generator Cooldown - 30 Seconds
7. [CONSTANT 4] TRADING_CAPITAL = 5,000,000
8. [CONSTANT 5] CONTRACTS_PER_TRADE = 25
9. [CONFIG 3] Secrets must reside in `.env` (see `.env.example`). Do not place keys in docs/repo.
   - `SCHWAB_API_KEY`
   - `SCHWAB_API_SECRET`
   - `POLYGON_API_KEY`
10. [CONSTANT 6] The time period for the MA9 should be 9 Mins

# Strategy

1. Detect VWAP / MA9 inversion (minute VWAP vs SMA9) on QQQ. Example crossover:
   - VWAP moves 409 → 410 while MA9 moves 410 → 409.
2. Short the nearest 0DTE option strike around the crossover (default: strike 410 in example).
3. Exit logic (any condition):
   1. Market close + 30 minute buffer.
   2. Stop-loss at 200% of entry credit.
   3. Take-profit at 50% of entry credit.
   4. VWAP crosses MA9 in the reverse direction.
4. Maintain live bid/ask/last streaming for every open short option until the trade is closed; these quotes drive the stop-loss / take-profit checks.
5. Enforce a single-position rule (one open option position at a time) to keep capital concentrated and simplify monitoring.
6. Store QQQ equity VWAP/MA9 data and option quotes in append-only tables for traceability.

# Outputs

1. View of Daily P/L, which aggregates Trade Execution

# Limitations

1. No Backtesting - only Real-Time
2. To Start we will be using a back-testing account on Schwab so we CAN execute the trades and see the daily P/L
