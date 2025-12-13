#!/bin/bash

# INARA HR - Native Development Startup Script (No Docker)
# This script starts all services natively for local development

echo "🚀 Starting INARA HR Development Environment (Native Mode)..."
echo ""

# Check if PostgreSQL is running
echo "📊 Checking PostgreSQL..."
if lsof -i:5432 > /dev/null; then
    echo "   ✅ PostgreSQL is running"
else
    echo "   ❌ PostgreSQL is NOT running!"
    echo "   Start it with: brew services start postgresql@15"
    exit 1
fi

# Check if Redis is running (optional but recommended)
echo "📦 Checking Redis..."
if lsof -i:6379 > /dev/null; then
    echo "   ✅ Redis is running"
else
    echo "   ⚠️  Redis is NOT running (optional)"
    echo "   Start it with: brew services start redis"
fi

echo ""
echo "🔧 Starting Backend API..."

# Kill any existing process on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null

# Start backend in background
cd apps/api
export PYTHONPATH=$PWD:$PYTHONPATH
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > /tmp/inara-api.log 2>&1 &
API_PID=$!
echo "   Backend PID: $API_PID"
cd ../..

# Wait for backend to start
echo "   ⏳ Waiting for backend to start..."
sleep 3

# Check if backend is responding
if curl -s http://localhost:8000/health > /dev/null; then
    echo "   ✅ Backend API is running at http://localhost:8000"
    echo "   📖 API Docs: http://localhost:8000/api/v1/docs"
else
    echo "   ❌ Backend failed to start! Check logs: tail -f /tmp/inara-api.log"
    exit 1
fi

echo ""
echo "🌐 Starting Frontend..."
echo "   Frontend will be available at: http://localhost:3000"
echo ""
echo "✅ All services started successfully!"
echo ""
echo "📋 Service URLs:"
echo "   • Frontend: http://localhost:3000"
echo "   • Backend API: http://localhost:8000"
echo "   • API Docs: http://localhost:8000/api/v1/docs"
echo "   • Database: localhost:5432 (inara_hris)"
echo ""
echo "🔐 Login Credentials:"
echo "   • Email: admin@inara.org"
echo "   • Password: Admin@123"
echo ""
echo "⚠️  Keep this terminal window open. Press Ctrl+C to stop all services."
echo ""

# Start frontend in foreground
cd apps/frontend && npm run dev
