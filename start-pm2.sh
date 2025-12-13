#!/bin/bash

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    echo "   INARA-HR requires Docker to run its backend services."
    exit 1
fi

# Ensure Docker services are running
cd /Users/maiwand/INARA-HR
docker-compose up -d postgres redis api 2>/dev/null || true

# Wait for API to be ready
echo "Waiting for API to be ready..."
for i in {1..30}; do
  if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
    echo "API is ready!"
    break
  fi
  if [ $i -eq 30 ]; then
    echo "❌ API failed to start after 30 seconds"
    exit 1
  fi
  sleep 1
done

# Start frontend on port 5177
cd /Users/maiwand/INARA-HR/apps/frontend
PORT=5177 npm run dev
