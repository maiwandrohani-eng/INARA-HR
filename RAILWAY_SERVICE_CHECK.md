# Railway Service Status Check

## Current Status
- ✅ Domain generated: `inara-hr-production.up.railway.app`
- ❌ Health endpoint returns 404: Service not running properly

## Diagnose the Issue

### Step 1: Check Service Status in Railway

1. Go to Railway Dashboard: https://railway.app/dashboard
2. Click on project: **brave-warmth**
3. Click on service: **INARA-HR**
4. Check the **Deployments** tab:
   - Is there a deployment?
   - What's the status? (Building, Deployed, Failed, Crashed)

### Step 2: Check Runtime Logs

1. In Railway → **INARA-HR** service
2. Click on **Logs** tab
3. Look for:
   - ✅ Success: `INFO:     Uvicorn running on http://0.0.0.0:XXXX`
   - ✅ Success: `Application startup complete`
   - ❌ Errors: `DATABASE_URL not set`
   - ❌ Errors: `SECRET_KEY not set`
   - ❌ Errors: Database connection failures
   - ❌ Errors: Import errors

### Step 3: Verify Required Environment Variables

In Railway → **INARA-HR** → **Variables**, ensure these are ALL set:

```bash
# CRITICAL - Service won't start without these
DATABASE_URL=postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres?pgbouncer=true
DATABASE_ASYNC_URL=postgresql+asyncpg://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres?pgbouncer=true
SECRET_KEY=your-generated-secret-key-minimum-32-characters
REDIS_URL= (can be empty string "" if not using Redis)

# Required for production
ENVIRONMENT=production
DEBUG=False
API_VERSION=v1
API_PREFIX=/api/v1

# Important for CORS
CORS_ORIGINS=["https://your-vercel-app.vercel.app"]
```

**Missing any of these?** → Service will crash on startup

### Step 4: Check Build Logs

1. Railway → **INARA-HR** → **Deployments**
2. Click on latest deployment
3. Check **Build Logs** for errors:
   - `pip install` failures
   - Missing dependencies
   - Build errors

### Step 5: Common Issues & Fixes

#### Issue: Service Crashes Immediately
**Symptom**: Deployment shows "Deployed" but logs show immediate crash
**Fix**: 
- Check for missing environment variables
- Verify DATABASE_URL is correct
- Check SECRET_KEY is set and valid

#### Issue: Database Connection Fails
**Symptom**: Logs show "Database connection failed"
**Fix**:
- Verify Supabase connection strings
- Use **Connection Pooling** URL from Supabase
- Check Supabase database is accessible

#### Issue: Import Errors
**Symptom**: Logs show `ModuleNotFoundError`
**Fix**:
- Check `requirements.txt` exists in `apps/api/`
- Verify root directory is `apps/api`
- Rebuild service

#### Issue: Port Configuration
**Symptom**: Service doesn't respond
**Fix**:
- Railway uses `$PORT` automatically
- Don't hardcode port 8000 or 8080
- Start command should be: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## Quick Fix Checklist

1. [ ] Check Railway Logs for error messages
2. [ ] Verify all required env variables are set
3. [ ] Check DATABASE_URL is correct (Supabase connection pooling URL)
4. [ ] Generate SECRET_KEY if missing: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
5. [ ] Verify root directory is `apps/api`
6. [ ] Redeploy service after fixing env vars

## What to Share

If still not working, share:
1. Latest Railway Logs (copy error messages)
2. Deployment status (from Deployments tab)
3. Which environment variables you've set (names only, not values)

