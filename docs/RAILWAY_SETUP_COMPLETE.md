# Railway Setup Complete Guide

## Your Railway Token
**Token**: `0df7a770-ebe5-4edc-98ac-1e9d2086ef90`

⚠️ **SECURITY WARNING**: This token is now stored in this file for reference. After setup, consider regenerating it in Railway dashboard for security.

## Step 1: Complete Railway Login

Since Railway CLI requires interactive authentication, you need to complete the login manually:

```bash
# Run this command in your terminal
railway login
```

This will open a browser window where you can:
1. Sign in to your Railway account
2. Authorize the CLI
3. Return to terminal

## Step 2: Verify Authentication

```bash
# Check if you're logged in
railway whoami

# List your projects
railway projects
```

## Step 3: Connect Your Project

```bash
# Navigate to your project directory
cd /Users/makaminski1337/Developer/alpha-gen

# Link this project to Railway
railway link

# Or create a new project
railway new
```

## Step 4: Set Environment Variables

In Railway dashboard or via CLI:

```bash
# Set Schwab API credentials
railway variables set SCHWAB_CLIENT_ID=your_schwab_client_id
railway variables set SCHWAB_CLIENT_SECRET=your_schwab_client_secret
railway variables set SCHWAB_REDIRECT_URI=https://your-app.railway.app/auth/callback

# Set JWT configuration
railway variables set JWT_SECRET_KEY=your_secure_jwt_secret_key
railway variables set JWT_ALGORITHM=HS256
railway variables set JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# Set database
railway variables set DATABASE_URL=sqlite:///./alpha_gen.db

# Set CORS
railway variables set FRONTEND_URL=https://alpha-gen.vercel.app

# Set logging
railway variables set LOG_LEVEL=INFO
```

## Step 5: Deploy

```bash
# Deploy your application
railway up

# Or use the deployment script
python scripts/deploy_railway.py
```

## Step 6: Get Your Railway URL

After deployment, Railway will provide you with a URL like:
- `https://alpha-gen-production.railway.app`

Update your `vercel.json` with the actual URL:

```json
{
  "env": {
    "NEXT_PUBLIC_WS_URL": "wss://your-actual-railway-url.railway.app/ws/market-data",
    "NEXT_PUBLIC_API_URL": "https://your-actual-railway-url.railway.app"
  }
}
```

## Step 7: Test Deployment

```bash
# Check deployment status
railway status

# View logs
railway logs

# Test health endpoint
curl https://your-railway-url.railway.app/health
```

## Security Best Practices

1. **Regenerate Token**: After setup, go to Railway dashboard → Settings → Tokens and regenerate your token
2. **Environment Variables**: Never commit sensitive variables to git
3. **CORS**: Update CORS settings in production
4. **HTTPS**: Railway provides HTTPS automatically

## Troubleshooting

### Common Issues

1. **Login Issues**: Make sure you're using the correct Railway account
2. **Deployment Fails**: Check logs with `railway logs`
3. **Environment Variables**: Verify all required variables are set
4. **CORS Issues**: Check that your Vercel URL is in the allowed origins

### Useful Commands

```bash
# View all variables
railway variables

# Update a variable
railway variables set KEY=value

# Delete a variable
railway variables delete KEY

# View deployment logs
railway logs --follow

# Check project status
railway status

# Open Railway dashboard
railway open
```

## Next Steps

1. Complete the interactive login
2. Deploy your application
3. Update Vercel with the Railway URL
4. Test the full stack integration
5. Set up monitoring and alerts

Your Railway configuration is ready - just complete the interactive login step!

