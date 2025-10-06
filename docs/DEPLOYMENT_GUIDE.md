# Alpha-Gen Vercel Deployment Guide

## Overview
This guide covers deploying the Alpha-Gen Debug GUI to Vercel for public access.

## Architecture
- **Frontend**: Next.js app deployed to Vercel
- **Backend**: FastAPI app deployed to Railway/Render
- **Database**: PostgreSQL (Railway) or existing SQLite
- **WebSocket**: Real-time data streaming via backend

## Prerequisites
1. Vercel account
2. Railway or Render account for backend
3. GitHub repository with the code

## Frontend Deployment (Vercel)

### 1. Environment Variables
Create these environment variables in Vercel:

```bash
NEXT_PUBLIC_WS_URL=wss://your-backend-url.railway.app/ws/market-data
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
```

### 2. Deploy to Vercel
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy from frontend directory
cd frontend
vercel

# Follow the prompts:
# - Link to existing project or create new
# - Set build command: npm run build
# - Set output directory: .next
```

### 3. Configure Custom Domain (Optional)
- Go to Vercel dashboard
- Select your project
- Go to Settings > Domains
- Add your custom domain

## Backend Deployment (Railway)

### 1. Prepare Backend
```bash
cd backend
pip install -r requirements.txt
```

### 2. Deploy to Railway
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Deploy
railway up
```

### 3. Environment Variables
Set these in Railway dashboard:
```bash
JWT_SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=postgresql://user:pass@host:port/db
```

## Backend Deployment (Render Alternative)

### 1. Create render.yaml
```yaml
services:
  - type: web
    name: alphagen-api
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: JWT_SECRET_KEY
        value: your-secret-key-change-in-production
```

### 2. Deploy to Render
- Connect GitHub repository
- Select backend directory
- Deploy

## Testing the Deployment

### 1. Test Frontend
- Visit your Vercel URL
- Check if the interface loads
- Test WebSocket connection

### 2. Test Backend
- Test API endpoints: `https://your-backend-url.railway.app/health`
- Test WebSocket: `wss://your-backend-url.railway.app/ws/market-data`

### 3. Test Integration
- Start data streaming
- Verify real-time updates
- Check chart functionality

## Security Considerations

### 1. Authentication
- Implement proper JWT secret management
- Use environment variables for secrets
- Add rate limiting

### 2. CORS
- Configure CORS properly for production
- Restrict origins to your Vercel domain

### 3. WebSocket Security
- Implement authentication for WebSocket connections
- Add connection limits
- Monitor for abuse

## Monitoring and Maintenance

### 1. Logs
- Monitor Vercel function logs
- Check backend application logs
- Set up error alerting

### 2. Performance
- Monitor WebSocket connection count
- Check API response times
- Optimize database queries

### 3. Updates
- Use GitHub Actions for CI/CD
- Test in staging environment
- Deploy during low-traffic periods

## Troubleshooting

### Common Issues

1. **WebSocket Connection Failed**
   - Check CORS configuration
   - Verify WebSocket URL
   - Check firewall settings

2. **API Authentication Errors**
   - Verify JWT secret
   - Check token expiration
   - Validate user credentials

3. **Chart Not Updating**
   - Check WebSocket connection
   - Verify data format
   - Check browser console for errors

### Debug Steps
1. Check browser developer tools
2. Monitor network requests
3. Check backend logs
4. Test API endpoints directly

## Production Checklist

- [ ] Environment variables configured
- [ ] CORS properly set up
- [ ] Authentication working
- [ ] WebSocket connections stable
- [ ] Charts updating in real-time
- [ ] Error handling implemented
- [ ] Monitoring set up
- [ ] Security measures in place
- [ ] Performance optimized
- [ ] Documentation updated

## Support

For issues or questions:
1. Check the GitHub repository
2. Review the deployment logs
3. Contact the development team
