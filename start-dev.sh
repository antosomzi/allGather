#!/bin/bash

echo "🚀 Starting DriverScore Development Stack (without Nginx)..."

# Start with development frontend
docker-compose -f docker-compose.dev.yml up --build

echo "✅ Development stack started!"
echo "🌐 Frontend (Vite): http://localhost:5173"  
echo "📊 Backend API: http://localhost:8000"
echo "📖 API docs: http://localhost:8000/docs"
echo "🗄️ Database: localhost:5432"