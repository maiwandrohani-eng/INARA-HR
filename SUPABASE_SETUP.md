# Setting Up Supabase with FastAPI Backend

## Understanding the Architecture

Your app has:
- **Frontend**: Next.js (deployed on Vercel) ✅
- **Backend**: FastAPI (Python) - **Needs to be deployed** ⚠️
- **Database**: Supabase PostgreSQL ✅ (you have the tokens)
- **Storage**: Cloudflare R2 ✅

## Step 1: Get Supabase Database Connection String

1. Go to your Supabase project: https://supabase.com/dashboard
2. Click **Settings** → **Database**
3. Scroll down to **Connection String**
4. Select **Connection pooling** (recommended for serverless)
5. Copy the connection string. It should look like:
   ```
   postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres?pgbouncer=true
   ```

### For Async (FastAPI):
You need to convert it to `postgresql+asyncpg://`:
```
postgresql+asyncpg://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres?pgbouncer=true
```

## Step 2: Deploy FastAPI Backend

You need to deploy your FastAPI backend to one of these platforms:

### Option A: Railway (Recommended - Easiest)
1. Go to https://railway.app
2. Create new project
3. Connect GitHub repository
4. Add service → Select your repo
5. Set root directory to `apps/api`
6. Railway auto-detects Python
7. Add environment variables (see Step 3)
8. Deploy!

### Option B: Render
1. Go to https://render.com
2. Create new **Web Service**
3. Connect GitHub repository
4. Settings:
   - **Root Directory**: `apps/api`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables (see Step 3)

### Option C: Fly.io
1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. `cd apps/api`
3. `fly launch`
4. Follow prompts
5. Add environment variables: `fly secrets set KEY=value`

## Step 3: Backend Environment Variables

Set these in your backend deployment platform:

### Database (Supabase)
```bash
# Use Connection Pooling URL from Supabase
DATABASE_URL=postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres?pgbouncer=true

# Async version for FastAPI
DATABASE_ASYNC_URL=postgresql+asyncpg://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres?pgbouncer=true
```

### Security
```bash
# Generate a secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

SECRET_KEY=your-generated-secret-key-here
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
CORS_ORIGINS=["https://your-app.vercel.app","https://your-custom-domain.com"]
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
If you want rate limiting, use Upstash (serverless Redis):
1. Go to https://upstash.com
2. Create Redis database
3. Copy connection URL:
```bash
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

## Step 4: Get Backend API URL

After deploying, you'll get a URL like:
- Railway: `https://your-app.railway.app`
- Render: `https://your-app.onrender.com`
- Fly.io: `https://your-app.fly.dev`

## Step 5: Configure Frontend (Vercel)

1. Go to Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.com/api/v1
   ```
3. Redeploy frontend

## Step 6: Run Database Migrations

After backend is deployed, you need to create tables. Options:

### Option A: Using Supabase SQL Editor
1. Go to Supabase Dashboard → SQL Editor
2. Run the schema creation script (if you have one)

### Option B: Using Python locally
1. Install dependencies: `pip install -r apps/api/requirements.txt`
2. Set environment variables (DATABASE_URL, etc.)
3. Run: `python apps/api/scripts/init_db.py` (if exists)

### Option C: Using Alembic (if configured)
1. `cd apps/api`
2. `alembic upgrade head`

## Important Notes

### Supabase Tokens You Shared
- `anon public api` - This is for Supabase's REST API (not used by your FastAPI backend)
- `service_role SECRET_KEY` - This is also for Supabase API (not used by your FastAPI backend)

**Your FastAPI backend uses:**
- `DATABASE_URL` / `DATABASE_ASYNC_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT token signing key (generate your own)

### Supabase vs Neon.tech
Both are PostgreSQL databases. The connection string format is the same:
- Neon: `postgresql://user:pass@host/db`
- Supabase: `postgresql://postgres.ref:pass@host:port/db`

## Quick Checklist

- [ ] Get Supabase database connection string
- [ ] Deploy FastAPI backend (Railway/Render/Fly.io)
- [ ] Set all backend environment variables
- [ ] Test backend health endpoint: `https://your-backend.com/health`
- [ ] Run database migrations/create tables
- [ ] Set `NEXT_PUBLIC_API_URL` in Vercel
- [ ] Redeploy frontend
- [ ] Test login from frontend

## Troubleshooting

### "Cannot connect to server" error
- ✅ Check backend is deployed and running
- ✅ Check backend URL is correct in Vercel env vars
- ✅ Check backend `/health` endpoint works
- ✅ Check CORS allows your Vercel domain

### Database connection errors
- ✅ Verify DATABASE_URL is correct (connection pooling URL)
- ✅ Check DATABASE_ASYNC_URL uses `postgresql+asyncpg://`
- ✅ Verify Supabase database is accessible
- ✅ Check firewall/network restrictions

### CORS errors
- ✅ Ensure CORS_ORIGINS includes your Vercel domain
- ✅ Format: `["https://your-app.vercel.app"]`
- ✅ Redeploy backend after changing CORS settings

