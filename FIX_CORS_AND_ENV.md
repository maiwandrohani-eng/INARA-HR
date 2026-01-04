# Fix: CORS Error and Environment Variable

## Two Issues Found

### Issue 1: Environment Variable Not Set
Console shows: `Backend URL: https://your-railway-url.up.railway.app/api/v1`
This is a placeholder! The actual Railway URL should be used.

### Issue 2: CORS Error
```
Access-Control-Allow-Origin header is missing
Vercel domain: https://hrmis-8rx5m4w4m-maiwand-rohanis-projects.vercel.app
```

## Fix 1: Set Environment Variable in Vercel

**CRITICAL**: You MUST set this in Vercel environment variables:

1. Go to **Vercel Dashboard** → Your Project
2. **Settings** → **Environment Variables**
3. Add:
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://inara-hr-production.up.railway.app/api/v1`
   - **Environment**: Production (and Preview)
4. **Save**

**IMPORTANT**: After setting, you MUST redeploy for it to take effect!

## Fix 2: Update CORS in Railway

Your Vercel domain needs to be in Railway's CORS settings:

1. Go to **Railway Dashboard** → **INARA-HR** service
2. **Variables** tab
3. Find `CORS_ORIGINS`
4. Update it to include your Vercel domain:

```bash
CORS_ORIGINS=["https://hrmis-8rx5m4w4m-maiwand-rohanis-projects.vercel.app","https://your-custom-domain.vercel.app"]
```

**OR** if you want to allow all Vercel preview deployments:

```bash
CORS_ORIGINS=["https://*.vercel.app","https://hrmis-8rx5m4w4m-maiwand-rohanis-projects.vercel.app"]
```

5. **Save** and Railway will auto-redeploy

## Step-by-Step

### Step 1: Set Vercel Environment Variable
- Key: `NEXT_PUBLIC_API_URL`
- Value: `https://inara-hr-production.up.railway.app/api/v1`
- Save

### Step 2: Redeploy Vercel
After setting env var, trigger new deployment:
- Push a commit, OR
- Click "Redeploy" on latest deployment

### Step 3: Update Railway CORS
- Railway → Variables → `CORS_ORIGINS`
- Set to: `["https://hrmis-8rx5m4w4m-maiwand-rohanis-projects.vercel.app"]`
- Save (auto-redeploys)

### Step 4: Test
After both redeploy:
1. Clear browser cache (or hard refresh)
2. Open Vercel app
3. Check console - should show correct Railway URL
4. Try login again

## Quick Fix Commands

I'll create a commit to trigger Vercel redeploy after you set the env var:

```bash
# After setting env var in Vercel, run:
git commit --allow-empty -m "Redeploy with env vars"
git push origin main
```

