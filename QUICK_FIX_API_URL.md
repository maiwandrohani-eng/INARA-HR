# Quick Fix: API Connection Error

## Problem
Frontend deployed to Vercel but getting: "Cannot connect to server. Please ensure the backend API is running."

## Solution

### 1. Make sure your backend is deployed
- Backend should be deployed to Railway/Render/Fly.io
- Backend URL should be accessible (e.g., `https://your-api.railway.app`)

### 2. Set NEXT_PUBLIC_API_URL in Vercel

1. Go to **Vercel Dashboard** → Your Project
2. Click **Settings** → **Environment Variables**
3. Add a new variable:
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://your-backend-url.com/api/v1`
     - Replace `your-backend-url.com` with your actual backend URL
     - Examples:
       - Railway: `https://inara-api.railway.app/api/v1`
       - Render: `https://inara-api.onrender.com/api/v1`
       - Fly.io: `https://inara-api.fly.dev/api/v1`
   - **Environment**: Select "Production" (and "Preview" if needed)
4. Click **Save**
5. **Redeploy** your frontend (Vercel should auto-redeploy, or trigger manually)

### 3. Verify Backend CORS Settings

Make sure your backend has CORS configured to allow your Vercel domain:

```bash
CORS_ORIGINS=["https://your-app.vercel.app"]
```

Or if using a custom domain:
```bash
CORS_ORIGINS=["https://your-custom-domain.com"]
```

### 4. Test

After redeploying:
1. Open your Vercel app
2. Try logging in
3. Check browser console for: `🌐 API Client initialized with baseURL: https://your-backend-url.com/api/v1`

## Common Issues

### Backend not deployed yet
- Deploy backend first to Railway/Render/Fly.io
- Wait for deployment to complete
- Get the backend URL

### Wrong URL format
- ✅ Correct: `https://api.example.com/api/v1`
- ❌ Wrong: `https://api.example.com` (missing `/api/v1`)
- ❌ Wrong: `http://api.example.com/api/v1` (should use `https`)

### Environment variable not applied
- After adding env var, you must redeploy
- Vercel usually auto-redeploys, but you can trigger manually
- Check deployment logs to verify env var is being used

## Need Help?

Check:
- Backend deployment is live and accessible
- Backend `/health` endpoint responds
- Vercel environment variable is set correctly
- CORS is configured in backend
- Browser console for detailed error messages

