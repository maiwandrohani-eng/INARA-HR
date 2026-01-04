# Fix: Railway Detecting Node.js Instead of Python

## Problem
Railway is detecting Node.js and trying to build the frontend instead of the Python backend.

**Error**: `sh: 1: next: not found` - Railway is trying to build Next.js!

## Solution

### Step 1: Set Root Directory Correctly

1. Go to Railway → **INARA-HR** → **Settings**
2. Scroll to **Source** section
3. **Root Directory**: Must be set to `apps/api`
4. Save changes

### Step 2: Force Python Detection

Add a `runtime.txt` file to help Railway detect Python:

The file `apps/api/runtime.txt` has been created with:
```
python-3.11
```

### Step 3: Verify Build Configuration

Railway → **INARA-HR** → **Settings** → **Build & Deploy**:

- **Build Command**: Should be `pip install -r requirements.txt` (or auto-detect)
- **Start Command**: Should be `uvicorn main:app --host 0.0.0.0 --port $PORT`

These should be set by `railway.json`, but verify they're correct.

### Step 4: Redeploy

After fixing root directory:
1. Railway → **INARA-HR** → **Deployments**
2. Click **Deploy** or trigger a new deployment
3. Railway should now detect Python and install from `requirements.txt`

### Step 5: Verify Detection

In the build logs, you should see:
- ✅ Python detected (not Node.js)
- ✅ `pip install -r requirements.txt`
- ✅ `uvicorn main:app --host 0.0.0.0 --port $PORT`

**NOT**:
- ❌ Node.js detected
- ❌ `npm install`
- ❌ `next build`

## If Still Not Working

### Option A: Manual Buildpack Selection
1. Railway → **INARA-HR** → **Settings**
2. Look for **Buildpack** or **Builder** option
3. Select **Python** (if available)

### Option B: Check for Conflicting Files
Railway might be detecting Node.js because:
- Root `package.json` exists
- Frontend `package.json` in `apps/frontend/`

The `runtime.txt` and correct root directory should override this.

### Option C: Use Nixpacks Configuration
Create `apps/api/nixpacks.toml`:
```toml
[phases.setup]
nixPkgs = ['python311', 'pip']

[phases.install]
cmds = ['pip install -r requirements.txt']

[start]
cmd = 'uvicorn main:app --host 0.0.0.0 --port $PORT'
```

## Most Important Fix

**Set Root Directory to `apps/api`** - This is the #1 fix!

The error shows Railway is looking at the root directory or frontend, not the backend.

