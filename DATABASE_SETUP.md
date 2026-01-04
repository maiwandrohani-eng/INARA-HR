# Database Setup for Railway Deployment

## Problem
Your Railway deployment logs show:
```
relation "users" does not exist
```

This means the database tables haven't been created yet.

## Solution
I've updated the code to **automatically create tables** on startup if they don't exist.

## What I Changed

1. **Updated `apps/api/main.py`**: Added automatic table creation in the startup lifespan function
2. **Created `apps/api/scripts/init_db.py`**: Manual initialization script (backup option)

## After Next Deployment

Once Railway redeploys with the new code:
1. Tables will be created automatically on first startup
2. The app will log: `✅ Database tables created successfully!`
3. Login should work (after creating a user - see below)

## Creating Your First User

After tables are created, you need to create an admin user. You have two options:

### Option 1: Use Railway CLI (Recommended)
```bash
# Install Railway CLI
npm i -g @railway/cli

# Login to Railway
railway login

# Connect to your project
railway link

# Run the user creation script
railway run python scripts/create_admin_user.py
```

### Option 2: SSH into Railway Container
1. Go to Railway Dashboard → Your Service → Settings
2. Enable "Allow SSH"
3. Connect via Railway CLI or SSH
4. Run: `python scripts/create_admin_user.py`

### Option 3: Create via API Endpoint
If you have a registration endpoint, you can create users via the API.

## Manual Table Creation (If Auto-Create Fails)

If automatic creation doesn't work, you can run manually:

```bash
# On Railway
railway run python scripts/init_db.py
```

## Expected Logs After Fix

```
✅ Database connection verified
✅ Database tables created successfully!
✅ All systems initialized successfully
```

## Next Steps

1. **Wait for Railway to redeploy** (triggered by the code push)
2. **Check logs** - should see table creation messages
3. **Create first admin user** (see above)
4. **Test login** from Vercel frontend

