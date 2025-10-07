# Deployment Status & Guide

## Current Deployment Configuration

### Frontend (Vercel)
- **Platform**: Vercel
- **Framework**: Next.js 14
- **Configuration**: `vercel.json`
- **Build**: Automatic from `frontend/` directory
- **Environment Variables**:
  - `NEXT_PUBLIC_API_URL`: Backend API endpoint
  - `NEXT_PUBLIC_WS_URL`: WebSocket endpoint

### Backend (Railway)
- **Platform**: Railway
- **Runtime**: Python 3.11
- **Configuration**: `deploy/railway.json`
- **Dockerfile**: `deploy/Dockerfile`
- **Start Script**: `deploy/railway_start.py`
- **Health Check**: `/health` endpoint
- **Port**: Dynamic (from `PORT` env variable)

## Deployment Steps

### 1. Frontend Deployment (Vercel)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy from project root
cd /path/to/alpha-gen
vercel --prod

# Or connect your GitHub repo to Vercel for automatic deployments
```

**Environment Variables to Set in Vercel**:
- `NEXT_PUBLIC_API_URL=https://your-railway-app.railway.app`
- `NEXT_PUBLIC_WS_URL=wss://your-railway-app.railway.app/ws/market-data`

### 2. Backend Deployment (Railway)

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Deploy
railway up

# Set environment variables
railway variables set SCHWAB_APP_KEY=your_key
railway variables set SCHWAB_APP_SECRET=your_secret
railway variables set POLYGON_API_KEY=your_key
```

**Environment Variables Needed**:
- `PORT` (auto-set by Railway)
- `RAILWAY_ENVIRONMENT` (auto-set by Railway)
- `SCHWAB_APP_KEY` (your Schwab API key)
- `SCHWAB_APP_SECRET` (your Schwab API secret)
- `POLYGON_API_KEY` (your Polygon API key)

## Verification Steps

### Frontend Health Check
1. Visit `https://your-app.vercel.app`
2. Check browser console for API connection errors
3. Verify WebSocket connection in Network tab

### Backend Health Check
1. Visit `https://your-app.railway.app/health`
2. Should return:
   ```json
   {
     "status": "healthy",
     "timestamp": "2025-10-07T...",
     "active_connections": 0
   }
   ```

### WebSocket Testing
```bash
# Using wscat
npm install -g wscat
wscat -c wss://your-app.railway.app/ws/market-data

# Send test message
{"type": "start_stream"}
```

## Current Status

### ✅ Completed
- Docker configuration for Railway
- FastAPI backend with health checks
- CORS configuration for Vercel frontend
- WebSocket endpoint for real-time data
- Next.js frontend build configuration
- Environment variable setup

### 🔄 In Progress
- Schwab API authentication flow
- Polygon data streaming integration
- OAuth token management

### ❌ Pending
- Production environment variable configuration
- Domain configuration (if custom domain needed)
- SSL certificate verification
- Load testing
- Monitoring setup

## Troubleshooting

### Common Issues

#### 1. CORS Errors
- Verify your frontend URL is in `backend/main.py` allowed_origins
- Check Railway environment variables are set
- Ensure Vercel env vars point to correct Railway URL

#### 2. WebSocket Connection Fails
- Verify Railway app is running (`railway logs`)
- Check WebSocket URL uses `wss://` protocol
- Ensure firewall/network allows WebSocket connections

#### 3. API 404 Errors
- Verify Railway deployment was successful
- Check API endpoints in `backend/main.py`
- Review Railway logs for errors

#### 4. Build Failures
- Check `deploy/Dockerfile` has all required dependencies
- Verify `pyproject.toml` is complete
- Review Railway build logs

## Monitoring

### Railway Metrics
- View at: `https://railway.app/project/YOUR_PROJECT_ID`
- Monitor: CPU, Memory, Network
- Check logs in real-time

### Vercel Analytics
- View at: `https://vercel.com/YOUR_TEAM/YOUR_PROJECT`
- Monitor: Page views, Response times, Errors
- Check deployment logs

## Rollback Procedure

### Frontend (Vercel)
```bash
# List deployments
vercel ls

# Rollback to specific deployment
vercel rollback DEPLOYMENT_URL
```

### Backend (Railway)
```bash
# List deployments
railway status

# Rollback via Railway dashboard
# Go to Deployments tab and click "Redeploy" on previous version
```

## Cost Estimates

### Vercel (Frontend)
- **Free Tier**: Up to 100GB bandwidth, unlimited deployments
- **Pro**: $20/month for team features
- **Expected**: Free tier sufficient for development

### Railway (Backend)
- **Free Tier**: $5 credit/month
- **Estimated Usage**: ~$5-10/month for hobby project
- **Production**: $10-20/month with monitoring

## Security Checklist

- [ ] Environment variables not committed to git
- [ ] `.env` files in `.gitignore`
- [ ] API keys rotated regularly
- [ ] HTTPS enabled on all endpoints
- [ ] CORS properly configured
- [ ] Rate limiting enabled (production)
- [ ] Authentication required for sensitive endpoints
- [ ] Logging enabled for security events

## Next Steps

1. Set up production environment variables
2. Configure custom domain (optional)
3. Enable monitoring and alerting
4. Set up backup/disaster recovery
5. Document runbook for common operations
6. Create deployment automation
7. Set up staging environment

