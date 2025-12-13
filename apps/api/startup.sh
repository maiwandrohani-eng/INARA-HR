#!/bin/bash
set -e

echo "🚀 Starting INARA HR API..."

echo "📦 Running database migrations..."
alembic upgrade head

echo "✅ Migrations complete!"

echo "🌐 Starting API server..."
uvicorn main:app --host 0.0.0.0 --port $PORT
