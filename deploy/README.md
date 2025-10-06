# Deployment Guide

This document walks through running Alpha-Gen on inexpensive cloud infrastructure so the bot can stay online, be monitored, and restarted quickly when needed.

## 1. Container Image

The repository includes a production-ready `Dockerfile`. Build it locally (or in CI) to produce a reusable image:

```bash
docker build -t alpha-gen:latest .
```

Copy your `.env` (or a sanitized version) to the target host; the container loads configuration from the environment.

## 2. Docker Compose (single VM)

For a low-cost $5–$7/month VPS (e.g. DigitalOcean droplet, Hetzner CX11, Lightsail micro), install Docker and Docker Compose v2, then launch the service with the bundled compose file:

```bash
scp -r . user@host:/opt/alpha-gen
ssh user@host
cd /opt/alpha-gen
cp .env.example .env  # edit with real API keys
sudo docker compose up -d
```

- **Monitoring:** `sudo docker compose logs -f` streams live logs. Use `--tail` to limit history.
- **Stop/start:** `sudo docker compose stop` pauses the bot; `sudo docker compose start` resumes. `sudo docker compose down` removes the container but preserves `alpha_gen.db` because it is bind-mounted.
- **Health checks:** add services like Prometheus node_exporter or use the provider's VM metrics dashboard.

## 3. Fly.io (free tier container platform)

Fly.io offers a free micro VM with 3 shared CPU cores and 256 MB RAM—enough for Alpha-Gen’s workload.

1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Authenticate: `fly auth login`
3. In the repo, run `fly launch --no-deploy --copy-config` and answer:
   - Choose a unique app name (e.g. `alpha-gen-bot`).
   - Select a region close to the U.S. east coast for best market latency.
   - Decline database creation.
4. Edit the generated `fly.toml`:
   ```toml
   [build]
     dockerfile = "Dockerfile"

   [processes]
     app = "python -m alphagen.cli run"

   [env]
     PYTHONUNBUFFERED = "1"

   [services]
     [[services.http_checks]]
       interval = "60s"
       timeout  = "10s"
       grace_period = "30s"
       method = "get"
       path   = "/health"
       protocol = "http"
       port = 8080
   ```
   (The app does not expose HTTP yet; omit the health check or add a lightweight FastAPI endpoint if desired.)
5. Push secrets:
   ```bash
   fly secrets set $(grep -v '^#' .env | xargs)
   ```
6. Deploy: `fly deploy`
7. Monitor logs: `fly logs`
8. Pause/resume: `fly scale suspend` and `fly scale resume`

## 4. GitHub Actions (optional)

To automate deployments, create `.github/workflows/deploy.yml` that builds the Docker image and runs `fly deploy`. Store the Fly API token as `FLY_API_TOKEN` secret.

## 5. Observability & Alerting

- Enable Fly.io’s “Metrics” tab or install a lightweight agent (Grafana Cloud Agent, Vector) in the container to ship logs/metrics to a hosted Grafana stack.
- For Compose deployments, add a service like [Promtail](https://grafana.com/docs/loki/latest/clients/promtail/) or connect Docker logging to AWS CloudWatch / GCP Logging.
- Consider integrating Slack or PagerDuty by piping structured logs from `structlog` into webhook handlers.

## 6. Operations Checklist

- **Rolling restart:** `docker compose restart` or `fly deploy --strategy rolling`.
- **Environment changes:** rotate API keys by updating `.env` (Compose) or running `fly secrets set ...` (Fly).
- **Backups:** the SQLite file lives at `/app/alpha_gen.db`. Bind-mount or schedule periodic `sqlite3 .backup` copies to object storage.

With this setup you can run the bot continuously on a minimal VM or free-tier container, observe runtime logs, and stop/start the process quickly if an error occurs.
