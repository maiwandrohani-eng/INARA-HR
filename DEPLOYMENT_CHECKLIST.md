# Deployment Checklist

Use this checklist to ensure a smooth deployment to Vercel.

## Pre-Deployment

### 1. Code Preparation
- [ ] All code committed to GitHub
- [ ] All tests passing locally
- [ ] No console errors or warnings
- [ ] Environment variables documented
- [ ] `.env` files added to `.gitignore`

### 2. Database Setup (Neon.tech)
- [ ] Database created and accessible
- [ ] Connection string saved securely
- [ ] Test connection from local machine
- [ ] Database migrations ready (`alembic upgrade head`)

### 3. Cloudflare R2 Setup
- [ ] R2 bucket created (`hrmis`)
- [ ] R2 credentials generated
- [ ] Custom domain configured (`hrmis.inara.ngo`)
- [ ] Public access enabled (if needed)
- [ ] Test upload/download from local

### 4. Redis Setup
- [ ] Redis instance created (Upstash/Railway/Cloud)
- [ ] Connection URL saved
- [ ] Test connection from local

### 5. Email Configuration
- [ ] SMTP credentials ready
- [ ] App password created (for Gmail)
- [ ] Test email sending locally

## Vercel Frontend Deployment

### 1. Project Setup
- [ ] Vercel account created
- [ ] GitHub repository connected
- [ ] Project created in Vercel
- [ ] Root directory set to `apps/frontend`

### 2. Environment Variables (Vercel)
- [ ] `NEXT_PUBLIC_API_URL` set to backend API URL
- [ ] Variables set for Production environment
- [ ] Variables set for Preview environment (if needed)

### 3. Build Configuration
- [ ] Framework: Next.js
- [ ] Build Command: `npm run build`
- [ ] Output Directory: `.next`
- [ ] Install Command: `npm install`

### 4. Deployment
- [ ] Initial deployment triggered
- [ ] Build completes successfully
- [ ] Frontend accessible at Vercel URL

## Backend API Deployment

### Choose Platform: Railway / Render / Fly.io

### Railway Setup
- [ ] Railway account created
- [ ] New project created
- [ ] GitHub repository connected
- [ ] Root directory set to `apps/api`
- [ ] Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- [ ] Environment variables configured (see VERCEL_ENV_SETUP.md)
- [ ] Custom domain configured (if needed)

### Render Setup
- [ ] Render account created
- [ ] New Web Service created
- [ ] GitHub repository connected
- [ ] Root directory: `apps/api`
- [ ] Build command: `pip install -r requirements.txt`
- [ ] Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- [ ] Environment variables configured
- [ ] Custom domain configured (if needed)

### Fly.io Setup
- [ ] Fly.io account created
- [ ] `flyctl` installed
- [ ] `flyctl launch` run in `apps/api`
- [ ] `fly.toml` configured correctly
- [ ] Environment variables set via `flyctl secrets set`
- [ ] App deployed with `flyctl deploy`

## Post-Deployment

### 1. Database
- [ ] Run migrations: `alembic upgrade head`
- [ ] Seed roles/permissions: `python seed_roles_permissions.py`
- [ ] Create admin user: `python create_admin.py`
- [ ] Verify database connection from API

### 2. API Verification
- [ ] Health check: `GET /health` returns 200
- [ ] API docs accessible: `GET /api/v1/docs`
- [ ] Test authentication endpoint
- [ ] Test file upload (verify R2)
- [ ] Check API logs for errors

### 3. Frontend Verification
- [ ] Frontend loads without errors
- [ ] Can navigate to login page
- [ ] API calls working (check network tab)
- [ ] No CORS errors in console
- [ ] Images loading correctly

### 4. Integration Testing
- [ ] User can register/login
- [ ] User can access dashboard
- [ ] File upload works (test with R2)
- [ ] Email notifications work (test password reset)
- [ ] All major features accessible

### 5. Security
- [ ] HTTPS enabled
- [ ] CORS configured correctly
- [ ] Environment variables secure (not in code)
- [ ] `SECRET_KEY` is strong and unique
- [ ] Rate limiting enabled
- [ ] Error messages don't expose sensitive info

### 6. Monitoring
- [ ] Logs accessible
- [ ] Error tracking configured (Sentry)
- [ ] Health checks monitored
- [ ] Database connections monitored

### 7. Custom Domain (Optional)
- [ ] Frontend custom domain configured in Vercel
- [ ] Backend custom domain configured
- [ ] DNS records configured correctly
- [ ] SSL certificates active
- [ ] Update `NEXT_PUBLIC_API_URL` and `CORS_ORIGINS` if needed

## Documentation
- [ ] Deployment guide reviewed
- [ ] Environment variables documented
- [ ] Admin credentials secured
- [ ] Team members have access (if needed)
- [ ] Backup procedures documented

## Rollback Plan
- [ ] Previous deployment version identified
- [ ] Database backup procedure known
- [ ] Rollback steps documented
- [ ] Test rollback procedure (optional)

## Final Verification
- [ ] All checklist items completed
- [ ] System tested end-to-end
- [ ] Team notified of deployment
- [ ] Monitoring alerts configured
- [ ] Support contacts documented

---

## Quick Reference

### Vercel Dashboard
- Frontend URL: https://vercel.com/dashboard
- Project Settings → Environment Variables
- Project Settings → Domains

### Backend Platform
- Railway: https://railway.app
- Render: https://render.com
- Fly.io: https://fly.io

### Services
- Neon Database: https://neon.tech
- Cloudflare R2: https://dash.cloudflare.com
- Upstash Redis: https://upstash.com

### Important URLs
- API Health: `https://your-api-domain.com/health`
- API Docs: `https://your-api-domain.com/api/v1/docs`
- Frontend: `https://your-app.vercel.app`

---

## Troubleshooting

### Build Fails
- Check build logs in Vercel
- Verify Node.js version
- Check for dependency errors
- Review `package.json` scripts

### API Connection Errors
- Verify `NEXT_PUBLIC_API_URL` is correct
- Check backend is deployed and running
- Verify CORS configuration
- Check network/firewall rules

### Database Connection Errors
- Verify DATABASE_URL format
- Check SSL requirements (Neon requires SSL)
- Verify credentials
- Check database is accessible

### File Upload Errors
- Verify R2 credentials
- Check bucket permissions
- Verify R2_PUBLIC_URL configuration
- Check file size limits

### CORS Errors
- Verify CORS_ORIGINS includes frontend URL
- Check for trailing slashes
- Ensure HTTPS in production
- Verify origin header matches exactly

