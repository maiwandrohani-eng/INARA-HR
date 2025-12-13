# ⚠️ LOGIN NOT WORKING - DATABASE REQUIRED

## Why Login Fails

The login credentials **cannot work** without a PostgreSQL database because:
1. User accounts are stored in the database
2. The backend needs to query the database to verify credentials
3. No database = no users = login fails

## Current Status

✅ **Working:**
- Frontend UI (http://localhost:3000) - fully styled
- Backend API (http://localhost:8000) - running
- All pages, navigation, and components

❌ **Not Working:**
- Login functionality - **requires database**
- Any feature that saves/reads data

## Quick Setup (15 minutes)

### Option 1: Docker (Recommended & Easiest)

```bash
# 1. Install Docker Desktop from https://www.docker.com/
# 2. Start PostgreSQL and Redis
docker-compose up -d postgres redis

# 3. Wait 10 seconds for database to start
sleep 10

# 4. Run database migrations
cd apps/api
PYTHONPATH=. alembic upgrade head

# 5. Create admin users
PYTHONPATH=. python3 scripts/seed_data.py

# 6. Restart backend
pkill -f uvicorn
PYTHONPATH=. python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
```

### Option 2: Local PostgreSQL

```bash
# 1. Install PostgreSQL
brew install postgresql@15
brew services start postgresql@15

# 2. Create database and user
psql postgres << EOF
CREATE USER inara_user WITH PASSWORD 'inara_password';
CREATE DATABASE inara_hris OWNER inara_user;
GRANT ALL PRIVILEGES ON DATABASE inara_hris TO inara_user;
EOF

# 3. Run migrations
cd apps/api
PYTHONPATH=. alembic upgrade head

# 4. Create admin users
PYTHONPATH=. python3 scripts/seed_data.py

# 5. Restart backend
pkill -f uvicorn
PYTHONPATH=. python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
```

## After Setup

Once the database is running, you can login with:

- **Admin**: admin@inara.org / Admin@123
- **HR Manager**: hr@inara.org / HR@123

## What You Can Do Now (Without Database)

You can explore the UI:
- View the landing page: http://localhost:3000
- See the login form: http://localhost:3000/login
- Check the dashboard layout: http://localhost:3000/dashboard
- Review the API docs: http://localhost:8000/docs

But remember: **Nothing will save or load data until you setup PostgreSQL!**

## Need Help?

Run this to check status:
```bash
./status.sh
```

Check if database is running:
```bash
docker ps  # if using Docker
# OR
brew services list | grep postgresql  # if using local install
```
