# Update Railway CORS Configuration

## Current Issue
CORS error: Vercel domain `https://hrmis-8rl0hghor-maiwand-rohanis-projects.vercel.app` is blocked.

## Solution
I've updated the backend code to automatically allow **all Vercel preview deployments** using a regex pattern (`*.vercel.app`).

## What You Need to Do

### Option 1: No Action Required (Recommended)
The code now automatically allows all `*.vercel.app` domains, so you don't need to update Railway variables. Just redeploy Railway after the code is pushed.

### Option 2: Add Specific Vercel Domain (If you want explicit control)
If you prefer to explicitly list domains, update Railway:

1. Go to **Railway Dashboard** → **INARA-HR** service
2. **Variables** tab
3. Find `CORS_ORIGINS`
4. Update to include your Vercel domain:

**As JSON array:**
```json
["http://localhost:3000","http://localhost:3001","http://localhost:3002","http://localhost:8000","https://hrmis-8rl0hghor-maiwand-rohanis-projects.vercel.app"]
```

**OR as comma-separated list:**
```
http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:8000,https://hrmis-8rl0hghor-maiwand-rohanis-projects.vercel.app
```

5. **Save** (Railway will auto-redeploy)

## After Code Update
Once the code is pushed to GitHub:
1. Railway will auto-detect the change
2. It will rebuild and redeploy
3. CORS will automatically allow all `*.vercel.app` domains

## Test
After Railway redeploys:
1. Clear browser cache
2. Try login again
3. Should work! ✅

