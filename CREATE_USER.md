# Create Maiwand User

## Automatic Creation
I've updated the startup code to **automatically create** your user account (`maiwand@inara.org`) when the database tables are first created.

## What Happens
On first startup after tables are created:
1. Tables are created automatically
2. System checks if `maiwand@inara.org` exists
3. If not, creates the user with super_admin role
4. You'll see in logs: `✅ Initial user (maiwand@inara.org) created successfully!`

## Manual Creation (Backup)
If automatic creation doesn't work, you can run manually:

### On Railway:
```bash
railway run python scripts/create_maiwand_user.py
```

### Credentials:
- **Email**: maiwand@inara.org
- **Password**: Come*1234
- **Role**: Super Administrator (full access)

## After User is Created

1. **Railway redeploys** with the new code
2. **Tables are created** automatically
3. **Your user is created** automatically
4. **Login from Vercel** with:
   - Email: `maiwand@inara.org`
   - Password: `Come*1234`

## Expected Logs

```
✅ Database connection verified
⚠️  Database tables not found. Creating tables...
✅ Database tables created successfully!
Creating initial user: maiwand@inara.org...
✅ Initial user (maiwand@inara.org) created successfully!
✅ All systems initialized successfully
```

