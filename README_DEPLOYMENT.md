# INARA HR - Vercel Deployment Guide

## Quick Start

This guide will help you deploy the INARA HR System to Vercel.

### Architecture

- **Frontend**: Next.js app deployed on Vercel
- **Backend**: FastAPI deployed separately (Railway/Render/Fly.io recommended)
- **Database**: Neon.tech PostgreSQL
- **File Storage**: Cloudflare R2
- **Cache**: Upstash Redis (serverless-friendly)

## Deployment Steps

### 1. Frontend Deployment (Vercel)

1. **Connect Repository**
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "Add New Project"
   - Import: `maiwandrohani-eng/INARA-HR`
   - Set **Root Directory**: `apps/frontend`

2. **Environment Variables**
   - Go to Project Settings → Environment Variables
   - Add: `NEXT_PUBLIC_API_URL=https://your-api-domain.com/api/v1`
   - Replace with your actual backend API URL

3. **Deploy**
   - Click "Deploy"
   - Vercel will automatically build and deploy

### 2. Backend Deployment

Choose one platform:

#### Option A: Railway (Recommended)
1. Go to [Railway](https://railway.app)
2. Create new project from GitHub
3. Set root directory: `apps/api`
4. Add environment variables (see `VERCEL_ENV_SETUP.md`)
5. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

#### Option B: Render
1. Go to [Render](https://render.com)
2. Create new Web Service
3. Connect GitHub repo
4. Set root directory: `apps/api`
5. Build command: `pip install -r requirements.txt`
6. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

#### Option C: Fly.io
1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Run `flyctl launch` in `apps/api` directory
3. Configure `fly.toml`
4. Set secrets: `flyctl secrets set KEY=value`

### 3. Environment Variables

See `VERCEL_ENV_SETUP.md` for complete list.

**Required for Backend:**
- Database: Neon.tech connection string
- Redis: Upstash or Redis Cloud URL
- R2: Cloudflare R2 credentials
- Security: SECRET_KEY (generate with Python)

### 4. Post-Deployment

1. **Run Migrations**
   ```bash
   cd apps/api
   alembic upgrade head
   ```

2. **Seed Database**
   ```bash
   python seed_roles_permissions.py
   python create_admin.py
   ```

3. **Verify**
   - Frontend: https://your-app.vercel.app
   - API Health: https://your-api-domain.com/health
   - API Docs: https://your-api-domain.com/api/v1/docs

## Configuration Files

- `VERCEL_DEPLOYMENT.md` - Detailed deployment guide
- `VERCEL_ENV_SETUP.md` - Complete environment variables list
- `DEPLOYMENT_CHECKLIST.md` - Step-by-step checklist

## Important URLs

- **GitHub**: https://github.com/maiwandrohani-eng/INARA-HR
- **Database**: Neon.tech dashboard
- **File Storage**: Cloudflare R2 dashboard
- **Frontend**: Your Vercel deployment URL
- **Backend**: Your backend platform URL

## Support

For issues, check:
- `VERCEL_DEPLOYMENT.md` for troubleshooting
- Vercel documentation: https://vercel.com/docs
- Railway docs: https://docs.railway.app
- Neon docs: https://neon.tech/docs

## Security Notes

1. Never commit `.env` files
2. Use environment variables in platforms, not code
3. Generate strong SECRET_KEY
4. Enable HTTPS everywhere
5. Configure CORS correctly
6. Use App Passwords for email (not regular passwords)

