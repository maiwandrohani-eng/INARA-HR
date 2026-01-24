# Complete Railway Environment Variables List

## All Environment Variables for Railway Backend Deployment

Copy and paste these into Railway → **INARA-HR** → **Variables**:

### 🔴 REQUIRED - Service Won't Start Without These

```bash
# Database (Supabase PostgreSQL)
# Get from: Supabase Dashboard → Settings → Database → Connection String → Connection Pooling
DATABASE_URL=postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres?pgbouncer=true
DATABASE_ASYNC_URL=postgresql+asyncpg://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres?pgbouncer=true

# Security (Generate SECRET_KEY: python -c "import secrets; print(secrets.token_urlsafe(32))")
SECRET_KEY=your-generated-secret-key-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
REFRESH_TOKEN_EXPIRE_DAYS=7

# Environment
ENVIRONMENT=production
DEBUG=False
API_VERSION=v1
API_PREFIX=/api/v1
```

### 🟡 IMPORTANT - For CORS (Frontend Connection)

```bash
# Replace with your actual Vercel domain
CORS_ORIGINS=["https://your-app.vercel.app"]
```

### 🟢 CLOUDFLARE R2 STORAGE (Already Provided)

```bash
R2_ENDPOINT_URL=https://f672838a09e9e6a09d08ce61b5866002.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=f2232270caa9e6bf962cc60ee8d3c5e3
R2_SECRET_ACCESS_KEY=e10c35df6da6306b5bb207161aa6b36668b20f429c9c00279d915fc7630cb8d5
R2_BUCKET_NAME=hrmis
R2_PUBLIC_URL=https://hrmis.inara.ngo
```

**✅ These are already correct - just copy them!**

### 🔵 OPTIONAL - Redis (Can be Empty)

```bash
# Leave empty if not using Redis, or add Upstash Redis URL
REDIS_URL=
```

### 🟣 OPTIONAL - Email Configuration

```bash
SEND_EMAILS=False
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_USE_TLS=True
FROM_EMAIL=noreply@inara.org
FROM_NAME=INARA HR System
APP_URL=https://your-app.vercel.app
```

## Complete Architecture

```
Frontend (Vercel)
    ↓ API calls
Backend (Railway) ← You are here
    ↓ Database queries
Supabase (PostgreSQL)
    ↓ File uploads/downloads
Cloudflare R2 (File Storage) ← Already configured!
```

## Quick Copy-Paste Checklist

1. ✅ Get Supabase `DATABASE_URL` and `DATABASE_ASYNC_URL`
2. ✅ Generate `SECRET_KEY`
3. ✅ Copy Cloudflare R2 variables (already provided above)
4. ✅ Set `CORS_ORIGINS` with your Vercel domain
5. ✅ Add all to Railway Variables
6. ✅ Deploy!

## Notes

- **Cloudflare R2**: Already configured correctly ✅
- **Supabase Database**: Need connection strings from Supabase Dashboard
- **SECRET_KEY**: Generate your own (never share it!)
- **CORS_ORIGINS**: Must match your Vercel frontend URL

All file uploads (employee documents, etc.) will automatically use Cloudflare R2 storage!

