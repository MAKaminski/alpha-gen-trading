# Deployment Guide

## Overview

Alpha-Gen can be deployed to **Railway** (backend) and **Vercel** (frontend).

## Quick Deploy

### Backend → Railway
```bash
python3.11 scripts/deploy_railway.py
```

### Frontend → Vercel
```bash
cd frontend
vercel deploy --prod
```

## Railway Backend Deployment

### Prerequisites
- Railway account
- Railway CLI: `npm install -g @railway/cli`

### Setup
1. **Login to Railway**
   ```bash
   railway login
   ```

2. **Link project**
   ```bash
   railway link
   ```

3. **Set environment variables**
   ```bash
   railway variables set SCHWAB_API_KEY="your-api-key"
   railway variables set SCHWAB_API_SECRET="your-secret"
   railway variables set SCHWAB_ACCOUNT_ID="your-account-id"
   ```

4. **Deploy**
   ```bash
   python3.11 scripts/deploy_railway.py
   ```

### Configuration Files
- `deploy/Dockerfile` - Container configuration
- `deploy/railway.json` - Railway configuration
- `deploy/Procfile` - Process definitions
- `deploy/railway_start.py` - Startup script

## Vercel Frontend Deployment

### Prerequisites
- Vercel account
- Vercel CLI: `npm install -g vercel`

### Setup
1. **Login to Vercel**
   ```bash
   vercel login
   ```

2. **Deploy**
   ```bash
   cd frontend
   vercel deploy --prod
   ```

3. **Set environment variables** (in Vercel dashboard)
   ```
   NEXT_PUBLIC_API_URL=https://your-railway-app.railway.app
   NEXT_PUBLIC_WS_URL=wss://your-railway-app.railway.app/ws/market-data
   NEXTAUTH_URL=https://your-vercel-app.vercel.app
   NEXTAUTH_SECRET=<generate-random-secret>
   GOOGLE_CLIENT_ID=<your-google-client-id>
   GOOGLE_CLIENT_SECRET=<your-google-client-secret>
   ```

### Configuration
- `deploy/vercel.json` - Vercel configuration
- `frontend/package.json` - Dependencies

## Environment Variables

### Backend (Railway)
```env
SCHWAB_API_KEY=your-api-key
SCHWAB_API_SECRET=your-secret
SCHWAB_ACCOUNT_ID=your-account-id
```

### Frontend (Vercel)
```env
NEXT_PUBLIC_API_URL=backend-url
NEXT_PUBLIC_WS_URL=backend-ws-url
NEXTAUTH_URL=frontend-url
NEXTAUTH_SECRET=random-secret
GOOGLE_CLIENT_ID=google-client-id
GOOGLE_CLIENT_SECRET=google-client-secret
```

## Monitoring

Check deployment status:
```bash
python3.11 scripts/dashboard_status.py
```

## Troubleshooting

### Railway Issues
- **Check logs:** `railway logs`
- **Check service:** `railway status`
- **Redeploy:** `railway up`

### Vercel Issues
- **Check logs:** Vercel dashboard
- **Check build:** `vercel logs`
- **Redeploy:** `vercel deploy --prod --force`

## Architecture

```
Client (Browser)
    ↓
Vercel (Next.js Frontend)
    ↓
Railway (FastAPI Backend)
    ↓
Schwab API
```

For detailed architecture, see [architecture.md](architecture.md).

