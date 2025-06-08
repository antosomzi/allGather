#!/bin/bash

echo "🚀 Starting Full DriverScore Stack..."

# Start all services
docker-compose up --build

echo "✅ Full stack started!"
echo "🌐 Frontend: http://localhost:3000"
echo "📊 Backend API: http://localhost:8000"
echo "📖 API docs: http://localhost:8000/docs"
echo "🗄️ Database: localhost:5432"