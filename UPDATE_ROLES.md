# Update Maiwand User Roles

## Issue
Your user (`maiwand@inara.org`) was created with only `super_admin` role, but the frontend needs `admin` and `ceo` roles to show admin/CEO dashboard and menu items.

## Solution
I've updated the code to automatically add `admin` and `ceo` roles. You have two options:

### Option 1: Wait for Auto-Update (After Railway Redeploy)
The updated code will automatically add missing roles on next startup. After Railway redeploys:
1. Railway will restart
2. Code will detect existing user
3. Will add `admin` and `ceo` roles automatically
4. Check logs: `✅ Added admin/ceo roles to existing user: maiwand@inara.org`

### Option 2: Run Manual Update Script (Faster)
If you want to update immediately without waiting for redeploy:

```bash
# Using Railway CLI
railway run python scripts/update_maiwand_roles.py
```

## After Roles Are Updated

1. **Logout** from the frontend
2. **Login again** with `maiwand@inara.org` / `Come*1234`
3. You should now see:
   - Admin Settings menu item
   - All HR management pages
   - CEO-level access

## Roles You'll Have

- `super_admin` - System-level super admin
- `admin` - Administrator (frontend recognizes this)
- `ceo` - CEO (frontend recognizes this)

## Verify It Worked

After updating roles and logging in again, you should see:
- ✅ "Admin Settings" link in sidebar
- ✅ Full access to all HR management pages
- ✅ All menu items visible (not just employee view)

