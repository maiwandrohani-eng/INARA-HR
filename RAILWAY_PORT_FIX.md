# Railway Port Configuration Fix

## Important: Railway Port Setup

Your Railway service needs to:
1. **Generate a public domain** (click "Generate Domain" button)
2. **Use `$PORT` environment variable** (Railway provides this automatically)
3. **Configure the port correctly** in the networking settings

## Step-by-Step Fix

### Step 1: Generate Public Domain

1. In the Railway Networking page you're viewing:
2. **Clear the port field** (or leave it as default - Railway will auto-detect)
3. Click the purple **"Generate Domain"** button
4. Railway will create a domain like: `https://inara-hr-production.up.railway.app`

### Step 2: Verify Port Configuration

The FastAPI backend is already configured to use `$PORT`:
- Check: `railway.json` has `--port $PORT` in start command ✅
- Railway automatically provides `$PORT` environment variable ✅

**Important**: 
- Don't hardcode port `8080` or `8000`
- Railway assigns a dynamic port via `$PORT`
- The port field in UI is for **custom configuration** - you can usually leave it default

### Step 3: Test After Domain Generation

Once domain is generated:
```
https://your-generated-domain.up.railway.app/health
```

Should return: `{"status":"healthy"}`

## If Service Still Not Working

Check these in Railway → INARA-HR → Variables:

### Required Environment Variables:
```bash
DATABASE_URL=postgresql://... (from Supabase)
DATABASE_ASYNC_URL=postgresql+asyncpg://... (from Supabase)  
SECRET_KEY=generate-your-own-secret-key
REDIS_URL= (can be empty if not using Redis)
ENVIRONMENT=production
DEBUG=False
CORS_ORIGINS=["https://your-vercel-app.vercel.app"]
```

### Quick Test:
1. Generate domain first
2. Wait 1-2 minutes for service to start
3. Test: `https://your-domain.up.railway.app/health`
4. If it works, copy the domain for Vercel `NEXT_PUBLIC_API_URL`

