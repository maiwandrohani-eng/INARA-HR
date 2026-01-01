# Railway Backend Deployment - Quick Reference

## Your Railway Project Details
- **Project Name**: brave-warmth
- **Service Name**: INARA-HR
- **Project ID**: 93a43ea8-e0a6-4af1-ae0a-d8c26e816940
- **Environment**: production

## Step 1: Find Your Railway Backend URL

1. Go to Railway Dashboard: https://railway.app/dashboard
2. Click on your project: **brave-warmth**
3. Click on service: **INARA-HR**
4. Go to **Settings** → **Networking**
5. You'll see a **Public Domain** like:
   - `https://inara-hr-production.up.railway.app`
   - Or `https://[random-name].up.railway.app`

**This is your backend API URL!**

## Step 2: Configure Railway Environment Variables

In Railway Dashboard → **INARA-HR** service → **Variables**, set:

### Database (Supabase)
```bash
DATABASE_URL=postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres?pgbouncer=true
DATABASE_ASYNC_URL=postgresql+asyncpg://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres?pgbouncer=true
```

### Security
```bash
# Generate your own: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_KEY=your-generated-secret-key-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### Environment
```bash
ENVIRONMENT=production
DEBUG=False
API_VERSION=v1
API_PREFIX=/api/v1
```

### CORS (IMPORTANT - Use your Vercel URL)
```bash
# Replace with your actual Vercel domain
CORS_ORIGINS=["https://your-app.vercel.app"]
```

### Cloudflare R2
```bash
R2_ENDPOINT_URL=https://f672838a09e9e6a09d08ce61b5866002.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=f2232270caa9e6bf962cc60ee8d3c5e3
R2_SECRET_ACCESS_KEY=e10c35df6da6306b5bb207161aa6b36668b20f429c9c00279d915fc7630cb8d5
R2_BUCKET_NAME=hrmis
R2_PUBLIC_URL=https://hrmis.inara.ngo
```

### Redis (Optional - for rate limiting)
```bash
# If using Upstash or other Redis service
REDIS_URL=redis://default:[password]@[host]:[port]
```

### Email (Optional)
```bash
SEND_EMAILS=True
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=True
FROM_EMAIL=noreply@inara.org
FROM_NAME=INARA HR System
APP_URL=https://your-app.vercel.app
```

## Step 3: Verify Backend is Running

1. Get your Railway backend URL (from Step 1)
2. Test health endpoint:
   ```
   https://your-backend-url.up.railway.app/health
   ```
3. Should return: `{"status":"healthy"}`

## Step 4: Configure Frontend (Vercel)

1. Go to Vercel Dashboard → Your Project → **Settings** → **Environment Variables**
2. Add:
   ```
   NEXT_PUBLIC_API_URL=https://your-railway-url.up.railway.app/api/v1
   ```
   - Replace `your-railway-url.up.railway.app` with your actual Railway domain
   - **IMPORTANT**: Include `/api/v1` at the end
3. Select **Production** (and **Preview** if needed)
4. Click **Save**
5. **Redeploy** your frontend

## Step 5: Test Connection

1. Open your Vercel app
2. Open browser console (F12)
3. Look for: `🌐 API Client initialized with baseURL: https://your-railway-url.up.railway.app/api/v1`
4. Try logging in

## Troubleshooting

### Backend not accessible
- ✅ Check Railway service is **deployed** and **running**
- ✅ Check **Public Domain** is generated in Railway Settings → Networking
- ✅ Verify `/health` endpoint works

### CORS errors
- ✅ Ensure `CORS_ORIGINS` in Railway includes your Vercel domain
- ✅ Format: `["https://your-app.vercel.app"]`
- ✅ Redeploy Railway service after changing CORS

### Database connection errors
- ✅ Verify Supabase database connection strings are correct
- ✅ Use **Connection Pooling** URL from Supabase
- ✅ Check Railway logs for database connection errors

### Environment variables not working
- ✅ Ensure variables are set in Railway (not just locally)
- ✅ Redeploy Railway service after adding variables
- ✅ Check variable names match exactly (case-sensitive)

## Railway Service Configuration

Make sure in Railway:
- **Root Directory**: `apps/api`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

The `railway.json` file in `apps/api/` should handle this automatically.

