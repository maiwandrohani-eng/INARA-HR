#!/bin/bash

# Navigate to API directory
cd "$(dirname "$0")"

# Set PYTHONPATH so Python can find modules
export PYTHONPATH="$PWD"

echo "🚀 Starting INARA HR API..."
echo "   PYTHONPATH: $PYTHONPATH"
echo "   Server will be available at: http://localhost:8000"
echo "   API Docs: http://localhost:8000/api/v1/docs"
echo ""

# Start the server
python3 -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
