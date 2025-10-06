# Role-Based Onboarding

A concise entry point for newcomers. Pair this with `README.md` and `docs/architecture.md` for deeper context.

## Quick Map

| Role | Start Here | Focus |
|------|------------|-------|
| Core Developer | Section 1 | Code structure, services, testing |
| Quant / Trader | Section 2 | Strategy logic, data tables, overrides |
| Operations / DevOps | Section 3 | Deployment, monitoring, runbooks |
| AI Assistant / Automation | Section 4 | Minimal context for prompts |

---

## 1. Core Developer Checklist

1. **Read** `README.md` (project layout) and `docs/architecture.md` (system diagram).
2. **Environment**: Python 3.11, `pip install -e .[dev]`, set `.env` (see `.env.example`).
3. **Key packages** (`src/alphagen/`):
   - `app.py`: orchestrator, wiring of services.
   - `signals.py`, `trade_generator.py`, `trade_manager.py`, `option_monitor.py`.
   - `schwab_client.py`: REST interactions; `fetch_option_quote` powers stop-loss checks.
   - `market_data/`: provider factory (Schwab polling vs Polygon stub).
4. **Important constraints**: single-position rule, 30s cooldown, minute VWAP/SMA, EST timestamps.
5. **Tests**: (pending) – preferred location `tests/`. Add integration tests with mocked Schwab endpoints.
6. **Deployment**: review `Dockerfile`, `docker-compose.yml`, `deploy/README.md`.

### Developer To-Do Template
- [ ] Update `.env` with real keys (never commit).
- [ ] Run locally via `python -m alphagen.cli run`.
- [ ] Verify SQLite schema: `sqlite3 alpha_gen.db '.tables'`.
- [ ] Add structured logging context for new modules.
- [ ] Document changes in `docs/architecture.md` and `AGENT.md` when behavior shifts.

---

## 2. Quant / Trader Checklist

1. **Strategy Summary**: see `AGENT.md` → Strategy section (VWAP vs SMA9, stop-loss/take-profit, single-position rule).
2. **Data Feeds**:
   - Equity VWAP/SMA from Schwab minute history.
   - Option quotes polled continuously for open positions.
   - Tables of interest: 1 (equity), 2 (option quotes), 7 (intents), 8 (executions).
3. **Risk Settings**: configurable via env (`RISK_*`, `FEATURE_ENABLE_CHART`).
4. **Live Monitoring**: enable `FEATURE_ENABLE_CHART=true` to see real-time VWAP/MA9 crossovers.
5. **Reporting**: `python -m alphagen.cli report --for-date YYYY-MM-DD` (or default latest day).
6. **Backtesting**: not supported—live-only system.

### Trader Workflow
- [ ] Confirm market schedule & holiday list.
- [ ] Load `.env` with desired risk multipliers / trade size.
- [ ] Run live service in tmux or container; monitor log lines tagged `signal`, `position_state`, `option_monitor`.
- [ ] Review `alpha_gen.db` daily P/L view for reconciliation.

---

## 3. Operations / DevOps Checklist

1. **Containerisation**: `Dockerfile`, `.dockerignore`, `docker-compose.yml`.
2. **Cloud Deployment**: follow `deploy/README.md` (Docker Compose on VPS or Fly.io free tier).
3. **Secrets Management**: inject via `.env` (Compose) or `fly secrets set` (Fly.io). Never bake into images.
4. **Persistence**: mount/bind `alpha_gen.db`; schedule backups to object storage.
5. **Monitoring**:
   - Logs: `structlog` JSON-style output, accessible via `docker compose logs -f` or `fly logs`.
   - Health: add optional HTTP endpoint if needed for Fly.io checks.
   - Alerting: integrate log processors (Loki/Promtail, CloudWatch, etc.).
6. **Operations Playbook**:
   - Start/stop: `docker compose start/stop` or `fly scale resume/suspend`.
   - Redeploy: `docker compose pull && up -d --force-recreate` or `fly deploy`.
   - Key rotation: update secrets and recycle container.

---

## 4. AI Assistant / Automation Context

Minimal, high-signal snippets for prompt engineering:

- **Core workflow**: normalized ticks → signal engine → trade generator → trade manager (single position) → Schwab API.
- **Key modules**: `app.py`, `option_monitor.py`, `trade_manager.py`, `signals.py`, `schwab_client.py`.
- **Critical constraints**: minute VWAP vs SMA9, 30s cooldown, stop-loss 200%, take-profit 50%, EST timestamps, single position, continuous option polling for open trades.
- **Persisted artefacts**: SQLite tables 1–8, daily P/L view; append-only to preserve audit trail.
- **Deployment**: Docker Compose / Fly.io with `.env` secrets; no Polygon streaming in production.

When asking an AI agent for changes, include:
1. Desired behavioral change (signal/strategy/storage/etc.).
2. Impacted modules from the list above.
3. Reminder of single-position/safety constraints.

Keep prompts short; link to `docs/architecture.md` when deeper context is needed.
