# INARA HRIS Login Credentials

## 🔐 Default User Accounts

### Admin Account
- **Email:** admin@inara.org
- **Password:** Admin@123
- **Role:** Super Administrator
- **Permissions:** Full system access

### HR Account
- **Email:** hr@inara.org
- **Password:** HR@12345
- **Role:** HR Administrator
- **Permissions:** HR administration access

## 🌐 Access URLs

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

## ⚠️ Important Security Notes

1. **Change These Passwords Immediately** in production
2. These are development/demo credentials only
3. Never commit credentials to version control
4. Use environment variables for production secrets
5. Enable two-factor authentication in production

## 🗄️ Database Info

- **Database:** inara_hris
- **User:** inara_user
- **Password:** inara_password
- **Host:** localhost
- **Port:** 5432

## 🚀 Quick Start

1. Make sure PostgreSQL is running: `brew services list | grep postgresql`
2. Start the backend: `cd apps/api && ./start.sh`
3. Start the frontend: `cd apps/frontend && npm run dev`
4. Navigate to http://localhost:3000
5. Login with one of the accounts above

## 📝 Notes

- All users have been successfully created in the database
- Both backend (port 8000) and frontend (port 3000) are running
- Database tables have been created and seeded with initial data
