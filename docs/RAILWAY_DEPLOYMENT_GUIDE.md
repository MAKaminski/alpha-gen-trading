# Railway Deployment Guide for Alpha-Gen Backend

## Overview

This guide covers deploying the Alpha-Gen Python backend to Railway, which will serve as your compute platform alongside Vercel for the frontend.

## Architecture

- **Frontend**: Vercel (Next.js/React)
- **Backend**: Railway (Python/FastAPI)
- **Database**: SQLite (existing) or Railway PostgreSQL
- **WebSocket**: Railway handles real-time connections

## Prerequisites

1. Railway account (free tier available)
2. GitHub repository connected
3. Schwab API credentials
4. Domain name (optional)

## Step 1: Railway Setup

### 1.1 Create Railway Project

1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your `alpha-gen` repository

### 1.2 Configure Environment Variables

In Railway dashboard, go to your project → Variables tab and add:

```bash
# Schwab API (required)
SCHWAB_CLIENT_ID=your_schwab_client_id
SCHWAB_CLIENT_SECRET=your_schwab_client_secret
SCHWAB_REDIRECT_URI=https://your-app.railway.app/auth/callback

# JWT Configuration
JWT_SECRET_KEY=your_secure_jwt_secret_key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=sqlite:///./alpha_gen.db

# CORS
FRONTEND_URL=https://alpha-gen.vercel.app

# Logging
LOG_LEVEL=INFO
```

### 1.3 Configure Build Settings

Railway will automatically detect the `railway.json` configuration:

- **Builder**: Dockerfile
- **Dockerfile Path**: `deploy/Dockerfile`
- **Start Command**: `python railway_start.py`
- **Health Check**: `/health`

## Step 2: Database Configuration

### Option A: SQLite (Current)
- Uses existing SQLite database
- Data persists in Railway's file system
- Good for development and small-scale production

### Option B: PostgreSQL (Recommended for Production)
1. In Railway dashboard, click "New" → "Database" → "PostgreSQL"
2. Copy the connection string
3. Update `DATABASE_URL` environment variable
4. Update your backend to use PostgreSQL

## Step 3: Domain Configuration

### 3.1 Railway Domain
Railway provides a free domain: `your-app.railway.app`

### 3.2 Custom Domain (Optional)
1. In Railway dashboard → Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed
4. Update Vercel environment variables

## Step 4: Update Vercel Configuration

Update your `vercel.json` with the actual Railway URL:

```json
{
  "env": {
    "NEXT_PUBLIC_WS_URL": "wss://your-app.railway.app/ws/market-data",
    "NEXT_PUBLIC_API_URL": "https://your-app.railway.app"
  }
}
```

## Step 5: Deployment Process

### 5.1 Automatic Deployment
Railway automatically deploys when you push to your main branch.

### 5.2 Manual Deployment
1. Push changes to GitHub
2. Railway detects changes
3. Builds Docker image
4. Deploys to Railway infrastructure

### 5.3 Health Checks
Railway monitors your app at `/health` endpoint:
- Returns 200 OK when healthy
- Automatically restarts on failure

## Step 6: Monitoring and Logs

### 6.1 View Logs
- Railway dashboard → Deployments → View logs
- Real-time log streaming
- Error tracking and debugging

### 6.2 Metrics
- CPU usage
- Memory consumption
- Request count
- Response times

## Step 7: Production Considerations

### 7.1 Security
- Use strong JWT secrets
- Enable HTTPS (automatic on Railway)
- Configure CORS properly
- Rate limiting (implement in FastAPI)

### 7.2 Performance
- Railway auto-scales based on traffic
- WebSocket connections are handled efficiently
- Database connection pooling

### 7.3 Backup
- Regular database backups
- Environment variable backup
- Code repository backup

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check Dockerfile syntax
   - Verify Python dependencies
   - Check build logs

2. **WebSocket Issues**
   - Verify CORS configuration
   - Check Railway domain settings
   - Test WebSocket connection

3. **Database Issues**
   - Verify DATABASE_URL format
   - Check database permissions
   - Test database connection

4. **Environment Variables**
   - Verify all required variables are set
   - Check variable names and values
   - Restart deployment after changes

### Debug Commands

```bash
# Check Railway CLI
railway --version

# Login to Railway
railway login

# Connect to project
railway link

# View logs
railway logs

# Deploy manually
railway up
```

## Cost Considerations

### Railway Free Tier
- $5 credit monthly
- 500 hours of usage
- 1GB RAM, 1 vCPU
- Perfect for development and small production

### Railway Pro Tier
- $20/month per service
- Unlimited usage
- More resources
- Better support

## Next Steps

1. Deploy to Railway
2. Test WebSocket connections
3. Configure monitoring
4. Set up custom domain
5. Implement production security measures

## Support

- Railway Documentation: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- GitHub Issues: Your repository issues
