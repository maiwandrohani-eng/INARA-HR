# Vercel Deployment Guide

This guide covers deploying the INARA HR System to Vercel.

## Architecture Overview

For production deployment, we recommend:
- **Frontend**: Deploy Next.js app on Vercel (native support)
- **Backend API**: Deploy FastAPI separately on Railway, Render, Fly.io, or similar (better for long-running connections, background tasks, and file uploads)

However, Vercel also supports Python serverless functions if you prefer a unified deployment.

## Prerequisites

1. Vercel account (https://vercel.com)
2. GitHub repository connected to Vercel
3. Neon.tech database configured
4. Cloudflare R2 bucket configured
5. Environment variables prepared

## Option 1: Frontend on Vercel + API on Separate Service (Recommended)

### Step 1: Deploy Frontend to Vercel

1. **Connect Repository**
   - Go to Vercel Dashboard
   - Click "Add New Project"
   - Import your GitHub repository: `maiwandrohani-eng/INARA-HR`
   - Set Root Directory to `apps/frontend`

2. **Configure Build Settings**
   - Framework Preset: Next.js
   - Build Command: `npm run build`
   - Output Directory: `.next`
   - Install Command: `npm install`

3. **Set Environment Variables** (in Vercel Dashboard → Project Settings → Environment Variables):

```bash
# API Configuration
NEXT_PUBLIC_API_URL=https://your-api-domain.com/api/v1

# Environment
NODE_ENV=production
```

4. **Deploy**
   - Click "Deploy"
   - Vercel will build and deploy your Next.js app

### Step 2: Deploy Backend API Separately

Deploy the FastAPI backend to one of these services:

**Railway (Recommended)**
- Connect GitHub repo
- Set Root Directory: `apps/api`
- Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Add environment variables (see below)

**Render**
- Create new Web Service
- Set Root Directory: `apps/api`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

**Fly.io**
- Use `flyctl launch` in the `apps/api` directory
- Configure `fly.toml` for Python runtime

### Step 3: Update Frontend API URL

Update the frontend environment variable in Vercel:
```
NEXT_PUBLIC_API_URL=https://your-api-domain.com/api/v1
```

## Option 2: Full Stack on Vercel (Serverless Functions)

If you want everything on Vercel, you'll need to adapt FastAPI to serverless functions. This approach has limitations:
- Function timeout limits (10s on Hobby, 60s on Pro)
- Cold starts
- Limited background job support

### Setup Serverless API

1. Create `api/serverless/index.py` in your project root (outside apps folder)
2. Use Vercel's Python runtime wrapper for FastAPI
3. Configure `vercel.json` to route API requests to serverless functions

**Note**: This option requires significant refactoring and is not recommended for production workloads with file uploads and background tasks.

## Environment Variables

### Frontend (Vercel)

```bash
NEXT_PUBLIC_API_URL=https://your-api-domain.com/api/v1
NODE_ENV=production
```

### Backend API

Set these in your backend deployment platform (Railway/Render/etc.):

```bash
# Database (Neon.tech)
DATABASE_URL=postgresql://neondb_owner:npg_bjk7NVPc8Rex@ep-rapid-thunder-ag48hxqf-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
DATABASE_ASYNC_URL=postgresql+asyncpg://neondb_owner:npg_bjk7NVPc8Rex@ep-rapid-thunder-ag48hxqf-pooler.c-2.eu-central-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require

# Redis (Use Upstash Redis for serverless, or Redis Cloud)
REDIS_URL=redis://your-redis-url:6379

# Security
SECRET_KEY=your-secret-key-minimum-32-characters-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=480
REFRESH_TOKEN_EXPIRE_DAYS=7

# Environment
ENVIRONMENT=production
DEBUG=False

# CORS - Add your Vercel domain
CORS_ORIGINS=["https://your-app.vercel.app","https://your-custom-domain.com"]

# Cloudflare R2 File Storage
R2_ENDPOINT_URL=https://f672838a09e9e6a09d08ce61b5866002.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=f2232270caa9e6bf962cc60ee8d3c5e3
R2_SECRET_ACCESS_KEY=e10c35df6da6306b5bb207161aa6b36668b20f429c9c00279d915fc7630cb8d5
R2_BUCKET_NAME=hrmis
R2_PUBLIC_URL=https://hrmis.inara.ngo

# Email Configuration
SEND_EMAILS=True
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=True
FROM_EMAIL=noreply@inara.org
FROM_NAME=INARA HR System
APP_URL=https://your-vercel-domain.vercel.app

# Rate Limiting
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
RATE_LIMIT_AUTH_PER_MINUTE=5

# File Upload Limits
MAX_FILE_SIZE_MB=10

# Request Timeouts
REQUEST_TIMEOUT_SECONDS=30
UPLOAD_TIMEOUT_SECONDS=300

# Sentry (Optional)
SENTRY_DSN=
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1

# Organization
ORG_NAME=INARA
ORG_TIMEZONE=UTC
DEFAULT_COUNTRY=US
```

## Database Setup

### Neon.tech PostgreSQL

1. Your database is already configured at:
   ```
   postgresql://neondb_owner:npg_bjk7NVPc8Rex@ep-rapid-thunder-ag48hxqf-pooler.c-2.eu-central-1.aws.neon.tech/neondb
   ```

2. Run migrations on first deployment:
   ```bash
   cd apps/api
   alembic upgrade head
   ```

3. Seed initial data (if needed):
   ```bash
   python seed_roles_permissions.py
   python create_admin.py
   ```

## Cloudflare R2 Setup

1. Your R2 bucket is already configured:
   - Bucket: `hrmis`
   - Public URL: `https://hrmis.inara.ngo`
   - Endpoint: `https://f672838a09e9e6a09d08ce61b5866002.r2.cloudflarestorage.com`

2. Configure R2 Public Access:
   - Go to Cloudflare Dashboard → R2
   - Select bucket `hrmis`
   - Enable "Public Access" if you want direct file access
   - Configure custom domain `hrmis.inara.ngo` in R2 settings

## Redis Setup

For serverless deployments, use:
- **Upstash Redis** (serverless-friendly): https://upstash.com
- **Redis Cloud**: https://redis.com/cloud
- Or include Redis in your backend deployment (Railway, Render, etc.)

## Post-Deployment Checklist

- [ ] Frontend deployed and accessible
- [ ] Backend API deployed and accessible
- [ ] Database migrations run
- [ ] Initial admin user created
- [ ] CORS configured correctly
- [ ] File uploads working (test with R2)
- [ ] Email notifications working (test password reset)
- [ ] API health check: `GET /health`
- [ ] Frontend can connect to API
- [ ] Authentication flow working

## Custom Domain Setup

### Frontend (Vercel)

1. In Vercel Dashboard → Project Settings → Domains
2. Add your custom domain
3. Follow DNS configuration instructions
4. Update `NEXT_PUBLIC_API_URL` to use the same domain or subdomain

### Backend API

1. Configure custom domain in your hosting platform
2. Update CORS_ORIGINS to include custom domain
3. Update frontend `NEXT_PUBLIC_API_URL`

## Monitoring & Logs

- **Vercel**: View logs in Vercel Dashboard → Deployments → Logs
- **Backend**: Use platform logs (Railway/Render logs)
- **Sentry**: Configure SENTRY_DSN for error tracking
- **Health Checks**: Monitor `/health` endpoint

## Troubleshooting

### CORS Errors
- Ensure `CORS_ORIGINS` includes your Vercel domain
- Check that `NEXT_PUBLIC_API_URL` matches backend URL

### File Upload Issues
- Verify R2 credentials are correct
- Check R2 bucket permissions
- Ensure R2_PUBLIC_URL is configured

### Database Connection Issues
- Verify DATABASE_URL format (Neon requires SSL)
- Check DATABASE_ASYNC_URL uses `postgresql+asyncpg://`
- Ensure database is accessible from deployment region

### Build Failures
- Check Node.js version (Vercel auto-detects)
- Verify all dependencies in package.json
- Review build logs for specific errors

## Support

For issues specific to:
- **Vercel**: https://vercel.com/docs
- **Neon.tech**: https://neon.tech/docs
- **Cloudflare R2**: https://developers.cloudflare.com/r2

## Next Steps

After successful deployment:
1. Run full system tests
2. Configure monitoring and alerts
3. Set up automated backups
4. Review security settings
5. Document admin credentials securely

