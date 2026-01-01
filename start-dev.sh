#!/bin/bash

# INARA HR - Development Startup Script
# This script starts all services for local development

echo "🚀 Starting INARA HR Development Environment..."
echo ""

# Start Docker containers (database, redis, api) - NOT frontend
echo "📦 Starting Docker containers (backend only)..."
docker-compose up -d postgres redis api

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 3

# Check if services are running
echo ""
echo "✅ Services Status:"
docker-compose ps

echo ""
echo "🌐 Starting Frontend..."
echo "   Frontend will be available at: http://localhost:3002"
echo ""
echo "⚠️  Keep this terminal window open. Press Ctrl+C to stop the frontend."
echo ""

# Start frontend in foreground
cd apps/frontend && npm run dev
