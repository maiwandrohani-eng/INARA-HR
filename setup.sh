#!/bin/bash

# INARA HRIS - Quick Start Setup Script
# This script sets up the development environment

echo "🚀 INARA HRIS - Quick Start Setup"
echo "=================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check for .env file
if [ ! -f "apps/api/.env" ]; then
    echo "📝 Creating .env file for backend..."
    cp apps/api/.env.example apps/api/.env
    echo "⚠️  Please edit apps/api/.env with your configuration"
fi

if [ ! -f "apps/frontend/.env.local" ]; then
    echo "📝 Creating .env.local file for frontend..."
    cp apps/frontend/.env.local.example apps/frontend/.env.local
    echo "⚠️  Please edit apps/frontend/.env.local with your configuration"
fi

echo ""
echo "🐳 Starting Docker services..."
docker-compose up -d

echo ""
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 10

echo ""
echo "🗄️  Running database migrations..."
docker-compose exec -T api alembic upgrade head

echo ""
echo "✅ Setup complete!"
echo ""
echo "📍 Access your application:"
echo "   Frontend: http://localhost:3000"
echo "   API Docs: http://localhost:8000/docs"
echo "   API Health: http://localhost:8000/health"
echo ""
echo "📝 Next steps:"
echo "   1. Review and update .env files"
echo "   2. Create admin user: docker-compose exec api python scripts/seed_data.py"
echo "   3. Start coding!"
echo ""
echo "📚 Documentation:"
echo "   - Main README: README.md"
echo "   - API Docs: apps/api/README.md"
echo "   - Frontend Docs: apps/frontend/README.md"
echo "   - Deployment Guide: DEPLOYMENT.md"
echo ""
echo "🔧 Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart service: docker-compose restart <service>"
echo ""
