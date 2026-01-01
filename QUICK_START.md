# Quick Start Guide - INARA HRIS

## 🚀 Starting the Application

### Option 1: Docker Compose (Easiest - Recommended)

```bash
# Start all services (database, redis, backend, frontend)
docker-compose up
```

This will start:
- ✅ PostgreSQL database (port 5432)
- ✅ Redis cache (port 6379)
- ✅ Backend API (port 8000)
- ✅ Frontend (port 3000)

**Access URLs:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/v1/docs

**To stop:**
```bash
docker-compose down
```

---

### Option 2: Native Development (Without Docker)

**Step 1: Start Database & Redis**
```bash
# macOS with Homebrew:
brew services start postgresql@15
brew services start redis

# Or use Docker for just database/redis:
docker-compose up -d postgres redis
```

**Step 2: Setup Backend**

Terminal 1:
```bash
cd apps/api

# Create virtual environment (if not exists)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (create .env file)
# DATABASE_URL=postgresql://inara_user:inara_password@localhost:5432/inara_hris
# DATABASE_ASYNC_URL=postgresql+asyncpg://inara_user:inara_password@localhost:5432/inara_hris
# REDIS_URL=redis://localhost:6379
# SECRET_KEY=your-secret-key-here

# Run migrations (if needed)
alembic upgrade head

# Start backend
export PYTHONPATH=$PWD:$PYTHONPATH
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Step 3: Setup Frontend**

Terminal 2:
```bash
cd apps/frontend

# Install dependencies (if not already)
npm install

# Create .env.local file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1" > .env.local

# Start frontend
npm run dev
```

---

### Option 3: Using Start Scripts

**Native Mode:**
```bash
./start-native.sh
```

**Docker Mode (backend in Docker, frontend native):**
```bash
./start-dev.sh
```

---

## 🔍 Troubleshooting

### Login Network Error

If you get a "network error" or "timeout" when logging in:

1. **Check if backend is running:**
   ```bash
   curl http://localhost:8000/health
   ```
   Should return: `{"success": true, "status": "healthy"}`

2. **Check backend logs:**
   ```bash
   # If using Docker:
   docker-compose logs api
   
   # If running natively:
   # Check terminal where backend is running
   ```

3. **Verify API URL in frontend:**
   - Frontend should use: `http://localhost:8000/api/v1`
   - Check browser console for API URL logs

4. **Check CORS settings:**
   - Backend allows: `http://localhost:3000`
   - Frontend runs on: `http://localhost:3000`

5. **Check database connection:**
   ```bash
   # Test PostgreSQL connection
   psql -h localhost -U inara_user -d inara_hris
   ```

6. **Check ports are not in use:**
   ```bash
   # macOS/Linux:
   lsof -i:8000  # Backend
   lsof -i:3000  # Frontend
   ```

### Common Issues

**Issue: "Cannot connect to backend"**
- ✅ Make sure backend is running on port 8000
- ✅ Check `NEXT_PUBLIC_API_URL` in frontend `.env.local`
- ✅ Verify no firewall blocking port 8000

**Issue: "Database connection failed"**
- ✅ Ensure PostgreSQL is running
- ✅ Check database credentials in `.env`
- ✅ Verify database `inara_hris` exists

**Issue: "CORS error"**
- ✅ Backend CORS allows `http://localhost:3000`
- ✅ Frontend running on port 3000 (not 3002)

---

## 📋 Environment Variables

### Backend (.env in `apps/api/`)
```env
DATABASE_URL=postgresql://inara_user:inara_password@localhost:5432/inara_hris
DATABASE_ASYNC_URL=postgresql+asyncpg://inara_user:inara_password@localhost:5432/inara_hris
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key-change-in-production
ENVIRONMENT=development
DEBUG=True
```

### Frontend (.env.local in `apps/frontend/`)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

---

## 🔐 Default Login Credentials

After setting up the database, create a user:

```bash
cd apps/api
python create_admin.py
```

Or use the seed script:
```bash
python seed_roles_permissions.py
python seed_employees.py
```

---

## ✅ Verification Steps

1. **Backend Health Check:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **API Docs:**
   - Open: http://localhost:8000/api/v1/docs

3. **Frontend:**
   - Open: http://localhost:3000
   - Should show login page

4. **Test Login:**
   - Use credentials created via seed scripts
   - Check browser console for any errors

---

## 🆘 Still Having Issues?

1. Check backend logs for errors
2. Check frontend browser console (F12)
3. Verify all services are running
4. Check network connectivity between frontend and backend
5. Ensure ports 3000 and 8000 are not blocked

