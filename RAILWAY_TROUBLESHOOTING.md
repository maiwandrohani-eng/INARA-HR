# Railway Deployment Troubleshooting

## Error: "The train has not arrived at the station"

This means your Railway service hasn't deployed successfully or isn't running.

## Step-by-Step Fix

### Step 1: Check Railway Deployment Status

1. Go to Railway Dashboard: https://railway.app/dashboard
2. Click on project: **brave-warmth**
3. Click on service: **INARA-HR**
4. Check the **Deployments** tab:
   - Is there a deployment? 
   - What's the status? (Building, Deployed, Failed)
   - Check the latest deployment logs

### Step 2: Check Build Logs

1. In Railway → **INARA-HR** service
2. Click on **Deployments** tab
3. Click on the latest deployment
4. Check **Build Logs** for errors

**Common build errors:**
- Missing `requirements.txt` (should be in `apps/api/`)
- Python version issues
- Missing dependencies

### Step 3: Check Runtime Logs

1. In Railway → **INARA-HR** service
2. Click on **Logs** tab (or **View Logs**)
3. Look for errors

**Common runtime errors:**
- `DATABASE_URL` not set
- `SECRET_KEY` not set
- Import errors
- Database connection failed

### Step 4: Verify Required Environment Variables

In Railway → **INARA-HR** → **Variables**, ensure these are set:

```bash
# REQUIRED - Service won't start without these
DATABASE_URL=postgresql://...
DATABASE_ASYNC_URL=postgresql+asyncpg://...
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256

# REQUIRED for production
ENVIRONMENT=production
DEBUG=False

# RECOMMENDED - Set to avoid errors
CORS_ORIGINS=["https://your-app.vercel.app"]
```

### Step 5: Verify Railway Configuration

In Railway → **INARA-HR** → **Settings**:

1. **Root Directory**: Should be `apps/api`
2. **Build Command**: Should auto-detect from `railway.json`
3. **Start Command**: Should be `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Step 6: Check Service Health

1. In Railway → **INARA-HR** service
2. Go to **Settings** → **Networking**
3. Is there a **Public Domain**? 
   - If not, click **Generate Domain**
4. Once domain is generated, test:
   ```
   https://your-domain.up.railway.app/health
   ```

### Step 7: Common Issues & Fixes

#### Issue 1: Build Fails
**Error**: `ModuleNotFoundError` or `pip install` fails
**Fix**: 
- Ensure `requirements.txt` exists in `apps/api/`
- Check Railway is using correct root directory (`apps/api`)
- Check build logs for specific package errors

#### Issue 2: Service Crashes on Start
**Error**: Service starts then immediately stops
**Fix**:
- Check runtime logs for error messages
- Verify all required environment variables are set
- Check `SECRET_KEY` is at least 32 characters
- Verify database connection strings are correct

#### Issue 3: Database Connection Fails
**Error**: `could not connect to server` or `database does not exist`
**Fix**:
- Verify `DATABASE_URL` and `DATABASE_ASYNC_URL` are correct
- For Supabase, use **Connection Pooling** URL
- Ensure Supabase database is accessible (check firewall/IP restrictions)
- Test connection string locally first

#### Issue 4: Missing Environment Variables
**Error**: `Settings validation error` or `DATABASE_URL not set`
**Fix**:
- Add all required variables in Railway → Variables
- Format `CORS_ORIGINS` as JSON array: `["https://domain.com"]`
- Redeploy after adding variables

#### Issue 5: Port Configuration
**Error**: Service not responding
**Fix**:
- Railway uses `$PORT` environment variable automatically
- Don't hardcode port 8000
- Start command should use `--port $PORT`

### Step 8: Manual Redeploy

If all else fails:

1. Go to Railway → **INARA-HR** → **Settings**
2. Scroll to **Danger Zone**
3. Click **Redeploy** or **Clear Build Cache**
4. Trigger a new deployment

### Step 9: Verify Deployment Success

Once deployed, you should see in logs:
```
INFO:     Uvicorn running on http://0.0.0.0:XXXX (Press CTRL+C to quit)
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

Test endpoints:
- Health: `https://your-domain.up.railway.app/health`
- API Docs: `https://your-domain.up.railway.app/api/v1/docs`

## Quick Checklist

- [ ] Service has a deployment (check Deployments tab)
- [ ] Build completed successfully (check build logs)
- [ ] Service is running (check runtime logs)
- [ ] All required env variables are set (DATABASE_URL, SECRET_KEY, etc.)
- [ ] Root directory is set to `apps/api`
- [ ] Public domain is generated (Settings → Networking)
- [ ] `/health` endpoint returns `{"status":"healthy"}`

## Still Not Working?

Share these details:
1. Latest deployment status (from Railway Deployments tab)
2. Latest build logs (copy errors)
3. Latest runtime logs (copy errors)
4. Which environment variables you've set (list names, not values)

