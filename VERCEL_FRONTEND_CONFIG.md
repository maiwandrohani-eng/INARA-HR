# Vercel Frontend Configuration - Final Step

## Your Backend API URL
```
https://inara-hr-production.up.railway.app
```

## Step 1: Configure Vercel Environment Variable

1. Go to **Vercel Dashboard**: https://vercel.com/dashboard
2. Click on your **INARA-HR** project
3. Go to **Settings** → **Environment Variables**
4. Click **Add New**
5. Set:
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://inara-hr-production.up.railway.app/api/v1`
   - **IMPORTANT**: Include `/api/v1` at the end!
   - **Environment**: Select **Production** (and **Preview** if you want)
6. Click **Save**

## Step 2: Redeploy Frontend

After saving the environment variable:
1. Go to **Deployments** tab
2. Click the **3 dots** (⋯) on the latest deployment
3. Click **Redeploy**
4. Wait for deployment to complete

Or Vercel might auto-redeploy when you save the env var.

## Step 3: Test Connection

1. Open your Vercel app URL
2. Open browser **Developer Console** (F12)
3. Look for: `🌐 API Client initialized with baseURL: https://inara-hr-production.up.railway.app/api/v1`
4. Try logging in

## Step 4: Verify Backend Health (Optional)

Test your backend directly:
```
https://inara-hr-production.up.railway.app/health
```

Should return: `{"status":"healthy"}`

## Troubleshooting

### Still getting "Cannot connect to server"?
- ✅ Verify `NEXT_PUBLIC_API_URL` is set in Vercel
- ✅ Check it includes `/api/v1` at the end
- ✅ Verify backend is running (check Railway logs)
- ✅ Test backend health endpoint directly
- ✅ Check browser console for actual error messages

### CORS errors?
- ✅ In Railway → INARA-HR → Variables, set:
  ```
  CORS_ORIGINS=["https://your-vercel-app.vercel.app"]
  ```
- ✅ Replace `your-vercel-app` with your actual Vercel domain
- ✅ Redeploy Railway service after changing CORS

### Backend not responding?
- ✅ Check Railway → INARA-HR → Logs for errors
- ✅ Verify all environment variables are set (DATABASE_URL, SECRET_KEY, etc.)
- ✅ Check Railway service is running (not crashed)

## Quick Checklist

- [ ] `NEXT_PUBLIC_API_URL` set in Vercel: `https://inara-hr-production.up.railway.app/api/v1`
- [ ] Frontend redeployed after setting env var
- [ ] Backend health endpoint works: `/health`
- [ ] CORS configured in Railway to allow Vercel domain
- [ ] Test login from frontend

