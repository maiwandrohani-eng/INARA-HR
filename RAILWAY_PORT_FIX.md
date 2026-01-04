# Fix: Railway $PORT Environment Variable Not Expanding

## Problem
Railway is passing `$PORT` literally instead of expanding it to the actual port number.

**Error**: `Error: Invalid value for '--port': '$PORT' is not a valid integer.`

## Solution

The start command needs to run in a shell that expands the `$PORT` variable.

### Option 1: Update railway.json (Already Fixed)
Changed:
```json
"startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT"
```

To:
```json
"startCommand": "sh -c 'uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}'"
```

This runs the command in a shell that expands `${PORT:-8000}` (uses PORT env var, defaults to 8000).

### Option 2: Set in Railway Settings
If the above doesn't work, manually set in Railway:

1. Railway → **INARA-HR** → **Settings**
2. Find **Start Command** or **Deploy** section
3. Set to: `sh -c 'uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}'`
4. Save and redeploy

### Option 3: Alternative (Python Script)
Create a start script if needed, but the shell expansion should work.

## After Fix

1. Commit and push the changes (already done)
2. Railway → **INARA-HR** → **Deployments**
3. Redeploy (or it should auto-redeploy)
4. Check logs - should see:
   ```
   INFO:     Uvicorn running on http://0.0.0.0:XXXX (Press CTRL+C to quit)
   ```

Instead of:
   ```
   Error: Invalid value for '--port': '$PORT' is not a valid integer.
   ```

## Test

After redeploy, check:
- Service status: Should be "Online"
- Logs: Should show uvicorn running on a port
- Health endpoint: `https://your-domain.up.railway.app/health`
