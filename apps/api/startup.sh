#!/bin/bash
set -e

echo "🚀 Starting INARA HR API..."

echo "📦 Creating database tables..."
python -c "
from core.database import engine
from core.models import Base
print('Creating all tables...')
Base.metadata.create_all(bind=engine)
print('✅ Tables created!')
"

echo "✅ Database setup complete!"

echo "🌐 Starting API server..."
uvicorn main:app --host 0.0.0.0 --port $PORT
