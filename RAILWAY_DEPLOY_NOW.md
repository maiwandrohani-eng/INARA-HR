# Railway Deployment - Pre-Deploy Checklist

## Before You Deploy - Verify These Settings

### Step 1: Check Service Configuration
In Railway → **INARA-HR** → **Settings**:

1. **Root Directory**: Should be `apps/api`
2. **Build Command**: Should auto-detect (from `railway.json`)
3. **Start Command**: Should be `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 2: Set Required Environment Variables FIRST
**IMPORTANT**: Set these BEFORE deploying, or the service will crash!

Go to Railway → **INARA-HR** → **Variables**, and add:

```bash
# Database (Supabase - REQUIRED)
DATABASE_URL=postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres?pgbouncer=true
DATABASE_ASYNC_URL=postgresql+asyncpg://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres?pgbouncer=true

# Security (REQUIRED)
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=your-generated-secret-key-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
REFRESH_TOKEN_EXPIRE_DAYS=7

# Environment (REQUIRED)
ENVIRONMENT=production
DEBUG=False
API_VERSION=v1
API_PREFIX=/api/v1

# CORS (IMPORTANT - Use your Vercel domain)
CORS_ORIGINS=["https://your-app.vercel.app"]

# Redis (Optional - can be empty if not using)
REDIS_URL=

# Cloudflare R2
R2_ENDPOINT_URL=https://f672838a09e9e6a09d08ce61b5866002.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=f2232270caa9e6bf962cc60ee8d3c5e3
R2_SECRET_ACCESS_KEY=e10c35df6da6306b5bb207161aa6b36668b20f429c9c00279d915fc7630cb8d5
R2_BUCKET_NAME=hrmis
R2_PUBLIC_URL=https://hrmis.inara.ngo
```

### Step 3: Generate SECRET_KEY (if you haven't)
Run this locally to generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
Copy the output and set it as `SECRET_KEY` in Railway Variables.

### Step 4: Get Supabase Database URLs
1. Go to Supabase Dashboard → Your Project
2. Settings → Database
3. Scroll to "Connection String"
4. Select "Connection pooling" (recommended)
5. Copy the URL and set as `DATABASE_URL`
6. Change `postgresql://` to `postgresql+asyncpg://` for `DATABASE_ASYNC_URL`

### Step 5: NOW You Can Deploy!
1. After setting all environment variables
2. Go to Railway → **INARA-HR** → **Deployments**
3. Click **Deploy** (or it may auto-deploy)
4. Wait for deployment to complete (2-5 minutes)

### Step 6: Generate Public Domain (if not done)
1. Railway → **INARA-HR** → **Settings** → **Networking**
2. Click **Generate Domain**
3. You'll get: `https://inara-hr-production.up.railway.app`

### Step 7: Test Backend
After deployment completes:
```
https://inara-hr-production.up.railway.app/health
```
Should return: `{"success":true,"status":"healthy","environment":"production"}`

### Step 8: Configure Frontend
In Vercel → Settings → Environment Variables:
```
NEXT_PUBLIC_API_URL=https://inara-hr-production.up.railway.app/api/v1
```
Then redeploy frontend.

## Quick Checklist

- [ ] Root directory set to `apps/api`
- [ ] DATABASE_URL set (from Supabase)
- [ ] DATABASE_ASYNC_URL set (postgresql+asyncpg:// version)
- [ ] SECRET_KEY generated and set
- [ ] ENVIRONMENT=production set
- [ ] DEBUG=False set
- [ ] CORS_ORIGINS includes your Vercel domain
- [ ] All other env vars set (Cloudflare R2, etc.)
- [ ] Click Deploy
- [ ] Wait for deployment
- [ ] Generate public domain
- [ ] Test /health endpoint
- [ ] Set NEXT_PUBLIC_API_URL in Vercel
- [ ] Redeploy frontend

## After Deployment

Monitor logs:
- Railway → **INARA-HR** → **Logs**
- Look for: `INFO:     Uvicorn running on http://0.0.0.0:XXXX`
- Look for: `Application startup complete`

If you see errors, check the troubleshooting guide.

