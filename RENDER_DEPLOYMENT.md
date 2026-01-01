# Deploy Backend to Render (Free Alternative)

## Why Render?
- ✅ Free tier available (with some limitations)
- ✅ Easy deployment from GitHub
- ✅ Automatic SSL/HTTPS
- ✅ Similar to Railway but allows web services on free tier

## Step-by-Step Deployment

### Step 1: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub (free)
3. Connect your GitHub account

### Step 2: Create New Web Service
1. Click **New** → **Web Service**
2. Connect your repository: `maiwandrohani-eng/INARA-HR`
3. Configure:
   - **Name**: `inara-hr-api` (or any name)
   - **Root Directory**: `apps/api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Select **Free** (or paid if you prefer)

### Step 3: Set Environment Variables
In Render → Your Service → **Environment**, add:

```bash
# Database (Supabase)
DATABASE_URL=postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres?pgbouncer=true
DATABASE_ASYNC_URL=postgresql+asyncpg://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres?pgbouncer=true

# Security
SECRET_KEY=your-generated-secret-key-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
REFRESH_TOKEN_EXPIRE_DAYS=7

# Environment
ENVIRONMENT=production
DEBUG=False
API_VERSION=v1
API_PREFIX=/api/v1

# CORS (Use your Vercel domain)
CORS_ORIGINS=["https://your-app.vercel.app"]

# Cloudflare R2
R2_ENDPOINT_URL=https://f672838a09e9e6a09d08ce61b5866002.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=f2232270caa9e6bf962cc60ee8d3c5e3
R2_SECRET_ACCESS_KEY=e10c35df6da6306b5bb207161aa6b36668b20f429c9c00279d915fc7630cb8d5
R2_BUCKET_NAME=hrmis
R2_PUBLIC_URL=https://hrmis.inara.ngo

# Redis (Optional - can be empty)
REDIS_URL=
```

### Step 4: Deploy
1. Click **Create Web Service**
2. Render will automatically:
   - Clone your repo
   - Install dependencies
   - Start the service
3. Wait 5-10 minutes for first deployment

### Step 5: Get Your Backend URL
After deployment, Render provides a URL like:
```
https://inara-hr-api.onrender.com
```

### Step 6: Test Health Endpoint
```
https://inara-hr-api.onrender.com/health
```
Should return: `{"success":true,"status":"healthy"}`

### Step 7: Configure Vercel Frontend
In Vercel → Settings → Environment Variables:
```
NEXT_PUBLIC_API_URL=https://inara-hr-api.onrender.com/api/v1
```

## Render Free Tier Limitations
- ⚠️ Service spins down after 15 minutes of inactivity
- ⚠️ First request after spin-down takes ~30 seconds (cold start)
- ⚠️ 750 hours/month free (enough for always-on if single service)

**Solution for always-on**: Upgrade to paid plan ($7/month) or use Fly.io

## Alternative: Fly.io (Also Free)

Fly.io also offers free tier with better performance:

1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. `cd apps/api`
3. `fly launch`
4. Follow prompts
5. Set environment variables: `fly secrets set KEY=value`
6. Deploy: `fly deploy`

## Quick Comparison

| Platform | Free Tier | Always-On | Best For |
|----------|-----------|-----------|----------|
| **Render** | ✅ Yes | ❌ No (spins down) | Development, testing |
| **Fly.io** | ✅ Yes | ✅ Yes | Production (better performance) |
| **Railway** | ❌ No (limited) | ✅ Yes (paid) | Production (if upgraded) |

## Recommendation

For **production use**, I recommend:
1. **Fly.io** (free, always-on, better performance)
2. **Render** (free, but spins down - good for testing)
3. **Railway** (requires upgrade, but good if you prefer it)

Would you like me to help you set up Fly.io or Render?

