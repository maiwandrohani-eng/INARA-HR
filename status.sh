#!/bin/bash

echo "🚀 INARA HRIS - Quick Start Guide"
echo "=================================="
echo ""
echo "📊 Current Status:"
echo ""

# Check if backend is running
if lsof -i :8000 >/dev/null 2>&1; then
    echo "✅ Backend API: http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
else
    echo "❌ Backend API: Not running"
    echo "   Start with: cd apps/api && PYTHONPATH=. python3 -m uvicorn main:app --reload &"
fi

echo ""

# Check if frontend is running
if lsof -i :3000 >/dev/null 2>&1; then
    echo "✅ Frontend: http://localhost:3000"
else
    echo "❌ Frontend: Not running"
    echo "   Start with: cd apps/frontend && npm run dev &"
fi

echo ""
echo "⚠️  DATABASE NOT CONFIGURED"
echo "=================================="
echo ""
echo "The login credentials won't work until you set up PostgreSQL."
echo ""
echo "📝 To enable login functionality:"
echo ""
echo "Option 1 - Use Docker (Recommended):"
echo "  1. Install Docker Desktop from https://www.docker.com/products/docker-desktop"
echo "  2. Run: docker-compose up -d postgres redis"
echo "  3. Run migrations: cd apps/api && PYTHONPATH=. alembic upgrade head"
echo "  4. Seed data: cd apps/api && PYTHONPATH=. python3 scripts/seed_data.py"
echo ""
echo "Option 2 - Install PostgreSQL locally:"
echo "  1. Install PostgreSQL: brew install postgresql@15"
echo "  2. Start service: brew services start postgresql@15"
echo "  3. Create database: createdb inara_hris"
echo "  4. Update apps/api/.env with your database credentials"
echo "  5. Run migrations: cd apps/api && PYTHONPATH=. alembic upgrade head"
echo "  6. Seed data: cd apps/api && PYTHONPATH=. python3 scripts/seed_data.py"
echo ""
echo "🎯 After setup, you can login with:"
echo "   Admin: admin@inara.org / Admin@123"
echo "   HR: hr@inara.org / HR@123"
echo ""
echo "📚 Documentation:"
echo "   - API: apps/api/README.md"
echo "   - Frontend: apps/frontend/README.md"
echo "   - Deployment: DEPLOYMENT.md"
echo ""
