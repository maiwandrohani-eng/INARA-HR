#!/bin/bash

# Navigate to API directory
cd "$(dirname "$0")"

# Set PYTHONPATH so Python can find modules
export PYTHONPATH="$PWD"

# Use PORT from environment, default to 8000
PORT=${PORT:-8000}

echo "🚀 Starting INARA HR API..."
echo "   PYTHONPATH: $PYTHONPATH"
echo "   Server will be available at: http://0.0.0.0:$PORT"
echo "   API Docs: http://0.0.0.0:$PORT/api/v1/docs"
echo ""

# Start the server (no --reload in production)
python3 -m uvicorn main:app --host 0.0.0.0 --port $PORT
