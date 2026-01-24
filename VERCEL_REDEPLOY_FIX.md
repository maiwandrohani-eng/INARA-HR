# Vercel Redeploy - How to Trigger New Deployment

## Problem
"This deployment can not be redeploy. Please try again from a fresh commit."

This happens when trying to redeploy an old deployment. You need to trigger a **new deployment** instead.

## Solutions

### Option 1: Push a New Commit (Recommended)

This will automatically trigger a new deployment:

```bash
# Make a small change (or just touch a file)
cd /Users/maiwand/INARA-HR
echo "# Deployment update" >> apps/frontend/.vercel-deploy
git add apps/frontend/.vercel-deploy
git commit -m "Trigger Vercel deployment"
git push origin main
```

Vercel will automatically detect the new commit and deploy!

### Option 2: Trigger Deployment from Vercel Dashboard

1. Go to **Vercel Dashboard** → Your Project
2. Click **Deployments** tab
3. Find the **latest deployment** (should be from your recent commits)
4. If you see a "Redeploy" button on the latest one, click it
5. **OR** click the **"..."** menu → **"Redeploy"**

### Option 3: Set Environment Variable (Auto-Redeploys)

When you add/modify environment variables:
1. Vercel Dashboard → Settings → Environment Variables
2. Add `NEXT_PUBLIC_API_URL` (if not already set)
3. Click **Save**
4. Vercel will **automatically trigger a new deployment**!

This is the easiest way - just set the env var and it redeploys automatically.

### Option 4: Manual Deployment Trigger

1. Go to Vercel Dashboard → Your Project
2. Click **Deployments** tab
3. Look for **"Redeploy"** button at the top
4. Or click **"Create Deployment"** to manually trigger

## Recommended: Just Set the Environment Variable

**Easiest solution:**
1. Vercel → Settings → Environment Variables
2. Add: `NEXT_PUBLIC_API_URL=https://inara-hr-production.up.railway.app/api/v1`
3. Save (this triggers auto-redeploy!)
4. Wait for deployment to complete

## Quick Fix: Push Empty Commit

If you just need to trigger deployment:
```bash
cd /Users/maiwand/INARA-HR
git commit --allow-empty -m "Trigger Vercel deployment for env var update"
git push origin main
```

This creates an empty commit that triggers Vercel to deploy.

## Check Deployment Status

After triggering:
1. Vercel → Deployments tab
2. You should see a new deployment in progress
3. Wait for it to complete
4. Test your app!

