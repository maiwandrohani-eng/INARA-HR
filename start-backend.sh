#!/bin/bash

# INARA HR - Start Backend API Only
# This script starts just the backend API server

echo "🚀 Starting INARA HR Backend API..."
echo ""

# Navigate to API directory
cd "$(dirname "$0")/apps/api"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if [ ! -f "venv/bin/uvicorn" ]; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Set PYTHONPATH
export PYTHONPATH="$PWD:$PYTHONPATH"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  WARNING: .env file not found!"
    echo "   Creating default .env file..."
    cat > .env << EOF
DATABASE_URL=postgresql://inara_user:inara_password@localhost:5432/inara_hris
DATABASE_ASYNC_URL=postgresql+asyncpg://inara_user:inara_password@localhost:5432/inara_hris
REDIS_URL=redis://localhost:6379
SECRET_KEY=dev-secret-key-change-in-production
ENVIRONMENT=development
DEBUG=True
S3_ENDPOINT_URL=
S3_ACCESS_KEY_ID=
S3_SECRET_ACCESS_KEY=
S3_BUCKET_NAME=
SMTP_HOST=localhost
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=noreply@inara.org
EOF
    echo "   ✅ Created .env file. Please update with your database credentials if needed."
fi

echo ""
echo "✅ Starting API server..."
echo "   Backend will be available at: http://localhost:8000"
echo "   API Docs: http://localhost:8000/api/v1/docs"
echo "   Health Check: http://localhost:8000/health"
echo ""
echo "⚠️  Keep this terminal window open. Press Ctrl+C to stop the server."
echo ""

# Start the server
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

