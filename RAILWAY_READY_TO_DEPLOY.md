# 🚀 Railway Deployment - Ready to Deploy!

## ✅ All Information Collected

You now have everything needed:

- ✅ **Database**: Neon.tech connection string
- ✅ **Storage**: Cloudflare R2 credentials
- ✅ **Backend**: Railway service created
- ✅ **Frontend**: Vercel (already deployed)

## 📋 Complete Environment Variables for Railway

Copy these **EXACTLY** into Railway → **INARA-HR** → **Variables**:

### 🔴 REQUIRED Variables

```bash
# Database (Neon.tech)
DATABASE_URL=postgresql://neondb_owner:npg_bjk7NVPc8Rex@ep-rapid-thunder-ag48hxqf-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
DATABASE_ASYNC_URL=postgresql+asyncpg://neondb_owner:npg_bjk7NVPc8Rex@ep-rapid-thunder-ag48hxqf-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require

# Security (Generate SECRET_KEY first - see below)
SECRET_KEY=GENERATE_THIS_FIRST_MINIMUM_32_CHARACTERS
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
REFRESH_TOKEN_EXPIRE_DAYS=7

# Environment
ENVIRONMENT=production
DEBUG=False
API_VERSION=v1
API_PREFIX=/api/v1

# CORS (Replace with your actual Vercel domain)
CORS_ORIGINS=["https://your-app.vercel.app"]

# Redis (Optional - leave empty if not using)
REDIS_URL=

# Cloudflare R2 Storage
R2_ENDPOINT_URL=https://f672838a09e9e6a09d08ce61b5866002.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=f2232270caa9e6bf962cc60ee8d3c5e3
R2_SECRET_ACCESS_KEY=e10c35df6da6306b5bb207161aa6b36668b20f429c9c00279d915fc7630cb8d5
R2_BUCKET_NAME=hrmis
R2_PUBLIC_URL=https://hrmis.inara.ngo
```

## 🔐 Generate SECRET_KEY

**IMPORTANT**: You must generate a SECRET_KEY before deploying!

Run this command locally:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and replace `GENERATE_THIS_FIRST_MINIMUM_32_CHARACTERS` above.

## 📝 Step-by-Step Deployment

### Step 1: Generate SECRET_KEY
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
Copy the output.

### Step 2: Set Environment Variables in Railway
1. Go to Railway Dashboard
2. Open project: **brave-warmth**
3. Open service: **INARA-HR**
4. Click **Variables** tab
5. Add each variable from the list above
6. **IMPORTANT**: Replace `CORS_ORIGINS` with your actual Vercel domain
7. **IMPORTANT**: Replace `SECRET_KEY` with the generated value

### Step 3: Verify Service Configuration
Railway → **INARA-HR** → **Settings**:
- **Root Directory**: `apps/api` ✅
- Build/Start commands should auto-detect from `railway.json` ✅

### Step 4: Deploy!
1. Railway → **INARA-HR** → **Deployments**
2. Click **Deploy** (or it may auto-deploy after setting variables)
3. Wait 2-5 minutes for deployment

### Step 5: Generate Public Domain
1. Railway → **INARA-HR** → **Settings** → **Networking**
2. Click **Generate Domain**
3. You'll get: `https://inara-hr-production.up.railway.app`

### Step 6: Test Backend
```
https://inara-hr-production.up.railway.app/health
```
Should return: `{"success":true,"status":"healthy","environment":"production"}`

### Step 7: Configure Frontend (Vercel)
1. Vercel Dashboard → Your Project → **Settings** → **Environment Variables**
2. Add:
   ```
   NEXT_PUBLIC_API_URL=https://inara-hr-production.up.railway.app/api/v1
   ```
   (Replace with your actual Railway domain)
3. Select **Production** environment
4. **Save** and **Redeploy** frontend

### Step 8: Test Everything
1. Open your Vercel app
2. Try logging in
3. Check browser console for any errors

## ✅ Quick Checklist

- [ ] Generate SECRET_KEY
- [ ] Add all environment variables to Railway
- [ ] Replace CORS_ORIGINS with your Vercel domain
- [ ] Verify root directory is `apps/api`
- [ ] Deploy backend on Railway
- [ ] Generate public domain
- [ ] Test `/health` endpoint
- [ ] Set `NEXT_PUBLIC_API_URL` in Vercel
- [ ] Redeploy frontend
- [ ] Test login from frontend

## 🎯 Architecture

```
Frontend (Vercel)
    ↓
Backend (Railway) ← Deploy this!
    ↓
    ├─→ Neon.tech (Database) ✅ Ready!
    └─→ Cloudflare R2 (Storage) ✅ Ready!
```

## ⚠️ Important Notes

1. **CORS_ORIGINS**: Must match your Vercel frontend URL exactly
   - Format: `["https://your-app.vercel.app"]`
   - Don't forget the `https://` and brackets!

2. **SECRET_KEY**: Must be at least 32 characters
   - Use the Python command to generate a secure one
   - Never share it or commit it to git!

3. **DATABASE_ASYNC_URL**: Notice `postgresql+asyncpg://` (not `postgresql://`)
   - This is required for FastAPI async database operations

## 🆘 Troubleshooting

If deployment fails:
1. Check Railway → **Logs** for error messages
2. Verify all required variables are set
3. Check `SECRET_KEY` is at least 32 characters
4. Verify `DATABASE_URL` format is correct
5. Check root directory is `apps/api`

You're ready to deploy! 🚀

