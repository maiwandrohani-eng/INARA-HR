# How to Get Supabase Database Connection String

## What You Have vs What You Need

### ❌ What You Have (API Keys)
- `anon public` - Supabase REST API key
- `service_role secret` - Supabase Service Role key

**These are for Supabase's REST API, not for direct database connections!**

### ✅ What You Need (Database Connection Strings)
- `DATABASE_URL` - PostgreSQL connection string
- `DATABASE_ASYNC_URL` - Same, but with `postgresql+asyncpg://` prefix

**These are for your FastAPI backend to connect to the database!**

## Step-by-Step: Get Database Connection String

### Step 1: Go to Supabase Dashboard
1. Open: https://supabase.com/dashboard
2. Select your project (the one with ref: `qeqwowallrenlqlbvwweb`)

### Step 2: Navigate to Database Settings
1. Click **Settings** (gear icon) in left sidebar
2. Click **Database** in the settings menu

### Step 3: Find Connection String
1. Scroll down to **Connection String** section
2. You'll see different connection options:
   - Direct connection
   - Connection pooling (Transaction mode)
   - Connection pooling (Session mode)

### Step 4: Copy Connection Pooling URL (Recommended)
1. Select **Connection pooling** → **Transaction mode** (recommended for serverless)
2. Select **URI** format
3. Copy the connection string - it looks like:
   ```
   postgresql://postgres.qeqwowallrenlqlbvwweb:[YOUR-PASSWORD]@aws-0-[region].pooler.supabase.com:6543/postgres?pgbouncer=true
   ```

### Step 5: Replace `[YOUR-PASSWORD]`
The connection string will have `[YOUR-PASSWORD]` placeholder. Replace it with:
- Your database password (if you set one)
- Or check: **Settings** → **Database** → **Database password** section

### Step 6: Create Both URLs

**For `DATABASE_URL`:**
```
postgresql://postgres.qeqwowallrenlqlbvwweb:YOUR_PASSWORD@aws-0-[region].pooler.supabase.com:6543/postgres?pgbouncer=true
```

**For `DATABASE_ASYNC_URL` (change `postgresql://` to `postgresql+asyncpg://`):**
```
postgresql+asyncpg://postgres.qeqwowallrenlqlbvwweb:YOUR_PASSWORD@aws-0-[region].pooler.supabase.com:6543/postgres?pgbouncer=true
```

## Alternative: Find Database Password

If you don't know your database password:

1. Go to **Settings** → **Database**
2. Scroll to **Database password** section
3. If you forgot it, you may need to:
   - Check your initial setup notes, OR
   - Reset it (this will require updating all connection strings)

## Quick Visual Guide

In Supabase Dashboard:
```
Settings
  └─ Database
      └─ Connection String
          ├─ Direct connection
          └─ Connection pooling ← USE THIS!
              └─ Transaction mode
                  └─ URI ← Copy this!
```

## Example Format

Your connection string should look like:
```
postgresql://postgres.qeqwowallrenlqlbvwweb:abcdefghijklmnop@aws-0-us-west-1.pooler.supabase.com:6543/postgres?pgbouncer=true
```

## After You Get It

1. Copy the connection string
2. Use it as `DATABASE_URL` in Railway
3. Change `postgresql://` to `postgresql+asyncpg://` for `DATABASE_ASYNC_URL`
4. Add both to Railway → Variables
5. Deploy!

## Need Help Finding It?

If you can't find it:
1. Go to Supabase Dashboard
2. Settings → Database
3. Look for "Connection string" or "Connection pooling"
4. It might be under "Connection Info" section

The connection string is different from API keys - you need the PostgreSQL connection URL!

