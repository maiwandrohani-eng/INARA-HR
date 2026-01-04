# Fix Admin Access - Immediate Steps

## The Problem
Your user (`maiwand@inara.org`) needs `admin` and `ceo` roles in the database, and you need to refresh your session.

## Quick Fix Steps

### Step 1: Update Roles in Database
Run this command on Railway to add the roles:

```bash
railway run python scripts/update_maiwand_roles.py
```

**OR** if you don't have Railway CLI, the roles will be added automatically on next Railway restart (after code redeploy).

### Step 2: Refresh Your Session
After roles are updated, you MUST:

1. **Logout** from the frontend (click logout button)
2. **Clear browser cache** (or do hard refresh: Cmd+Shift+R / Ctrl+Shift+R)
3. **Login again** with `maiwand@inara.org` / `Come*1234`

The frontend caches your user data, so you need to logout/login to get the updated roles.

### Step 3: Verify It Worked
After logging in again, you should see:
- ✅ "Admin Settings" menu item in sidebar
- ✅ All HR management pages visible
- ✅ Full admin/CEO dashboard access

## Why This Happens
- The frontend gets user roles from `/auth/me` endpoint
- Your current session has the old roles (only `super_admin`)
- Logout/login refreshes the session and gets new roles from database

## If Still Not Working
1. Check Railway logs to confirm roles were added
2. Open browser console (F12) and check what `/auth/me` returns
3. Verify roles in database directly

