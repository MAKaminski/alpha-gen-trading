# Google OAuth Setup Guide

This guide explains how to set up Google OAuth authentication for the Alpha-Gen trading platform.

## Prerequisites

1. A Google Cloud Platform account
2. Access to the Google Cloud Console

## Step 1: Create Google OAuth Credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google+ API" and enable it
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Web application"
   - Add authorized redirect URIs:
     - `http://localhost:3000/api/auth/callback/google` (for development)
     - `https://your-domain.com/api/auth/callback/google` (for production)

## Step 2: Environment Variables

Create a `.env.local` file in the frontend directory with the following variables:

```env
# NextAuth.js Configuration
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key-here

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id-here
GOOGLE_CLIENT_SECRET=your-google-client-secret-here
```

### Getting the Values

- **GOOGLE_CLIENT_ID**: Found in the Google Cloud Console credentials page
- **GOOGLE_CLIENT_SECRET**: Found in the Google Cloud Console credentials page
- **NEXTAUTH_SECRET**: Generate a random secret key (you can use `openssl rand -base64 32`)

## Step 3: Update Vercel Environment Variables

For production deployment on Vercel:

1. Go to your Vercel project dashboard
2. Navigate to Settings > Environment Variables
3. Add the following variables:
   - `NEXTAUTH_URL`: Your production domain
   - `NEXTAUTH_SECRET`: Same secret as development
   - `GOOGLE_CLIENT_ID`: Your Google OAuth client ID
   - `GOOGLE_CLIENT_SECRET`: Your Google OAuth client secret

## Step 4: Test the Integration

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Navigate to `http://localhost:3000`
4. Click "Sign in with Google"
5. Complete the OAuth flow

## Security Considerations

- Keep your OAuth credentials secure
- Use HTTPS in production
- Regularly rotate your NEXTAUTH_SECRET
- Monitor OAuth usage in Google Cloud Console
- Implement rate limiting for authentication endpoints

## Troubleshooting

### Common Issues

1. **"Invalid redirect URI"**: Ensure the redirect URI in Google Cloud Console matches exactly
2. **"Client ID not found"**: Verify the GOOGLE_CLIENT_ID is correct
3. **"Invalid client secret"**: Verify the GOOGLE_CLIENT_SECRET is correct
4. **CORS errors**: Ensure NEXTAUTH_URL is set correctly

### Debug Mode

Enable NextAuth debug mode by adding to your `.env.local`:
```env
NEXTAUTH_DEBUG=true
```

This will provide detailed logs for troubleshooting authentication issues.

## Next Steps

After successful setup:

1. Customize the sign-in/sign-up pages in `src/app/auth/`
2. Implement user profile management
3. Add role-based access control
4. Set up user preferences and settings
5. Integrate with your backend user management system
