# Vercel Build Fix

## Issue
`sh: line 1: next: command not found` - This happens because Vercel isn't installing dependencies in the correct directory.

## Solution

### Option 1: Configure Root Directory in Vercel Dashboard (Recommended)

1. Go to your Vercel project settings
2. Navigate to **Settings → General → Root Directory**
3. Set Root Directory to: `apps/frontend`
4. Save
5. Redeploy

This tells Vercel that the Next.js app is in the `apps/frontend` directory.

### Option 2: Update vercel.json (Already done)

I've updated the `vercel.json` file to specify the root directory. If Option 1 doesn't work, make sure Vercel is reading from the root `vercel.json` file.

### Option 3: Manual Build Settings in Vercel

If the above doesn't work, manually set these in **Vercel Dashboard → Settings → Build & Development Settings**:

- **Framework Preset**: Next.js
- **Root Directory**: `apps/frontend`
- **Build Command**: `npm run build` (or leave empty for auto-detection)
- **Output Directory**: `.next` (or leave empty for auto-detection)
- **Install Command**: `npm install` (or leave empty for auto-detection)

### Verify Package.json Location

Make sure `apps/frontend/package.json` exists and has the build script:
```json
{
  "scripts": {
    "build": "next build"
  }
}
```

### After Fix

1. Delete the failed deployment (if any)
2. Trigger a new deployment
3. Check build logs to confirm dependencies are installing

The build should now succeed!

